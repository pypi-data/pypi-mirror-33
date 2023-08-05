import unittest
from unittest.mock import Mock, patch

from rectify.main import main
from rectify.palette import palettes


@patch('rectify.main.docopt')
class TestCLI(unittest.TestCase):
    def setUp(self):
        self.args = {
            '--width': None,
            '--height': None,
            '--background': None,
            '--colors': None,
            '--count': None,
            '--show': False,
            '--output': None,
            '--version': False,
            '--help': False,
        }

    @patch('rectify.main.generate')
    def test_valid_width(self, generate, docopt):
        width = [
            '1',
            '345',
            '500',
            '1000',
        ]
        for w in width:
            with self.subTest(w=w):
                self.args['--width'] = w
                docopt.return_value = self.args
                main()
                generate.assert_called_with(width=int(w))

    def test_invalid_width(self, docopt):
        width = [
            '',
            '0',
            '-100',
            'abc',
            '84i',
            '(1,2)',
            '{67}',
        ]
        for w in width:
            with self.subTest(w=w):
                self.args['--width'] = w
                docopt.return_value = self.args
                with self.assertRaises(SystemExit):
                    main()

    @patch('rectify.main.generate')
    def test_valid_height(self, generate, docopt):
        height = [
            '1',
            '345',
            '500',
            '1000',
        ]
        for h in height:
            with self.subTest(h=h):
                self.args['--height'] = h
                docopt.return_value = self.args
                main()
                generate.assert_called_with(height=int(h))

    def test_invalid_height(self, docopt):
        height = [
            '',
            '0',
            '-100',
            'abc',
            '84i',
            '(1,2)',
            '{67}',
        ]
        for h in height:
            with self.subTest(h=h):
                self.args['--height'] = h
                docopt.return_value = self.args
                with self.assertRaises(SystemExit):
                    main()

    @patch('rectify.main.generate')
    def test_valid_background(self, generate, docopt):
        palette = [
            ('black', palettes['black']),
            ('(56, 78, 89)', (56, 78, 89)),
            ('[(200, 67, 23), (1, 1, 1), (48, 98, 34)]',
              [(200, 67, 23), (1, 1, 1), (48, 98, 34)]),
            ('(56,78,89)', (56, 78, 89)),
            ('[(200,67,23), (1,1,1,),]', [(200, 67, 23), (1, 1, 1)]),
        ]
        for p, result in palette:
            with self.subTest(p):
                self.args['--background'] = p
                docopt.return_value = self.args
                main()
                generate.assert_called_with(background=result)

    def test_invalid_background(self, docopt):
        palette = [
            'nonexistent',
            '(1, 2)',
            '[]',
            'neon pastel',
            '456',
            '[(1,)]',
        ]
        for p in palette:
            with self.subTest(p=p):
                self.args['--background'] = p
                docopt.return_value = self.args
                with self.assertRaises(SystemExit):
                    main()

    @patch('rectify.main.generate')
    def test_valid_colors(self, generate, docopt):
        palette = [
            ('black', palettes['black']),
            ('(56, 78, 89)', (56, 78, 89)),
            ('[(200, 67, 23), (1, 1, 1), (48, 98, 34)]',
              [(200, 67, 23), (1, 1, 1), (48, 98, 34)]),
            ('(56,78,89)', (56, 78, 89)),
            ('[(200,67,23), (1,1,1,),]', [(200, 67, 23), (1, 1, 1)]),
        ]
        for p, result in palette:
            with self.subTest(p):
                self.args['--colors'] = p
                docopt.return_value = self.args
                main()
                generate.assert_called_with(colors=result)

    def test_invalid_colors(self, docopt):
        palette = [
            'nonexistent',
            '(1, 2)',
            '[]',
            'black white',
            '456',
            '[(1,)]',
        ]
        for p in palette:
            with self.subTest(p=p):
                self.args['--colors'] = p
                docopt.return_value = self.args
                with self.assertRaises(SystemExit):
                    main()

    @patch('rectify.main.generate')
    def test_valid_count(self, generate, docopt):
        count = [
            '1',
            '345',
            '500',
            '1000',
        ]
        for c in count:
            with self.subTest(c=c):
                self.args['--count'] = c
                docopt.return_value = self.args
                main()
                generate.assert_called_with(count=int(c))

    def test_invalid_count(self, docopt):
        count = [
            '',
            '0',
            '-100',
            'abc',
            '84i',
            '(1,2)',
            '{67}',
        ]
        for c in count:
            with self.subTest(c=c):
                self.args['--count'] = c
                docopt.return_value = self.args
                with self.assertRaises(SystemExit):
                    main()

    @patch('rectify.main.generate')
    def test_show(self, generate, docopt):
        self.args['--show'] = True
        docopt.return_value = self.args
        main()
        generate.return_value.show.assert_called_with()

    @patch('rectify.main.generate')
    def test_no_show(self, generate, docopt):
        docopt.return_value = self.args
        main()
        generate.return_value.show.assert_not_called()

    @patch('rectify.main.save')
    def test_path(self, save, docopt):
        self.args['--output'] = 'path/to/file'
        docopt.return_value = self.args
        main()
        self.assertEqual(self.args['--output'], save.call_args[0][1])

    @patch('rectify.main.save')
    def test_no_path(self, save, docopt):
        docopt.return_value = self.args
        main()
        save.assert_not_called()
