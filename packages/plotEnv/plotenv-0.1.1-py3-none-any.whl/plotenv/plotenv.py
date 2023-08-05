#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
plotenv
=======

Wrapper for matplotlib and seaborn. Provides customised plotting enviroment
for publishable worthy.

purpose:
    - customization of plots for publishing (journals, thesis)
    - beautiful plots
    
:First Added:   2015-05-25
:Last Modified: 2018-02-16
:Author:        Lento Manickathan

"""

# Local modules
from ._cm import _cmb_data

# Import required modules
import numpy as _np
from cycler import cycler as _cycler

# Seaborn
import seaborn as _sns
from seaborn import despine as _despine

# Matplotlib
import matplotlib as _mpl
import matplotlib.pyplot as _plt
from matplotlib.offsetbox import AnchoredText as _AnchoredText
from matplotlib.patheffects import withStroke as _withStroke
from mpl_toolkits.axes_grid1 import ImageGrid as _ImageGrid
import matplotlib.dates as _mdates

# CONSTANTS (colors)
COLOR_FLATUI = {'red'      : '#e74c3c',
                'yellow'   : '#f1c40f',
                'green'    : '#2ecc71',
                'blue'     : '#3498db',
                'violet'   : '#8e44ad',
                'dark'     : '#2c3e50',
                'gray'     : '#7f8c8d',
                'darkgreen': '#16a085',
                'orange'   : '#d35400',
                'darkred'  : '#c0392b',
                'darkblue' : '#2980b9'}

COLOR_MPL = {'blue'    : '#1f77b4',
             'orange'   : '#ff7f0e',
             'green'    : '#2ca02c',
             'red'      : '#d62728',
             'purple'   : '#9467bd',
             'brown'    : '#8c564b',
             'pink'     : '#e377c2',
             'gray'     : '#7f7f7f',
             'olive'    : '#bcbd22',
             'cyan'     : '#17becf'}


# Marker style
MARKERTYPES = ['o', 's', 'D', 'v', '^', '<', '>','*', 'p', 'd',',', '.',]

# matplotlib parameters
DEFAULT_RCPARAMS = {'axes.axisbelow'  : True,
                    'axes.edgecolor'  : '0.15',
                    'axes.facecolor'  : 'white',
                    'axes.labelcolor' : '0.15',
                    'axes.grid'       : False,
                    'axes.labelsize'  : 20,
                    'axes.linewidth'  : 1.25,
                    'axes.titlesize'  : 12,
                    'figure.figsize'  : _np.array([2./(_np.sqrt(5)-1), 1])*5,
                    'font.family'     : ['sans-serif'], #['sans-serif'],
                    'font.sans-serif' : ['Helvetica'],# 'Arial', 'DejaVu Sans', 'sans-serif'],
		    'font.serif'      : ['Times'], #, 'Times New Roman', 'serif'], Palatino			    
                    #                     'Bitstream Vera Sans', 'sans-serif'],
                    'grid.color'      : '0.8',
                    'grid.linestyle'  : '-',
                    'grid.linewidth'  : 1,
                    'interactive'     : True,
                    'legend.fontsize' : 16,
                    'legend.frameon'  : False,
                    'legend.loc'      : 'best',
                    'legend.labelspacing': 0.05,
                    'legend.numpoints': 1,
                    'legend.scatterpoints' : 1,
                    'lines.linewidth' : 2,#1.2,
                    'lines.markeredgewidth' : 0.,
                    'lines.markersize': 12,
                    'lines.solid_capstyle' : 'round',
                    'mathtext.fontset': 'cm',
                    'patch.linewidth' : .3,
                    'savefig.dpi'     : 350,
                    'savefig.format'  : 'pdf',
                    #'text.color'      : '0.15',
                    'text.usetex'     : True,
                    #'text.latex.unicode' : True,
                    #'xtick.color'     : '0.15',
                    #'xtick.direction' : 'out',
                    'xtick.labelsize' : 18,
                    'xtick.major.pad' : 7,
                    'xtick.major.size': 6,
                    'xtick.minor.size': 3,
                    #'ytick.color'     : '0.15',
                    #'ytick.direction' : 'out',
                    'ytick.labelsize' : 18,
                    'ytick.major.pad' : 7,
                    'ytick.major.size': 6,
                    'ytick.minor.size': 3}

LINESTYLE = [(0, ()), # solid
            #('loosely dotted',      (0, (1, 10))),
             #('dotted',              (0, (1, 5))),
             #('loosely dashed',      (0, (5, 10))),
             #('dashed',              (0, (5, 5))),
            (0, (5, 5)), # densely dashed
             #('loosely dashdotted',  (0, (3, 10, 1, 10))),
             #('dashdotted',          (0, (3, 5, 1, 5))),
            (0, (3, 5, 1, 5)), # 'densely dashdotted'
             #('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
             #('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
             #('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))])
             (0, (1, 5)), # densely dotted
             ]


# Pollute (steal) matplotlib methods
#figure = _plt.figure
#plot = _plt.plot
pcolor = _plt.pcolor
imshow = _plt.imshow
contourf = _plt.contourf
pause = _plt.pause
clf = _plt.clf
close = _plt.close
gca = _plt.gca
gcf = _plt.gcf
plot = _plt.plot
plt = _plt # For more


# Pollute (steal) seaborn methods
kdeplot = _sns.kdeplot
jointplot = _sns.jointplot
heatmap = _sns.heatmap
sns = _sns # For more

# Custom wrapper for figure
def _wrapper_figure(function):
    def wrapper(*args,**kwargs):
        fig = function(*args,**kwargs)
        ax = fig.gca()
        return fig, ax
    wrapper.__doc__ = function.__doc__
    return wrapper

figure = _wrapper_figure(_plt.figure)
    

def initialize(plotType='both', numColors=10, interactive=True):
    """

    Parameters
    ----------
    plotType : 'line', 'surface', 'both' (default)

    numColors : int, or one of {1, 3, 10 (default), ##}
                The number of colour required for plotting.

    interactive : bool
                  Turn plot interactive on (default)

    See Also
    --------
    Palette : Line plot
                viridis
              Surface plot
                viridis

    Examples
    --------
    >>> palette = set() # plotType='both', numColors=10, interactive=True
    or 
    >>> palette = set(plotType='line', numColors=2)
    or
    >>> palette = set(plotType='surface')

    """

    # Set matplotlib rc parameters
    rcParams = DEFAULT_RCPARAMS

    # Set plot interactive on/off
    rcParams['interactive'] = interactive

    # Determine plot type
    if plotType == 'line':

        # Set Palette
        palette = linePlotPalette(numColors)
        #rcParams['axes.color_cycle'] = list(palette)
        rcParams['axes.prop_cycle'] = _cycler('color', list(palette))

    elif plotType == 'surface':

        # Set Palette
        palette = surfacePlotPalette()

    elif plotType == 'both':
        # Set colormap palette
        palette = surfacePlotPalette()
        palette['colors'] = linePlotPalette(numColors)
        rcParams['axes.prop_cycle'] = _cycler('color', list(palette['colors']))
    else:
        return NotImplementedError('plot type unknown or not implemented')

    # Set matplotlib rc parameters
    _mpl.rcParams.update(rcParams)

    print('Done!')
    return palette


def linePlotPalette(numColors):
    """
    Returns plot palette. Color palette : Flat ui: http://designmodo.github.io/Flat-UI/

    Parameters
    ----------
    numColors : int, or one of {1 (default), 3, 9}
                The number of colour required for plotting.

    Examples
    --------
    >>> palette = linePlotPalette(numColors=4)
    or

    """

    # Define the color palatte
    if numColors == 1:
        # Midnight blue
        palette = [PUREBLACK]

    elif numColors == 3:
        palette = [PUREBLACK,DARKRED,DARKBLUE]

    # elif numColors > 3 and numColors <= 9:
    #     # Alizarin, Peter river, Emerald, Sun Flower, Wisteria, Midnight blue
    #     # Asbestos, Green sea, Pumpkin
    #     #palette = [RED, BLUE, GREEN, YELLOW, VIOLET, DARK, GRAY, DARKGREEN, ORANGE][:numColors]
    #     palette = [RED, BLUE, DARKGREEN, ORANGE, VIOLET, DARK, GREEN, GRAY, YELLOW][:numColors]
    else:
        #return NotImplementedError('numColors should be 1 to 9.')
        palette = _plt.cm.viridis(_np.linspace(0,1,numColors))

    return palette


def surfacePlotPalette():
    """
    Surface plot palette

    Divergent colormap [cold (blue)-> hot (red)]

    Sequential colormaps: 1) Cold, 2) Hot

    """

    # Palette CMB: based on planck cosmic microwave background radiation cmap
    # Info : http://zonca.github.io/2013/09/Planck-CMB-map-at-high-resolution.html
    CMB = {'DIV'    : _mpl.colors.ListedColormap(list(zip(_cmb_data[:,0],_cmb_data[:,1],_cmb_data[:,2]))),
           'HOT'    : _mpl.colors.ListedColormap(list(zip(_cmb_data[64:,0],_cmb_data[64:,1],_cmb_data[64:,2]))),
           'COLD'  : _mpl.colors.ListedColormap(list(zip(_cmb_data[64::-1,0],_cmb_data[64::-1,1],_cmb_data[64::-1,2]))),
           'DIV_R'  : _mpl.colors.ListedColormap(list(zip(_cmb_data[::-1,0],_cmb_data[::-1,1],_cmb_data[::-1,2]))),
           'HOT_R' : _mpl.colors.ListedColormap(list(zip(_cmb_data[:64:-1,0],_cmb_data[:64:-1,1],_cmb_data[:64:-1,2]))),
           'COLD_R'   : _mpl.colors.ListedColormap(list(zip(_cmb_data[:64,0],_cmb_data[:64,1],_cmb_data[:64,2])))
           }

    # Palette spectral
    SPECTRAL = {'DIV'    : _mpl.cm.Spectral_r,
                'HOT'    : _mpl.colors.ListedColormap(_mpl.cm.Spectral_r(_np.arange(128,256))),
                'COLD'   : _mpl.colors.ListedColormap(_mpl.cm.Spectral(_np.arange(128,256))),
                'DIV_R'  : _mpl.cm.Spectral,
                'HOT_R'  : _mpl.colors.ListedColormap(_mpl.cm.Spectral(_np.arange(0,128))),
                'COLD_R' : _mpl.colors.ListedColormap(_mpl.cm.Spectral_r(_np.arange(0,128)))
                }

    return {'CMB' : CMB, 'SPECTRAL' : SPECTRAL}


def cleanupFigure(despine=True, tightenFigure=True):
    """
    Cleans up the figure by:
        1) Removing unnecessary top and right spines using seaborn's `despine` function
        2) Tighten the figure using pyplot's `tight_layout` function

    Parameters
    ----------
    despine : bool, True (default) or False

    tightenFigure : bool, True (default) or False


    See Also
    --------
    seaborn.despine : Seaborn's despine function

    pyplot.tight_layout : Function to adjust the subplot padding


    Examples
    --------
    >>> cleanupFigure(despine=True, tightenFigure=True)

    """

    # Remove extra spline
    if despine:
        _despine()

    # Remove the extra white spaces
    if tightenFigure:
        _plt.gcf().tight_layout()

    # Re-draw plot
    _plt.draw()

def legend(outside=False,xmax=None,*args,**kwargs):
    if outside:
        _plt.legend(bbox_to_anchor=(1,1),*args,**kwargs)
        _plt.gcf().subplots_adjust(right=0.8 if xmax is None else xmax)
    else:
        _plt.legend(*args,**kwargs)

legend.__doc__ = _plt.legend.__doc__

def xdateformat(xformat='%H:%M',autofmt=True):
    """
    set dateformat for x axis
    """
    # Auto
    if autofmt:
        fig = _plt.gcf()
        fig.autofmt_xdate()
    
    # change format of x
    ax = _plt.gca()
    ax.xaxis.set_major_formatter(_mdates.DateFormatter(xformat))


def colorbar(ticks=None,orientation='vertical',splitTicks=False,strFormat='%.2g',label=None,**kw):
    """
    Customized colorbar

    Parameters
    ----------
    ticks
    orientation
    splitTicks
    strFormat  : '%.2g' or None
                  None: default to matplotlib formatting.
    """

    # determine colorbar position
    if orientation[0]=='h':
        orientation='horizontal'
        aspect=40
        if splitTicks:
            pad=0.25
        else:
            pad=0.2
    elif orientation[0]=='v':
        orientation='vertical'
        aspect=25
        pad=0.05
    else:
        ValueError("orientation '%s' unknown" % orientation)

    # Default colorbar params
    cbParams = {'aspect'       : aspect,
                'drawedges'    : True if ((len(_plt.gca().collections) < 22) and (len(_plt.gca().collections) > 0)) else False,
                'format'       : strFormat,
                'orientation'  : orientation,
                'pad'          : pad,
                'spacing'      : 'proportional',
                #'ticks'        : ticks
                }
    if ticks is not None:
        cbParams['ticks'] = ticks

    # Modify cb params
    cbParams.update(kw)

    if cbParams['format'] == 'default':
        cbParams['format'] = None # Default

    # Draw colorbar
    cb = _plt.colorbar(**cbParams)

    # Split ticks
    if splitTicks:
        if orientation[0] == 'h':
            # Change ticks position
            if _np.any(ticks<0) and _np.any(ticks>0):
                for v,t in zip(ticks,cb.ax.xaxis.majorTicks):
                    if v>0:
                        t._apply_params(gridOn=False,label1On=False,label2On=True,
                                        tick1On=False,tick2On=True)
        elif orientation[0] == 'v':
            NotImplementedError("orientation 'vertical' not implemented")
        else:
            ValueError("orientation '%s' unknown" % orientation)

    # Add label
    if label:
        if orientation[0] == 'h':
            cb.ax.set_xlabel(label)
        elif orientation[0] == 'v':
            cb.ax.set_ylabel(label)
        else:
            ValueError("orientation '%s' unknown" % orientation)

    # Redraw plot
    _plt.draw()

    return cb

def subtitles(axes,titles,**kwargs):
    """
    add titles to sub figures

    example
    -------
    titleList = plotenv.subtitles(axes=(ax1,ax2),titles=["(a)","(b)"],
                                  loc=2,size=18.0)
    """

    loc  = kwargs.pop('loc', 2)
    size = kwargs.pop('size', DEFAULT_RCPARAMS['legend.fontsize'])

    # Add title to each axis
    ats = []
    for ax,title in zip(axes,titles):
        at = _AnchoredText(title, loc=loc, prop=dict(size=size),
                          pad=0., borderpad=0.5,
                          frameon=False, **kwargs)
        ax.add_artist(at)
        at.txt._text.set_path_effects([_withStroke(foreground="w", linewidth=3)])
        ats.append(at)

    return ats

def imagegrid(fig,nrow_ncols,xlabel=None,ylabel=None,**kwargs):
    """
    create an image grid - multiple plots
    """

    # multi-axes grid
    grid = _ImageGrid(fig, 111,
                      nrows_ncols=nrow_ncols,
                      direction=kwargs.pop('direction','column'),
                      axes_pad=kwargs.pop('axes_pad',0.5),
                      add_all=kwargs.pop('add_all',True),
                      #   label_mode="all",
                      share_all=kwargs.pop('share_all',False),
                      cbar_location=kwargs.pop('cbar_location','right'),
                      cbar_mode=kwargs.pop('cbar_mode','single'),
                      cbar_size=kwargs.pop('cbar_size','2%'),
                      cbar_pad=kwargs.pop('cbar_pad',0.25))

    # Add x,y labels only on the edges
    nrow,ncol = nrow_ncols
    if xlabel is not None:
        for i in nrow*_np.arange(ncol)+nrow-1:
            grid[i].set_xlabel(xlabel)
    if ylabel is not None:
        for i in range(nrow):
            grid[i].set_ylabel(ylabel)

    return grid


def add_text(text,loc=2,size=25,color='k',ax=None,weight='bold',borderpad=0.2):
    at = _AnchoredText(text, loc=loc, prop=dict(size=size,weight=weight,color=color),
                      pad=0., borderpad=borderpad,frameon=False)
    
    if ax is None:
        ax = _plt.gca()
    ax.add_artist(at)
    #at.txt._text.set_path_effects([_withStroke(foreground="w", linewidth=3)])

    return at


def quadBezierCurve(p0=[0,0],p1=[0.5,1],p2=[1,0],n=100):
    """
    quadratic bézier curve
    
    More info : https://en.wikipedia.org/wiki/Parabola
    """
    t = _np.linspace(0,1,n)
    p0 = _np.array(p0).reshape(-1,1)
    p1 = _np.array(p1).reshape(-1,1)
    p2 = _np.array(p2).reshape(-1,1)
    
    return (p0 -  2.0*p1 + p2)*t*t + (-2.0*p0 + 2*p1)*t + p0

def cubicBezierCurve(p0=[0,0],p1=[0.5,1],p2=[0.5,1],p3=[1,0],n=100):
    """
    cubic bézier curve
    
    More info : https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B.C3.A9zier_curves
    """
    t = _np.linspace(0,1,n)
    p0 = _np.array(p0).reshape(-1,1)
    p1 = _np.array(p1).reshape(-1,1)
    p2 = _np.array(p2).reshape(-1,1)
    p3 = _np.array(p3).reshape(-1,1)
    
    return (1-t)*quadBezierCurve(p0,p1,p2,n) + t*quadBezierCurve(p1,p2,p3,n)



# def labels(xlabel=None, ylabel=None, title=None):
#     """
#     Add labels: x,y, and title
#     """
#     if xlabel is not None:
#         _plt.xlabel(xlabel)
#     if ylabel is not None:
#         _plt.ylabel(ylabel)
#     if title is not None:
#         _plt.title(title)
