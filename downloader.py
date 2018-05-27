import logging as log
import os
import threading

from queue import Queue, Empty, Full
from threading import Thread

import youtube_dl

from utils import validate_url

#FIXME Filter log messages
logger = log.getLogger()
log.raiseExceptions = False
# Prevents debug-level messages from download
log.getLogger("youtube_dl").setLevel("INFO")


# Only one url at the moment
MAX_URLS =  1
STATUS = {0: "Waiting an URL to download",
          1: "Download in progress",
          2: "Download completed",
          3: "Reached maximum number of files to download",
          4: "Url not valid",
          5: "Unknown error",
          6: "Download failed",
          7: "All downlads completed"}


class Downloader():

    def __init__(self, path_dir):
        self.path_dir = path_dir
        # TODO adapt to Playlist
        self.urls = Queue(MAX_URLS)
        self.status = 0
        # TODO calculate & show progress %
        self.progress_bar = 0

    def download_url(self, url):
        try:
            self.urls.put_nowait(url)
            #FIXME continue converting until empty. Start the converter and feed it
            # try:
            #     self.urls.get_nowait()
            # except Empty:
            #     # Update msg
            #     self.status = 0
            self.convert_to_mp3()
        except Full as e:
            log.info("Wait to finish previous download.")
            self.status = 3
            return e

    def convert_to_mp3(self):

        url = self.urls.get_nowait()

        log.info(f"Downloading {url}")

        url = 'https://www.youtube.com/watch?v=r_xpgogcNwg'

        options = {'format': 'bestaudio/best',
                   'extractaudio': True,  # only keep the audio
                   'audioformat': "mp3",  # convert to mp3
                   'outtmpl': f'{self.path_dir}/%(title)s.%(ext)s',
                  # 'progress_hooks': [progress_hook],
                   'ignoreerrors': True,  # TO CHECK
                   'noplaylist': True,  #TODO only download single song, not playlist
                   'postprocessors': [{'key': 'FFmpegExtractAudio',
                                       'preferredcodec': 'mp3',
                                       'preferredquality': '3'}],
                   'keepvideo': True
                 #  'no_warnings': True,
                 #  'simulate': True
                 #  'logger': ProgressLogger,
                 #  'logtostderr': True
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            self.status = 1
            dl_thread = threading.Thread(target=ydl.download, args=([url],))
            dl_thread.start()

            # TODO add check when the file is already downloaded
            try:
                result = ydl.extract_info(url, download=False)
                log.info(f"Video {result['title']} converted in mp3")
            except Exception as e:
                log.error(f"Error converting Video {result['title']} in mp3: {e}")

        self.status = 2

    def get_status(self):
        return STATUS[self.status]

    def validate_url(self, url):
        #TODO verify if possible use youtube_dl validator
        try:
            validate_url(url)
        except ValueError as e:
            log.error(f"Url {url} not valid")
            self.status = 4
            raise e
        except Exception as e:
            log.error(f"Error during validation of {url}")
            self.status = 5
            raise e
        else:
            # stop all downloads
            self.stop_downloads()

    def stop_downloads(self):
        pass


# class ProgressLogger():
#     def __init__(self, parent):
#         Text.__init__(self, parent)
#         self.parent = parent
#
#     def log(self, info):
#         if '_percent_str' in info:
#             progress = info['_percent_str']
#         else:
#             progress = '100.0%'
#         filename = info['filename'].split(os.sep)[-1]
#         self.insert('1.0', "{:s} for {:s} \n".format(progress, filename))