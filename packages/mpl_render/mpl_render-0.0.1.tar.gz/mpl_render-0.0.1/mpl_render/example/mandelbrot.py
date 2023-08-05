from mpl_render import RenderingImShow
from matplotlib import pyplot as plt
import numpy as np

def mandelbrot_render(size, extent):
    radius = 2.0
    power = 2
    niter = 50

    xsize, ysize = size
    xstart, xend, ystart, yend = extent
    Xs = np.linspace(xstart, xend, xsize)
    Ys = np.linspace(ystart, yend, ysize).reshape(-1, 1)
    c = Xs + 1.0j * Ys
    threshold_time = np.zeros((ysize, xsize))
    z = np.zeros(threshold_time.shape, dtype=np.complex)
    mask = np.ones(threshold_time.shape, dtype=np.bool)
    for i in range(niter):
        z[mask] = z[mask]**power + c[mask]
        mask = (np.abs(z) < radius)
        threshold_time += mask
    return threshold_time

def main():
    fig, ax = plt.subplots(1, 1)
    p = RenderingImShow(ax, size=(400, 300),
                        extent=(-1, 1, -1, 1),
                        render_callback=mandelbrot_render)
    ax.set_title("Mandelbrot set")
    plt.show()

if __name__=='__main__':
    main()

