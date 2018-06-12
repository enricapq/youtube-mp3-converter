import time
import logging as log
import os
import threading

from queue import Queue, Empty, Full
from retry import retry

import youtube_dl

from utils import validate_url

#TODO Filter log messages
logger = log.getLogger()

# Maximum number of download at the same time
MAX_URLS =  1
# Number of Threads
POOL_SIZE = 5

# Map status of the Downloader with Status for the GUI
# Status dictionary: the tuple associated to each key represents:
# ("message status bar", "color msg status bar", "hex color Download button", "hex color Cancel button",
#  "status of Download button", "status of Cancel button" )
# TODO Create Class for sharing status, colors and msg (multilanguage) between the GUI and the Downloader
STATUS = {0: (0, "Waiting an URL to download", "#EC576B", "#EC576B", "#EC576B", "active", "active"),
          1: (1, "Download in progress", "#E5E338", "#000000", "#000000", "disabled", "disabled"),
          2: (2, "Download completed",  "#EC576B", "#EC576B", "#EC576B", "active", "active"),
          3: (3, "Reached maximum number of files to download, wait",
              "#E5E338", "#000000", "#000000", "disabled", "disabled"),
          4: (4, "Url not valid", "#FF3B3F", "#FF3B3F", "#FF3B3F", "active", "active"),
          5: (5, "Unknown error", "#E5E338", "#E5E338", "#E5E338", "active", "active"),
          6: (6, "Download failed", "#FC4A1A", "#FC4A1A", "#FC4A1A", "active", "active"),
          7: (7, "All downlads completed", "#E5E338", "#E5E338", "#E5E338", "active", "active")}


class OnDownload():
    def __init__(self):
        self.url = ''
        self.percentageDownloaded = 0


class AppState():
    def __init__(self):
        self.lock = threading.Lock()
        self.status = 0
        self.progress = 0.0

    def update_status(self, status):
        self.lock.acquire()
        try:
            log.debug('Acquired a lock')
            self.status = status
        finally:
            log.debug('Released a lock')
            self.lock.release()

    def get_status(self):
        return STATUS[self.status]


class DownloadManager():

    def __init__(self, path_dir):
        self.path_dir = path_dir
        # TODO adapt to Playlist
        self.queue_urls = Queue(MAX_URLS)
        self.queue_urls_done = Queue(MAX_URLS)
        self.status = AppState()
        # TODO calculate & show progress % --> keep track in AppState
        self.progress_bar = 0

        # Producer add url to the queue
        self.dp = DownloadProducer(self.queue_urls, self.queue_urls_done, self.status)
        self.dp.start()

        # TODO: create POOL of Consumers
        # Instantiate class that converts video continuing check if there are new ones in the queue
        self.dc = DownloadConsumer(self.path_dir, self.queue_urls, self.queue_urls_done,
                                   self.status)
        self.dc.start()
        # TODO return list of urls completed
        #     results = []
        #     while not self.queue_urls_done.empty():
        #         res = self.queue_urls_done.get()
        #         if res is not None:
        #             results.append(res)
        #         else:
        #             logger.error("One of the url has not been downloaded")


    def download_url(self, url):
        """Add the url to the queue of videos to convert"""
        return self.dp.download_url(url)

    def get_status(self):
        return self.status.get_status()

    def validate_url(self, url):
        #TODO verify if possible to use youtube_dl validator
        try:
            validate_url(url)
        except ValueError as e:
            log.error(f"Url {url} not valid")
            self.status.update_status(4)
            raise e
        except Exception as e:
            log.error(f"Error during validation of {url}")
            self.status.update_status(5)
            raise e
        else:
            # stop all downloads
            self.stop_downloads()

    def stop_downloads(self):
        # TODO stop Threads
        # TODO Notify GUI
        pass


# TODO make private
class DownloadConsumer(threading.Thread):

    def __init__(self, path_dir, queue_urls, queue_urls_done, status):
        # FIXME using derived from BaseClass
        self.path_dir = path_dir
        # TODO adapt to Playlist
        self.queue_urls = queue_urls
        self.queue_urls_done = queue_urls_done
        self.status = status
        threading.Thread.__init__(self)

    def run(self):
        while True:
            url = self.queue_urls.get()
            self.convert_to_mp3(url)
            # tell the queue that the processing on the task is complete
            self.queue_urls.task_done()
            log.info(f"Consumed {url}")
            time.sleep(1)

    def convert_to_mp3(self, url):

        log.info(f"Downloading {url}")

        url = 'https://www.youtube.com/watch?v=r_xpgogcNwg'

        options = {'format': 'bestaudio/best',
                   'extractaudio': True,  # only keep the audio
                   'audioformat': "mp3",  # convert to mp3
                   'outtmpl': f'{self.path_dir}/%(title)s.%(ext)s',
                   # 'progress_hooks': [progress_hook],
                   'ignoreerrors': True,  # TO CHECK
                   'noplaylist': True,  # TODO only download single song, not playlist
                   'postprocessors': [{'key': 'FFmpegExtractAudio',
                                       'preferredcodec': 'mp3',
                                       'preferredquality': '3'}],
                   'keepvideo': False
                   #  'no_warnings': True,
                   #  'simulate': True
                   #  'logger': ProgressLogger,
                   #  'logtostderr': True
                   }
        with youtube_dl.YoutubeDL(options) as ydl:
            self.status.update_status(1)
            dl_thread = threading.Thread(target=ydl.download, args=([url],))
            dl_thread.start()

            # TODO add check when the file is already downloaded
            try:
                result = ydl.extract_info(url, download=False)
                log.info(f"Video {result['title']} converted in mp3")
            except Exception as e:
                log.error(f"Error converting Video {result['title']} in mp3: {e}")

        self.status.update_status(2)


class DownloadProducer(threading.Thread):
    """ Producer validate url (recognise if it's a single video or a playlist)
    and add url to the queue
    """
    def __init__(self, queue_urls, queue_urls_done, status):
        self.status = status
        # TODO adapt for Playlist
        self.queue_urls = queue_urls
        self.queue_urls_done = queue_urls_done
        threading.Thread.__init__(self)

    @retry(Full, tries=10, delay=5, jitter=5)
    def download_url(self, url):
        try:
            log.info(f"Add to queue_urls {url}")
            self.queue_urls.put_nowait(url)
            #TODO get urls from queue done
            # try:
            #     self.queue_urls_done.get_nowait()
            # except Empty as e:
            #     # Update msg
            #     self.status = 0
        except Full as e:
            # queue is full, wait that previous download finished
            log.debug("Wait to finish previous download. {e}")
            self.status.update_status(3)
            raise Full
