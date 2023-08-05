"""
Color presets and utility functions for color generation.

In *rectify*, a color is either a triple ``(r, g, b)``, where ``r``,
``g`` and ``b``, each an integer between 0 and 255, are the red, green
and blue components of a color; or anything `supported by Pillow's
ImageColor
<https://pillow.readthedocs.io/en/latest/reference/ImageColor.html>`_.

A palette in this context is either a color, or a list of colors, or
something that, when called, returns a color. Any of these can be passed
directly as an argument to the main :func:`rectify.image.generate`
function for setting the colors for the background and the bars.

There are predefined palettes available in this module for basic color
sets, like pastel colors or grayscale. If you want to define your own
palette, you don't need this module; just pass your palette directly to
the :func:`rectify.image.generate`.
"""
from random import choice, randint

from PIL import ImageColor


palettes = {}

def palette(function):
    """Decorator for registering palettes."""
    global palettes
    palettes[function.__name__] = function
    return function


@palette
def black():
    """Get pure black."""
    return (0, 0, 0)


@palette
def white():
    """Get pure white."""
    return (255, 255, 255)


@palette
def grayscale():
    """Get a shade of gray, including white and black."""
    shade = randint(0, 255)
    return (shade, shade, shade)


@palette
def dark():
    """Get a dark color."""
    hue = randint(0, 360)
    sat = randint(0, 100)
    light = randint(0, 50)
    return 'hsl({},{}%,{}%)'.format(hue, sat, light)


@palette
def light():
    """Get a light color."""
    hue = randint(0, 360)
    sat = randint(0, 100)
    light = randint(50, 100)
    return 'hsl({},{}%,{}%)'.format(hue, sat, light)


@palette
def pastel():
    """Get a soft color."""
    hue = randint(0, 360)
    sat = randint(0, 50)
    light = randint(50, 100)
    return 'hsl({},{}%,{}%)'.format(hue, sat, light)


@palette
def neon():
    """Get a vivid color."""
    hue = randint(0, 360)
    sat = 100
    light = 50
    return 'hsl({},{}%,{}%)'.format(hue, sat, light)


@palette
def eight_bit():
    """Get a color with 3 bits for red and green and 2 for blue."""
    color = randint(0, 255)
    red = color >> 5
    green = (color >> 2) & 7
    blue = color & 3
    return (red << 5, green << 5, blue << 6)


@palette
def warm():
    """Get a warm color."""
    hue = (randint(0, 180) + 270) % 360
    sat = randint(50, 100)
    light = randint(0, 50)
    return 'hsl({},{}%,{}%)'.format(hue, sat, light)


@palette
def cold():
    """Get a cold color."""
    hue = randint(90, 270)
    sat = randint(50, 100)
    light = randint(0, 50)
    return 'hsl({},{}%,{}%)'.format(hue, sat, light)


@palette
def random():
    """Get any RGB color."""
    color = (
        randint(0, 255),
        randint(0, 255),
        randint(0, 255)
    )
    return color


def pick_color(palette=None):
    """
    Randomly pick a color from a palette.

    Parameters
    ----------
    palette
        A wide range of types is accepted for this parameter. The
        following describes the result of using a specific one:

        - ``None``: a random color
        - ``callable``: the result of calling the callable
        - :obj:`list`: a random element from the list
        - anything else: used directly

        Note that the respective results will, if possible, be first
        converted to the canonical RGB representation.

    Returns
    -------
    :obj:`tuple` of :obj:`int`
        A triple containing the RGB representation of a color from the
        palette.

    Raises
    ------
    ValueError
        The palette produced a color that couldn't be parsed.
    """
    if palette is None:
        return random()

    elif isinstance(palette, str) and palette in palettes:
        return rgb(palettes[palette]())

    elif callable(palette):
        return rgb(palette())

    elif isinstance(palette, list) and palette:
        return rgb(choice(palette))

    try:
        return rgb(palette)
    except ValueError:
        raise ValueError('Unsupported palette: {}'.format(palette))


def rgb(color):
    """
    Get the RGB representation of a color.

    Parameters
    ----------
    color : :obj:`tuple` or :obj:`str`
        The color to normalize. Supported formats:
            - a triple ``(r, g, b)``, with
              0 <= ``r``, ``g``, ``b`` <= 255
            - a `Pillow color string
              <https://pillow.readthedocs.io/en/5.1.x/reference/ImageColor.html>`_

    Returns
    -------
    :obj:`tuple` of :obj:`int`
        A triple containing three integers from 0 to 255: the red,
        green and blue component of the color.

    Raises
    ------
    ValueError
        If the provided color couldn't be converted.
    """
    if isinstance(color, tuple):
        if len(color) == 3 and all(0 <= c <= 255 for c in color):
            return color

    elif isinstance(color, str):
        try:
            return ImageColor.getrgb(color)
        except ValueError:
            pass

    raise ValueError('Unsupported color: {}'.format(color))
