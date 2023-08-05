'''Functions for assisting with plotting catalog data.
'''

from collections import OrderedDict
from random import seed, shuffle
from matplotlib.colors import rgb2hex
import seaborn as sns

from palettable import colorbrewer, cubehelix, wesanderson

__all__ = [
    'bandrepf', 'bandcolorf', 'radiocolorf', 'xraycolorf', 'bandaliasf',
    'bandshortaliasf', 'bandwavef', 'bandmetaf', 'bandcodes',
    'bandwavelengths',
    'bandgroupf'
]

bandreps = {
    'Ks': ['K_s'],
    'M2': ['uvm2', 'UVM2', 'UVm2', 'Um2', 'm2', 'um2'],
    'W1': ['uvw1', 'UVW1', 'UVw1', 'Uw1', 'w1', 'uw1'],
    'W2': ['uvw2', 'UVW2', 'UVw2', 'Uw2', 'w2', 'uw2'],
}

# Some bands are uniquely tied to an instrument/telescope/system, add this
# info here.
bandmeta = {
    'M2':     {'telescope': 'Swift', 'instrument': 'UVOT'},
    'W1':     {'telescope': 'Swift', 'instrument': 'UVOT'},
    'W2':     {'telescope': 'Swift', 'instrument': 'UVOT'},
    'F110W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F160W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F225W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F275W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F336W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F475W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F606W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F625W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F775W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F814W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F850W':  {'telescope': 'Hubble', 'instrument': 'WFC3'},
    'F850LP': {'telescope': 'Hubble', 'instrument': 'WFC3'}
}

bandcodes = [
    "u",
    "g",
    "r",
    "i",
    "z",
    "u'",
    "g'",
    "r'",
    "i'",
    "z'",
    "u_SDSS",
    "g_SDSS",
    "r_SDSS",
    "i_SDSS",
    "z_SDSS",
    "U",
    "B",
    "V",
    "R",
    "I",
    "G",
    "Y",
    "J",
    "H",
    "K",
    "C",
    "CR",
    "CV",
    "M2",
    "W1",
    "W2",
    "pg",
    "Mp",
    "w",
    "y",
    "Z",
    "F110W",
    "F160W",
    "F225W",
    "F275W",
    "F336W",
    "F475W",
    "F606W",
    "F625W",
    "F775W",
    "F814W",
    "F850W",
    "F850LP",
    "VM",
    "RM",
    "Ks",
    "Kepler"
]

bandaliases = OrderedDict([
    ("u_SDSS", "u'"),
    ("g_SDSS", "g'"),
    ("r_SDSS", "r'"),
    ("i_SDSS", "i'"),
    ("z_SDSS", "z'")
])

bandshortaliases = OrderedDict([
    ("u_SDSS", "u'"),
    ("g_SDSS", "g'"),
    ("r_SDSS", "r'"),
    ("i_SDSS", "i'"),
    ("z_SDSS", "z'"),
    ("G", "")
])

bandwavelengths = {
    "u": 354.,
    "g": 475.,
    "r": 622.,
    "i": 763.,
    "z": 905.,
    "y": 1005.,
    "u'": 354.,
    "g'": 475.,
    "r'": 622.,
    "i'": 763.,
    "z'": 905.,
    "U": 365.,
    "B": 445.,
    "V": 551.,
    "R": 658.,
    "I": 806.,
    "Y": 1020.,
    "J": 1220.,
    "H": 1630.,
    "K": 2190.,
    "M2": 260.,
    "W1": 224.6,
    "W2": 192.8,
    "Kepler": 5781.30
}

bandgroups = {
    "SDSS": ["u'", "g'", "r'", "i'", "z'"],
    "UVOT": ["W2", "M2", "W1"],
    "HST": ['F110W', 'F160W', 'F225W', 'F275W', 'F336W', 'F475W', 'F606W', 'F625W', 'F775W', 'F814W', 'F850W', 'F850LP'],
    
    "Johnson": ['U', 'B', 'V', 'R', 'I', 'Y', 'J', 'H', 'K']
}

radiocodes = [
    "5.9"
]
xraycodes = [
    "0.3 - 10",
    "0.5 - 8"
]

seed(101)
# bandcolors = ["#%06x" % round(float(x)/float(len(bandcodes))*0xFFFEFF)
# for x in range(len(bandcodes))]
bandcolors = (cubehelix.cubehelix1_16.hex_colors[2:13] +
              cubehelix.cubehelix2_16.hex_colors[2:13] +
              cubehelix.cubehelix3_16.hex_colors[2:13])
shuffle(bandcolors)
bandcolors2 = cubehelix.perceptual_rainbow_16.hex_colors
shuffle(bandcolors2)
bandcolors3 = cubehelix.jim_special_16.hex_colors
shuffle(bandcolors3)
bandcolors = bandcolors + bandcolors2 + bandcolors3
bandcolordict = dict(list(zip(bandcodes, bandcolors)))

radiocolors = wesanderson.Zissou_5.hex_colors
shuffle(radiocolors)
radiocolordict = dict(list(zip(radiocodes, radiocolors)))

xraycolors = colorbrewer.sequential.Oranges_9.hex_colors[2:]
shuffle(xraycolors)
xraycolordict = dict(list(zip(xraycodes, xraycolors)))


def bandrepf(code):
    for rep in bandreps:
        if code in bandreps[rep]:
            return rep
    return code


def bandcolorf(code):
    newcode = bandrepf(code)
    if newcode in bandcolordict:
        return bandcolordict[newcode]
    return 'black'


def radiocolorf(freq):
    ffreq = (float(freq) - 1.0)/(45.0 - 1.0)
    pal = sns.diverging_palette(200, 60, l=80, as_cmap=True, center="dark")
    return rgb2hex(pal(ffreq))


def xraycolorf(code):
    if code in xraycolordict:
        return xraycolordict[code]
    return 'black'


def bandaliasf(code):
    newcode = bandrepf(code)
    if newcode in bandaliases:
        return bandaliases[newcode]
    return newcode


def bandgroupf(code):
    newcode = bandrepf(code)
    for group in bandgroups:
        if newcode in bandgroups[group]:
            return group
    return ''


def bandshortaliasf(code):
    newcode = bandrepf(code)
    if newcode in bandshortaliases:
        return bandshortaliases[newcode]
    return newcode


def bandwavef(code):
    newcode = bandrepf(code)
    if newcode in bandwavelengths:
        return bandwavelengths[newcode]
    return 0.


def bandmetaf(band, field):
    if band in bandmeta:
        if field in bandmeta[band]:
            return bandmeta[band][field]
    return ''
