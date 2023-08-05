from setuptools import setup, find_packages
pkg = "mpl_render"
ver = '0.0.1'

with open(pkg+'/version.py', 'wt') as h:
    h.write('__version__ = "{}"\n'.format(ver))

setup(
    name             = pkg,
    version          = ver,
    description      = ("Zoom into matplotlib imshow by providing "
                        "a render callback"),
    author           = "Eduard Christian Dumitrescu",
    license          = "LGPLv3",
    url              = "https://hydra.ecd.space/f/mpl_render/",
    packages         = find_packages(),
    install_requires = ['numpy', 'matplotlib', 'cached_property'],
    classifiers      = ["Programming Language :: Python :: 3 :: Only"])
