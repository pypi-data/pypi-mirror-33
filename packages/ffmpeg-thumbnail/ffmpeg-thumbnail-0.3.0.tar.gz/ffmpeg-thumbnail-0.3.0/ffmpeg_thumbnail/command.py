from os.path import splitext


class FFMPEGThumbnailCommand:

    def __init__(self, input_path: str, output_path: str, ffmpeg_bin_path: str = '/usr/bin/ffmpeg'):
        self.output_path = output_path
        self.extension = splitext(self.output_path)[1]
        self.command = [
            ffmpeg_bin_path,
            '-i', input_path,
            '-y',
            '-an'
        ]

        if self.extension == '.png':
            self.command.extend([
                '-vcodec', 'png',
                '-pix_fmt', 'rgba',
            ])

        elif self.extension in ('.jpg', '.jpeg'):
            self.command.extend([
                '-vcodec', 'mjpeg'
            ])

        elif self.extension in ('.webp'):
            self.command.extend([
                '-vcodec', 'libwebp',
                '-lossless', '1',
                '-q:60'
            ])

    def generate_video(self, width: int, height: int):
        command = self.command.copy()
        command.extend([
            '-ss', '1',
            '-f', 'rawvideo',
            '-vframes', '1',
            '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height),
            self.output_path
        ])
        return command

    def generate_mp3_album(self, width: int, height: int):
        command = self.command.copy()
        if width == height:
            command.extend([
                '-vf', 'scale=\'if(gt(iw,ih),-1,%(width)s):if(gt(iw,ih),'
                       '%(height)s,-1)\', crop=%(width)s:%(height)s' % dict(
                            width=width, height=height
                        ),
                self.output_path
            ])
        else:
            command.extend([
                '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height),
                self.output_path
            ])
        return command

    def generate_photo(self, width: int, height: int):
        command = self.command.copy()
        if width == height:
            command.extend([
                '-vf', 'scale=\'if(gt(iw,ih),-1,%(width)s):if(gt(iw,ih),'
                       '%(height)s,-1)\', crop=%(width)s:%(height)s' % dict(
                            width=width, height=height
                        ),
                self.output_path
            ])
        else:
            command.extend([
                '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height),
                self.output_path
            ])
        return command
