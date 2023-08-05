import unittest
from unittest.mock import Mock, call, patch

from rectify import image


class ImageTest(unittest.TestCase):
    def test_invalid_numeric_input(self):
        arg_list = [
            {'width': -100},
            {'width': 0},
            {'width': 107.4},
            {'height': -1},
            {'height': 0},
            {'height': 9.3},
            {'count': 0},
            {'count': -20},
            {'count': 10.4},
        ]
        for kwargs in arg_list:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    image.generate(**kwargs)

    def test_invalid_palette_input(self):
        arg_list = [
            {'background': 'neony'},
            {'background': []},
            {'background': 78},
            {'background': 90.2},
            {'colors': 'neony'},
            {'colors': []},
            {'colors': 78},
            {'colors': 90.2},
        ]
        for kwargs in arg_list:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    image.generate(**kwargs)

    @patch('rectify.image.ImageDraw')
    @patch('rectify.image._generate_bar_positions')
    def test_generate(self, generate_bar_positions, imagedraw):
        width = 500
        height = 600
        background = (110, 140, 170)
        colors = (1, 2, 3)
        positions = [(2, 5), (80, 180), (181, 200)]
        generate_bar_positions.return_value = positions

        pic = image.generate(width, height, background, colors)

        self.assertEqual(pic.width, width)
        self.assertEqual(pic.height, height)
        imagedraw.Draw.return_value.rectangle.assert_has_calls([
            call([2, 0, 5, height], fill=(1, 2, 3)),
            call([80, 0, 180, height], fill=(1, 2, 3)),
            call([181, 0, 200, height], fill=(1, 2, 3)),
        ])

    def test_save(self):
        paths = [
            ('a/b/c', 'a/b/c.png'),
            ('a/b/c.png', 'a/b/c.png'),
            ('tests', 'tests/rectify-image.png'),
        ]
        pic = Mock()
        for path, expected in paths:
            image.save(pic, path)
            pic.save.assert_called_with(expected, format='PNG')

    @patch('rectify.image.logger')
    def test_bar_positions(self, _):
        widths = (1, 12, 103, 507)
        counts = (1, 12, 103, 507)
        for width in widths:
            for count in counts:
                with self.subTest(width=width, count=count):
                    points = image._generate_bar_positions(width, count)

                    # In bounds
                    self.assertTrue(all(
                        0 <= x1 <= width and 0 <= x2 <= width
                        for x1, x2 in points
                    ))

                    # Sorted
                    self.assertTrue(all(
                        points[i][0] < points[i][1] < points[i + 1][0]
                        < points[i + 1][1]
                        for i in range(len(points) - 1))
                    )

                    # Bar count based on count, if possible
                    if count * 2 < width:
                        self.assertEqual(len(points), count)

    @patch('rectify.image.random')
    def test_barification(self, random):
        input_ = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        expected = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
        random.choice.return_value = 0
        self.assertEqual(image._barify(input_), expected)

        expected = [(2, 3), (4, 5), (6, 7), (8, 9)]
        random.choice.return_value = 1
        self.assertEqual(image._barify(input_), expected)
