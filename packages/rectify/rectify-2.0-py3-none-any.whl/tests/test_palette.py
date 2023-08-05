import unittest
from unittest.mock import patch

from rectify import palette


class PaletteTest(unittest.TestCase):
    def test_register_palette(self):
        @palette.palette
        def dummy():
            return (4, 78, 200)
        self.assertTrue('dummy' in palette.palettes)
        self.assertEqual(palette.palettes['dummy'], dummy)

    def test_invalid_palette(self):
        palettes = [
            'bear brown',
            [],
            (79, 170),
        ]
        for p in palettes:
            with self.subTest(palette=p):
                with self.assertRaises(ValueError):
                    palette.pick_color(p)

    @patch('rectify.palette.rgb')
    @patch('rectify.palette.random')
    def test_valid_palette(self, random, rgb):
        palette.pick_color(None)
        self.assertTrue(random.called)

        palettes = [
            'pastel',
            [(167, 204, 252), (9, 58, 178), (230, 120, 10)],
            'white',
            (100, 100, 100),
        ]
        for p in palettes:
            with self.subTest(palette=p):
                palette.pick_color(p)
                self.assertTrue(rgb.called)
                rgb.reset_mock()

    def test_invalid_color_to_rgb(self):
        colors = [
            'unicorn pink',
            '[]',
            'blackish',
            (56, 34),
            [],
            [(1, 2, 3), (40, 50, 60)],
            (35, 70, 800),
            (-5, 67, 23),
        ]
        for color in colors:
            with self.subTest(color=color):
                with self.assertRaises(ValueError):
                    palette.rgb(color)

    def test_valid_color_to_rgb(self):
        colors = [
            ('black', (0, 0, 0)),
            ((89, 34, 10), (89, 34, 10)),
            ('hsl(1,2%,3%)', (8, 8, 7)),
        ]
        for color, expected in colors:
            with self.subTest(color=color):
                self.assertEqual(palette.rgb(color), expected)
