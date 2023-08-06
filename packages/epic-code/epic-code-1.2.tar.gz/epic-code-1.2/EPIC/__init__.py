
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

class Unsupported(Exception):
    pass

class NotAnalytic(Exception):
    pass

class DataError(Exception):
    pass

root = __path__[0]

color_options = ['tableau', 'xkcd', 'css4', 'base']
for scheme, options in zip(['xkcd', 'css4'], [
    [
    'bright',
    'dark',
    'darkish',
    'very dark',
    'soft',
    'vibrant',
    'ugly',
    'vivid',
    'pastel',
    'pale',
    'neon',
    'off',
    'gold',
    'light',
    'lightish',
    'very light',
    'muted',
    'medium',
    'hot',
    'greyish',
    'faded',
    'electric',
    'dull',
    'dusty',
    'dirty',
    'deep',
    ], [
    'medium',
    'light',
    'dark',
    ]]):
    for option in options:
        color_options.append('%s-%s' % (scheme, option))

pyplot_available_styles = ['default',] + sorted([
        'bmh',
        'dark_background',
        'fivethirtyeight',
        'ggplot',
        'grayscale',
        'Solarize_Light2',
        'seaborn',
        'seaborn-bright',  
        'seaborn-whitegrid',
        'seaborn-dark',
        'seaborn-muted',
        'seaborn-dark-palette',
        'seaborn-pastel',
        'seaborn-white',
        'seaborn-ticks',
        'seaborn-colorblind',
        ])

pyplot_grid_styles = ['default',] + sorted([
        'bmh',
        'dark_background',
        'ggplot',
        'Solarize_Light2',
        'seaborn-bright',  
        'seaborn-colorblind',
        'seaborn-whitegrid',
        'seaborn-muted',
        'seaborn-dark-palette',
        'seaborn-pastel',
        ])
