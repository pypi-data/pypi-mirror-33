import ast
import os.path
import sys

from docopt import docopt

from rectify import __tagline__, __version__
from rectify.image import generate, save
from rectify.palette import palettes, pick_color


MESSAGE = """rectify: {tagline}

The background color and the colors of the bars generated are customizable via
palettes. For the purposes of this command line interface, a PALETTE is either
a color or a list of colors, where a color is a triple (R, G, B) with 0 <= R,
G, B <= 255. So, for instance, '(0, 0, 0)' is a palette containing only black,
while '[(255, 0, 0), (0, 255, 0), (0, 0, 255)]' is a palette consisting of pure
red, green and blue. Alternatively, the following keywords can be used for
accessing built-in palettes:
- {palette_list}

Usage:
  rectify [-x WIDTH | --width WIDTH]
          [-y HEIGHT | --height HEIGHT]
          [-b PALETTE | --background PALETTE]
          [-c PALETTE | --colors PALETTE]
          [-i COUNT | --count COUNT]
          [-s | --show]
          [-o PATH | --output PATH]
  rectify (-h | --help)
  rectify --version

Options:
  -x WIDTH, --width WIDTH           Width of the generated image (pixels).      
  -y HEIGHT, --height HEIGHT        Height of the generated image (pixels).
  -b PALETTE, --background PALETTE  Palette to take the background color from.
  -c PALETTE, --colors PALETTE      Palette to take the bar colors from.
  -i COUNT, --count COUNT           Approximate amount of bars to generate.
  -s --show                         Show the generated image.
  -o PATH, --output PATH            Where to save the generated image.
  -h --help                         Show this help.
  --version                         Show the version of rectify in use.
""".format(
    tagline = __tagline__,
    palette_list='\n- '.join(palettes.keys()), version=__version__
)


def _parse_palette(palette):
    try:
        return palettes[palette]
    except KeyError:
        pass

    try:
        literal = ast.literal_eval(palette)
        pick_color(literal)
        return literal
    except (SyntaxError, ValueError):
        pass

    sys.exit('Unsupported palette "{}". See --help for more information.'
             .format(palette))


def _validate_positive_int(number):
    try:
        number = int(number)
        if number <= 0:
            raise ValueError
    except ValueError:
        sys.exit('Positive integer required, got "{}".'.format(number))
    return number


def main():
    args = docopt(MESSAGE, version=__version__)
    kwargs = {}

    # Dimensions
    if args['--width'] is not None:
        kwargs['width'] = _validate_positive_int(args['--width'])

    if args['--height'] is not None:
        kwargs['height'] = _validate_positive_int(args['--height'])

    # Set up palettes
    background = args['--background']
    if background is not None:
        background = _parse_palette(background)
        kwargs['background'] = background

    colors = args['--colors']
    if colors is not None:
        colors = _parse_palette(colors)
        kwargs['colors'] = colors

    # Customization
    if args['--count'] is not None:
        kwargs['count'] = _validate_positive_int(args['--count'])

    # Output
    show = args['--show']
    path = args['--output']

    # Generate
    image = generate(**kwargs)

    if path is not None:
        save(image, path)

    if show:
        image.show()
