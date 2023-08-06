ffmpeg-thumbnail
================

Very simple ``ffmpeg`` binding to generate thumbnails

- Extract and resize thumbnail with keeping aspect ratio
- Supported video formats: mp4, avi, flv, mov, webm, gif, ogv, 3gp
- Supported image formats: jpg, png, bmp, webp

Requirements:
- Python >= 3.5.x
- ffmpeg binary

tested on:

.. code-block::
    $ ffmpeg -v

    ffmpeg version 3.2.10-1~deb9u1 Copyright (c) 2000-2018 the FFmpeg developers
    built with gcc 6.3.0 (Debian 6.3.0-18) 20170516
    configuration: --prefix=/usr --extra-version='1~deb9u1' --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --enable-gpl --disable-stripping --enable-avresample --enable-avisynth --enable-gnutls --enable-ladspa --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libebur128 --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm --enable-libmp3lame --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvorbis --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx265 --enable-libxvid --enable-libzmq --enable-libzvbi --enable-omx --enable-openal --enable-opengl --enable-sdl2 --enable-libdc1394 --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libopencv --enable-libx264 --enable-shared
    libavutil      55. 34.101 / 55. 34.101
    libavcodec     57. 64.101 / 57. 64.101
    libavformat    57. 56.101 / 57. 56.101
    libavdevice    57.  1.100 / 57.  1.100
    libavfilter     6. 65.100 /  6. 65.100
    libavresample   3.  1.  0 /  3.  1.  0
    libswscale      4.  2.100 /  4.  2.100
    libswresample   2.  3.100 /  2.  3.100
    libpostproc    54.  1.100 / 54.  1.100

