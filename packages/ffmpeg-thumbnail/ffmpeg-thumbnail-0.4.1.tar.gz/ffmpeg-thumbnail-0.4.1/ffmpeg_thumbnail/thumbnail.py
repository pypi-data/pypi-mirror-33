from os.path import splitext, join

from hashlib import md5

from subprocess import run, DEVNULL, PIPE
from .constants import video_extensions, thumbnail_extensions

from io import BytesIO


class FFMPEGInput:
    input_ = None
    extension = None

    @property
    def key(self):  # pragma:nocover
        pass


class FFMPEGDirectInput(FFMPEGInput):

    def __init__(self, input_: str):
        self.input_ = input_
        self.extension = splitext(input_)

    @property
    def key(self):
        return md5(self.input_.encode()).hexdigest()


class FFMPEGOutput:
    output = None
    extension = None


class FFMPEGDirectOutput(FFMPEGOutput):

    def __init__(self, output: str, extension: str='.jpg'):
        self.output = output
        self.extension = extension


class FFMPEGFileOutput(FFMPEGOutput):

    def __init__(self, output: BytesIO, extension: str):
        self.output = output
        self.extension = extension


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

    def __init__(self, input_: FFMPEGInput, output: FFMPEGOutput,
                 width: int = None, height: int = None, debug: bool = False):
        self.assert_width_and_height(width, height)
        self.input_ = input_
        self.output = output
        self.width = width
        self.height = height
        self.debug = debug

        self.command = (self.__ffmpeg_bin__, )

        if isinstance(input_, FFMPEGDirectInput):
            self.command += ('-i', input_.input_)

        self.command += (
            '-y',  # Accept output overwriting
            '-an'  # Escape audio
        )

        # Recognize input file type
        if self.input_.extension == '.mp3':
            self.set_mp3_album_art(
                width=self.width,
                height=self.height
            )

        elif self.input_.extension in video_extensions:
            self.set_video(
                width=self.width,
                height=self.height
            )

        else:
            self.set_photo(
                width=self.width,
                height=self.height
            )

        if self.output.extension == '.png':
            self.command += (
                '-vcodec', 'png',
                '-pix_fmt', 'rgba'
            )

        elif self.output.extension in ('.jpg', '.jpeg'):
            self.command += (
                '-vcodec', 'mjpeg',
            )

        elif self.output.extension == '.webp':
            self.command += (
                '-vcodec', 'libwebp',
                '-lossless', '1',
            )

        else:
            raise ValueError(
                '(%s) extensions are supported you have entered %s' % (
                    ','.join(thumbnail_extensions), self.output.extension
                )
            )

        self.command += (
            '-f', 'image2pipe'
        )

    @property
    def key(self):
        return (
            'x'.join((
                str(self.width) if self.width else '',
                str(self.height) if self.height else ''
            )),
            self.input_.key
        )

    def __hash__(self):
        return hash(self.key)

    def get_output_filename(self):
        return '%s%s%s' % (self.__prefix__, '-'.join(self.key), self.output.extension)

    def get_output_path(self, base_path):
        return join(base_path, self.get_output_filename())

    @staticmethod
    def _get_filter(width, height):
        if width == height:
            return (
                '-vf', 'scale=\'if(gt(iw,ih),-1,%(width)s):if(gt(iw,ih),'
                       '%(height)s,-1)\', crop=%(width)s:%(height)s' % dict(
                            width=width, height=height
                        )
            )
        else:
            return (
                '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height)
            )

    def set_video(self, width: int, height: int):
        self.command += (
            '-ss', '1',
            '-f', 'rawvideo',
            '-vframes', '1',
        ) + self._get_filter(width, height)

    def set_mp3_album_art(self, width: int, height: int):
        self.command += self._get_filter(width, height)

    def set_photo(self, width: int, height: int):
        self.command += self._get_filter(width, height)

    def run(self):

        if isinstance(self.output, FFMPEGDirectOutput):
            self.command += (self.get_output_path(self.output.output),)

        else:
            self.command += ('pipe:1', )

        p = run(
            self.command,
            stdout=PIPE,
            stderr=None if self.debug else DEVNULL
        )

        if p.returncode != 0:
            raise RuntimeError('FFMPEG failure')

        if isinstance(self.output, FFMPEGFileOutput):
            self.output.output.write(p.stdout)
            self.output.output.seek(0)
