import unittest

from tempfile import TemporaryDirectory
from os.path import join, abspath, dirname, exists
from ffmpeg_thumbnail import FFMPEGThumbnail


class ThumbnailTestCase(unittest.TestCase):
    this_dir = abspath(join(dirname(__file__), '.'))
    tests_dir = this_dir
    stuff_dir = join(this_dir, 'stuff')

    def test_thumbnail(self):
        def generate_thumbnail(filename):
            return FFMPEGThumbnail(
                path=join(self.stuff_dir, filename),
                output_base_path=tmp_dir,
                width=200
            ).save()

        with TemporaryDirectory() as tmp_dir:
            self.assertTrue(exists(generate_thumbnail('img1.jpg')))
            self.assertTrue(exists(generate_thumbnail('img2.gif')))
            self.assertTrue(exists(generate_thumbnail('img3.webp')))
            self.assertTrue(exists(generate_thumbnail('img4.png')))
            self.assertTrue(exists(generate_thumbnail('img5.bmp')))
            self.assertTrue(exists(generate_thumbnail('video1.mp4')))
            self.assertTrue(exists(generate_thumbnail('video2.ogv')))
            self.assertTrue(exists(generate_thumbnail('video3.webm')))
            self.assertTrue(exists(generate_thumbnail('video4.flv')))
            self.assertTrue(exists(generate_thumbnail('video5.3gp')))
            self.assertTrue(exists(generate_thumbnail('song1.mp3')))

            # Song with no album art
            with self.assertRaises(RuntimeError):
                self.assertTrue(exists(generate_thumbnail('song2.mp3')))

            # Not existence input
            with self.assertRaises(RuntimeError):
                self.assertTrue(exists(generate_thumbnail('hell.js')))

            # Currently crop not supported just accept Width or Height
            with self.assertRaises(AssertionError):
                FFMPEGThumbnail(
                    path=join(self.stuff_dir, 'img1.jpg'),
                    output_base_path=tmp_dir,
                    width=250,
                    height=250)

            # Check Width or Height
            with self.assertRaises(AssertionError):
                FFMPEGThumbnail(
                    path=join(self.stuff_dir, 'img1.jpg'),
                    output_base_path=tmp_dir,
                    width=None,
                    height=None)


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
