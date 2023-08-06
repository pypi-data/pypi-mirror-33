from os.path import splitext, join

from subprocess import run, DEVNULL

from hashlib import md5

from .command import FFMPEGThumbnailCommand
from .constants import video_extensions


class FFMPEGThumbnail:
    __prefix__ = 'thumbnail-'
    __ffmpeg_bin__ = '/usr/bin/ffmpeg'
    debug = False

    @staticmethod
    def assert_width_and_height(width, height):
        if width is None and height is None:
            raise AssertionError('Define width and height')

        if width is not None and height is not None and width != height:
            raise AssertionError('Set width or height to keep aspect ratio or equal value to square cropping')

    @staticmethod
    def assert_output_extension(output_extension):
        supported_extensions = ('.jpg', '.png', '.webp')
        if output_extension not in supported_extensions:
            raise AssertionError(
                '(%s) extensions are supported you have entered %s' % (
                    ','.join(supported_extensions), output_extension
                )
            )

    def __init__(self, path, output_base_path, width: int = None, height: int = None,
                 output_extension: str= '.jpg', debug: bool = False):
        self.assert_width_and_height(width, height)
        self.assert_output_extension(output_extension)
        self.path = path
        self.output_base_path = output_base_path
        self.width = width
        self.height = height
        self.input_extension = splitext(self.path)[1]
        self.output_extension = output_extension
        self.debug = debug

    @property
    def key(self):
        return '%s-%s-%s' % (self.width, self.height, self.path)

    def __hash__(self):
        return md5(self.key.encode('utf8')).hexdigest()

    def get_output_filename(self):
        return '%s%s%s' % (self.__prefix__, self.__hash__(), self.output_extension)

    def get_output_path(self):
        return join(self.output_base_path, self.get_output_filename())

    def save(self):
        output_path = self.get_output_path()
        command = FFMPEGThumbnailCommand(
            input_path=self.path,
            output_path=output_path,
            ffmpeg_bin_path=self.__ffmpeg_bin__
        )

        if self.input_extension == '.mp3':
            command = command.generate_mp3_album(
                width=self.width,
                height=self.height
            )

        elif self.input_extension in video_extensions :
            command = command.generate_video(
                width=self.width,
                height=self.height
            )

        else:
            command = command.generate_photo(
                width=self.width,
                height=self.height
            )

        if run(
            command,
            stdout=None if self.debug else DEVNULL,
            stderr=None if self.debug else DEVNULL
        ).returncode != 0:
            raise RuntimeError('FFMPEG failure')

        return output_path
