"""
The module covers the main generating and saving functionality of the
package.
"""
import bisect
import logging
import os.path
import random

from PIL import Image, ImageDraw

from rectify import palette


logger = logging.getLogger(__name__)


def generate(width=200, height=200, background=None, colors=None, count=None):
    """
    Generate an image with colorful bars on a background.

    The dimensions of the image are customizable, as is the approximate
    number of bars to generate. The color of the background will be
    either random or, if ``background`` has been provided, randomly
    generated from a palette (which can also consist of a single color,
    see :mod:`rectify.palette`). Similarly, bar colors will be picked
    individually from the ``colors`` palette.

    Parameters
    ----------
    width : int
        The width of the image to generate, in pixels.
    height : int
        The height of the image to generate, in pixels.
    background
        The background color will be generated from this palette.
        See :mod:`rectify.palette` for more information.
    colors
        Bar colors will be generated from this palette. See
        :mod:`rectify.palette` for more information.
    count : int
        The target amount of bars to generate.

    Returns
    -------
    PIL.Image
        The generated `image
        <https://pillow.readthedocs.io/en/latest/reference/Image.html>`_.
    """
    _validate_positive_int(width)
    _validate_positive_int(height)
    if count is not None:
        _validate_positive_int(count)

    background = palette.pick_color(background)
    positions = _generate_bar_positions(width, count)

    image = Image.new('RGB', (width, height), background)
    draw = ImageDraw.Draw(image)
    for x1, x2 in positions:
        color = palette.pick_color(colors)
        draw.rectangle([x1, 0, x2, height], fill=color)
    del draw

    return image


def save(image, path):
    """
    Save an image to a specific location.

    Parameters
    ----------
    image : PIL.Image
        The `picture
        <http://pillow.readthedocs.io/en/latest/reference/Image.html>`_
        to save.
    path : str
        The path (optionally including the filename) where to save the
        image.
    """
    if os.path.isdir(path):
        path = os.path.join(path, 'rectify-image.png')
    elif not path.lower().endswith('.png'):
        path += '.png'

    if os.path.exists(path):
        logger.info('Overwriting existing "%s"', path)
    else:
        logger.info('Image saved to "%s"', path)

    image.save(path, format='PNG')


def _validate_positive_int(number):
    if not isinstance(number, int) or number <= 0:
        raise ValueError('Expected positive integer, got "{}"'.format(number))


def _generate_bar_positions(width, count=None):
    """
    Generate a list of bar starts and ends.

    Parameters
    ----------
    width : int
        The width of the canvas, in pixels.
    count : :obj:`int` or None
        The target amount of bars to generate.

    Returns
    -------
    :obj:`list` of :obj:`tuple` of :obj:`int`
        A list of pairs ``(x0, x1)`` denoting the starting and ending
        points of bars.
    """
    count_set = count is not None
    count = count or random.randint(1, 20)

    points = []
    point_set = set()
    collisions = 0

    while len(points) <= count * 2 and collisions < 100:
        point = random.randint(0, width)
        if point in point_set:
            collisions += 1
            if collisions >= 100:
                if count_set:
                    logger.warning(
                        "There doesn't seem to be enough space for the chosen "
                        "amount of bars; generating less bars."
                    )
            continue
        bisect.insort(points, point)
        point_set.add(point)

    coordinates = _barify(points)
    return coordinates


def _barify(points):
    """
    Transform a list of points into bar positions.

    Determines which pairs of points will be the bars and which will
    be the background by a coin flip.

    Parameters
    ----------
    points : :obj:`list` of :obj:`int`
        A sorted list of points.

    Returns
    -------
    :obj:`list` of :obj:`tuple` of :obj:`int`
        A list of pairs `(x0, x1)` denoting the starting and ending
        points of bars.
    """
    offset = random.choice((0, 1))
    bars = list(zip(points[offset::2], points[offset+1::2]))
    return bars
