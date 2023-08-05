import matplotlib
import matplotlib.font_manager
import numpy as np
import cycler
from .colors import RGB, Color, colors

def showSwatch(swatch, M=6):
    fig = matplotlib.pyplot.figure(figsize=(9, 4), dpi=216)
    ax = fig.add_axes([0, 0, 1, 0.92], frameon = False)
    for i in range(42):
        x = i % M
        y = M - i // M
        c = swatch[i]
        #print('{0:.2f},{1:.2f} -> {2}'.format(x, y, c[1].hex_format()))
        matplotlib.pyplot.plot(x, y, '.', markersize=50, color=c[1].hex_format())
        matplotlib.pyplot.text(x + 0.004, y - 0.03, str(i), color='white', va='center', ha='center')
        matplotlib.pyplot.text(x + 0.15, y - 0.03, c[0], va='center')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_xlim([-0.15, M])
    ax.set_ylim([-0.5, M + 0.5])
    fig.suptitle('Swatch', fontweight='bold')
    return fig

def rgb2lab(rgb):
    rgbv = np.array(rgb) / 255.0
    if len(rgbv.shape) == 1:
        rgbv = rgbv[[np.newaxis]]
    matrix = [[0.412453, 0.357580, 0.180423],
              [0.212671, 0.715160, 0.072169],
              [0.019334, 0.119193, 0.950227]]
    mat = np.array(matrix).transpose()
    xyz = np.matmul(rgbv, mat)
    # Normalize to D65 white point
    x = xyz[:, 0] / 0.950456;
    y = xyz[:, 1]
    z = xyz[:, 2] / 1.088754;
    # Threshold
    T = 0.008856
    xt = (x > T).astype(bool)
    yt = (y > T).astype(bool)
    zt = (z > T).astype(bool)
    y3 = y ** (1.0 / 3.0)
    fX = np.multiply(xt, x ** (1.0 / 3.0)) + np.multiply(~xt, 7.787 * x + 16.0 / 116.0)
    fY = np.multiply(yt, y3)               + np.multiply(~yt, 7.787 * y + 16.0 / 116.0)
    fZ = np.multiply(zt, z ** (1.0 / 3.0)) + np.multiply(~zt, 7.787 * y + 16.0 / 116.0)
    L = np.multiply(yt, 116.0 * y3 - 16.0) + np.multiply(~yt, 903.3 * y)
    a = 500.0 * (fX - fY)
    b = 200.0 * (fY - fZ)
    return np.array([L, a, b]).transpose()

def setColorCycleX():
    n = [5, 11, 29, 21, 15, 39, 6, 34, 9, 27, 20, 38]
    c = []
    for i in n:
        c.append(swatch[i][1].hex_format())
    matplotlib.rcParams['axes.prop_cycle'] = cycler.cycler(color=c)

def setColorCycle(column=3):
    c = []
    for i in range(column, len(swatch), 6):
        c.append(swatch[i][1].hex_format())
    matplotlib.rcParams['axes.prop_cycle'] = cycler.cycler(color=c)

def listFonts(verbose=0, showname=False):
    def make_html(fontname, showname=showname):
        line = '<p><span style="font-family:{font}; font-size:16pt;">{font}</span>'.format(font=fontname)
        if showname:
            line += ' (<span style="color:blue;">{}</span>)'.format(fontname)
        line += '</p>'
        return line
    code = '\n'.join([make_html(font) for font in sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))])
    if verbose:
        print('Type these in Notebook:\nfrom IPython.core.display import HTML\nHTML(result)')
    html = '<div style="column-count:2;">{}</div>'.format(code)
    return html

#
# Some default parameters I'd like to us
#

matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Arial']
matplotlib.rcParams['font.sans-serif'] = ['System Font', 'Verdana', 'Arial']
matplotlib.rcParams['figure.figsize'] = (8, 4)   # Change the size of plots
matplotlib.rcParams['figure.dpi'] = 108

highlight = [0.85, 0.96, 0]

# Make a list out of it
colorList = list(colors.items())

# The first color palette
idx = [433, 303, 290, 401, 537, 336, 129, 127, 270, 15, 142, 513, 90, 56, 325, 373, 460, 87, 59, 517, 521, 476, 348, 343, 356, 286, 107, 108, 531, 118, 124, 124, 229, 217, 202, 179, 404, 213, 544, 516, 482, 21]

swatch = [colorList[x] for x in idx]
swatchn = [[c[1].red, c[1].green, c[1].blue] for c in swatch]
swatchInHex = [x[1].hex_format() for x in swatch]

setColorCycleX()
