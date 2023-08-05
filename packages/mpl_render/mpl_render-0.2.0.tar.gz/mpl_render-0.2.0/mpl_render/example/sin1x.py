from mpl_render import RenderingPlot
from matplotlib import pyplot as plt
import numpy as np

def sin1x_render(size, extent):
    xstart, xend, ystart, yend = extent
    xsize, ysize = size
    Xs = np.linspace(xstart, xend, xsize)
    Ys = np.sin(1/Xs) * np.sqrt(np.abs(Xs))
    return (Xs, Ys)

def main():
    fig, ax = plt.subplots(1, 1)
    sz, ext = (2000, 2000), (-5, 5, -5, 5)

    # plot using full callback
    p = RenderingPlot(
        ax, size=sz, extent=ext,
        render_callback=sin1x_render)

    # plot using simple_plot shortcut
    p = RenderingPlot(
        ax, size=sz, extent=ext,
        kw=dict(linestyle='dashed'),
        simple_plot=lambda Xs: np.sin(Xs + 1/Xs)*np.sqrt(np.abs(Xs)))

    ax.set_title("Weird functions")
    plt.show()

if __name__=='__main__':
    main()

