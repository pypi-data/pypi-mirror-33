

class FFMPEGThumbnailCommand:

    def __init__(self, input_path: str, output_path: str, ffmpeg_bin_path: str = '/usr/bin/ffmpeg'):
        self.output_path = output_path
        self.command = [
            ffmpeg_bin_path,
            '-i', input_path,
            '-y',
            '-an'
        ]

    def generate_video(self, width: int, height: int=None):
        command = self.command.copy()
        command.extend([
            '-ss', '1',
            '-f', 'rawvideo',
            '-vframes', '1',
            '-vcodec', 'mjpeg',
            '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height),
            self.output_path
        ])
        return command

    def generate_mp3_album(self, width: int, height: int=None):
        command = self.command.copy()
        command.extend([
            '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height),
            self.output_path
        ])
        return command

    def generate_photo(self, width: int, height: int = None):
        command = self.command.copy()
        command.extend([
            '-filter', 'scale=%s:%s' % (width, '-1') if width is not None else ('-1', height),
            self.output_path
        ])
        return command
