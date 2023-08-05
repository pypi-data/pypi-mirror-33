
from .mandelbrot import mandelbrot_render
from mpl_render import RenderingImShow
from matplotlib import pyplot as plt
import numpy as np

import ipywidgets as widgets
from IPython.display import display

def main():
    params = {}

    fig, ax = plt.subplots(1, 1)
    p = RenderingImShow(
        ax, size=(400, 300),
        extent=(-2, 1, -1.32, 1.32),
        render_callback=(lambda size, extent:
                         mandelbrot_render(size, extent, **params)))
    ax.set_title("Mandelbrot set")

    button = widgets.Button(description="Click Me!")
    def on_click(b):
        # zoom to a specific region
        p.viewlim_extent = (-0.638331, -0.624316, 0.677216, 0.690501)
    button.on_click(on_click)

    def iterations_on_value_change(change):
        params.update(iterations=change['new'])
        p.trigger_update()

    iterations_widget = widgets.IntSlider(
        description="Iterations",
        value=50, min=0, max=200, continuous_update=False)
    iterations_widget.observe(iterations_on_value_change, names='value')

    display(iterations_widget)
    display(button)
    plt.show()

if __name__=='__main__':
    main()
