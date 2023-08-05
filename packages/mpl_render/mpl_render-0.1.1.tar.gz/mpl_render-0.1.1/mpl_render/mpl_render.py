import numpy as np
from cached_property import cached_property
from threading import Thread, Lock
from time import sleep

# this is mostly based on the `viewlims.py` example on the matplotlib website

class RenderingImShow(object):
    size = (500, 300)
    im = None
    _update_id = 0

    # The "update delay" is needed because we typically get sent two
    # events, 'xlim_changed' and 'ylim_changed', in close succession. So
    # we wait a couple miliseconds until the last received one before
    # actually drawing anything. This delay is implemented by having
    # another thread sleep, then do the drawing.
    #
    # Drawing in a thread can lead to issues on non-threadsafe
    # backends, and it is unclear on which backends this is safe.
    #
    # https://stackoverflow.com/questions/48418534/which-matplotlib-methods-may-be-called-outside-the-gui-thread
    #
    # Anyway, if you run into problems, set `force_single_thread` to True

    UPDATE_DELAY = 0.01
    force_single_thread = False

    # For temporarily disabling updates
    _inhibit_update_plot = False

    def __init__(self, ax, kw=None, size=None, render_callback=None,
                 extent=None, colorbar=True):
        if            size: self.size            = size
        if render_callback: self.render_callback = render_callback

        if not kw: kw = {}

        if extent:
            kw['extent'] = extent

        kw.setdefault('origin', 'lower')
        self._lock # initialize lock attribute to prevent race condition
        self._initial_extent = kw['extent']
        self.ax = ax
        self._create_imshow(ax, kw)
        self._connect_callbacks()
        self._attach_ax_reference()

        if colorbar == True:
            self.colorbar = ax.get_figure().colorbar(self.im)

    def _create_imshow(self, ax, imshow_kwargs):
        self.im = ax.imshow(self.update_data(), **imshow_kwargs)

    def _connect_callbacks(self):
        cb = self.ax.callbacks
        cb.connect('xlim_changed', self.cb_ax_update)
        cb.connect('ylim_changed', self.cb_ax_update)

    def _attach_ax_reference(self):
        ''' prevent getting garbage collected until ax disappears '''
        setattr(self.ax, "___mpl_render_ref_{}".format(id(self)), self)

    @property
    def extent(self):
        ''' query the current extent of the displayed data '''
        if self.im:
            return self.im.get_extent()
        else:
            return self._initial_extent

    @property
    def viewlim_extent(self):
        ''' extent of the axis.viewLim; setting this attribute makes the
        plot zoom to a particular region '''
        x0, y0, xd, yd = self.ax.viewLim.bounds
        x1 = x0 + xd
        y1 = y0 + yd
        return (x0, x1, y0, y1)

    @viewlim_extent.setter
    def viewlim_extent(self, extent):
        ax = self.ax
        self._inhibit_update_plot = True # avoid triggering two update events
        ax.set_xlim(extent[:2])
        self._inhibit_update_plot = False
        ax.set_ylim(extent[2:4])

    def update_data(self):
        ''' set self.data to self.user_render(), then return it

        NOTE: to trigger an update, use the `trigger_update()` method instead
        '''
        self.data = self.user_render()
        return self.data

    def user_render(self):
        ''' return image with size (self.h, self.w), representing area
        `self.extent`. by default, this calls
        `self.render_callback(self.size, self.extent)`, but you can
        override it to do whatever you want'''
        return self.render_callback(self.size, self.extent)

    @property
    def visible_size(self):
        ''' return size in pixels of image as it is shown on screen '''
        return tuple(ceil(x) for x in
                     ax.axesPatch.get_window_extent().bounds[2:4])

    def user_adjust_size(self):
        ''' by default this does nothing; override this '''

    def user_adjust_colorbar(self):
        ''' by default this calls `rescale_colorbar_to_data` '''
        self.rescale_colorbar_to_data()

    def rescale_colorbar_to_data(self):
        ''' note: this assumes `self.data` is defined '''
        V = self.data
        cbar = self.colorbar
        v0, v1 = np.nanmin(V), np.nanmax(V)
        self.im.set_clim(vmin=v0, vmax=v1)
        cbar_ticks = np.linspace(v0, v1, num=5, endpoint=True)
        cbar.set_ticks(cbar_ticks)

    def cb_ax_update(self, ax):
        ''' callback to update axis '''
        self.trigger_update()

    def trigger_update(self):
        '''
        Update the plot by re-rendering the visible area.

        This triggers an eventual update if `self.force_single_thread`
        is False, or updates right away otherwise. '''

        if self.force_single_thread:
            self._update_plot()
        else:
            Thread(target=self._thread_thunk_update).start()

    def _update_plot(self):
        if self._inhibit_update_plot:
            return

        ax = self.ax
        ax.set_autoscale_on(False) # prevent infinite loop

        # adjust image resolution if need be
        self.user_adjust_size()

        # get visible extent
        extent = self.viewlim_extent

        # update the image object with our new data and extent
        im = self.im
        im.set_extent(extent)
        self.data = self.user_render()
        im.set_data(self.data)

        # adjust colorbar if need be
        self.user_adjust_colorbar()

        ax.figure.canvas.draw_idle()

        # remove reference to `self.data` to allow GC
        self._after_update_plot_del_data()

    def _after_update_plot_del_data(self):
        # override this if you actually do need `self.data`
        self.data = None

    @cached_property
    def _lock(self):
        return Lock()

    def _thread_thunk_update(self):
        with self._lock:
            self._update_id = uid = self._update_id + 1
        sleep(self.UPDATE_DELAY)
        with self._lock:
            if self._update_id == uid: # nobody scooped us?
                self._update_plot()

