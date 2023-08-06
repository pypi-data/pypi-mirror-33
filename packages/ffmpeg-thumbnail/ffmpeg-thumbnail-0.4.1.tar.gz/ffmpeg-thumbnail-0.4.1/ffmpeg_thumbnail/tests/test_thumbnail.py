import unittest

from tempfile import TemporaryDirectory
from os.path import join, abspath, dirname, exists
from ffmpeg_thumbnail import FFMPEGThumbnail, FFMPEGDirectInput, FFMPEGDirectOutput


class ThumbnailTestCase(unittest.TestCase):
    this_dir = abspath(join(dirname(__file__), '.'))
    tests_dir = this_dir
    stuff_dir = join(this_dir, 'stuff')

    def test_thumbnail(self):
        def generate_thumbnail(filename, width_=200, height_=None):
            t = FFMPEGThumbnail(
                input_=FFMPEGDirectInput(join(self.stuff_dir, filename)),
                output=FFMPEGDirectOutput(tmp_dir, extension='.jpg'),
                width=width_,
                height=height_
            )
            t.run()
            return True

        with TemporaryDirectory() as tmp_dir:
            for width, height in ((200, None), (200, 200)):
                self.assertTrue(exists(generate_thumbnail('img1.jpg', width, height)))
                self.assertTrue(exists(generate_thumbnail('img1.jpg', width, height)))
                self.assertTrue(exists(generate_thumbnail('img1_1x1.jpg', width, height)))
                self.assertTrue(exists(generate_thumbnail('img1_1x150.jpg', width, height)))
                self.assertTrue(exists(generate_thumbnail('img1_50x50.jpg', width, height)))
                self.assertTrue(exists(generate_thumbnail('img1_150x5.jpg', width, height)))
                self.assertTrue(exists(generate_thumbnail('img2.gif', width, height)))
                self.assertTrue(exists(generate_thumbnail('img3.webp', width, height)))
                self.assertTrue(exists(generate_thumbnail('img4.png', width, height)))
                self.assertTrue(exists(generate_thumbnail('img5.bmp', width, height)))
                self.assertTrue(exists(generate_thumbnail('video1.mp4', width, height)))
                self.assertTrue(exists(generate_thumbnail('video2.ogv', width, height)))
                self.assertTrue(exists(generate_thumbnail('video3.webm', width, height)))
                self.assertTrue(exists(generate_thumbnail('video4.flv', width, height)))
                self.assertTrue(exists(generate_thumbnail('video5.3gp', width, height)))
                self.assertTrue(exists(generate_thumbnail('song1.mp3', width, height)))

            # Song with no album art
            with self.assertRaises(RuntimeError):
                self.assertTrue(exists(generate_thumbnail('song2.mp3')))

            # Not existence input
            with self.assertRaises(RuntimeError):
                self.assertTrue(exists(generate_thumbnail('hell.js')))

            # Just accept Width or Height (except squares)
            with self.assertRaises(AssertionError):
                FFMPEGThumbnail(
                    input_=FFMPEGDirectInput(join(self.stuff_dir, 'img1.jpg')),
                    output=FFMPEGDirectOutput(tmp_dir, extension='.jpg'),
                    width=250,
                    height=251)

            # Check Width or Height
            with self.assertRaises(AssertionError):
                FFMPEGThumbnail(
                    input_=FFMPEGDirectInput(join(self.stuff_dir, 'img1.jpg')),
                    output=FFMPEGDirectOutput(tmp_dir, extension='.jpg'),
                    width=None,
                    height=None)


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
