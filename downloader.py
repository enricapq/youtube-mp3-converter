import time
import logging as log
import os
import threading

from queue import Queue, Empty, Full

import youtube_dl

from utils import validate_url

#FIXME Filter log messages
logger = log.getLogger()
log.raiseExceptions = False
# Prevents debug-level messages from download
log.getLogger("youtube_dl").setLevel("INFO")

MAX_URLS =  10
POOL_SIZE = 5
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
        self.queue_urls = Queue(MAX_URLS)
        self.queue_urls_done = Queue(MAX_URLS)
        self.status = 0
        # TODO calculate & show progress %
        self.progress_bar = 0
        # Instantiate class that converts video continuing check if there are new ones in the queue
        DownloaderConsumer(self.path_dir, self.queue_urls, self.queue_urls_done).start()

    # TODO not working code but implement POOL and retry like this
    # def run(self):
    #
    #     def work():
    #         t = threading.current_thread()
    #         logger.info("Thread {} started".format(t.name))
    #
    #         url_done = None
    #         while True:
    #             try:
    #                 current_url = self.queue_urls.get(block=True, timeout=1)
    #                 log.info(f"Current url {current_url} to download")
    #             except Empty:
    #                 continue
    #
    #             try:
    #                 # download here
    #                 log.info(f"Downloading current_url {current_url}...")
    #                 url_done = current_url
    #             except Exception as e:
    #                 #TODO implement retry
    #                 logger.error(f"Download failed after 3 retries because of: {2}")
    #
    #             self.queue_urls_done.put(url_done)
    #             self.queue_urls.task_done()
    #
    #         logger.info(f"Thread {t.name} finished")
    #
    #     logger.info("Starting {} threads to convert videos".format(POOL_SIZE))
    #     for i in range(POOL_SIZE):
    #         t = Thread(target=work)
    #         t.daemon = True
    #         t.start()
    #
    #     self.queue_urls.join()
    #
    #     logger.info("All urls have been processed")
    #
    #     results = []
    #     while not self.queue_urls_done.empty():
    #         res = self.queue_urls_done.get()
    #         if res is not None:
    #             results.append(res)
    #         else:
    #             logger.error("One of the url has not been downloaded")


    def download_url(self, url):
        try:
            log.info(f"Addin to the queue_urls {url}")
            #FIXME remove, only for testing
            for i in range(5):
                self.queue_urls.put_nowait(url)
            #TODO get urls from queue done
            # try:
            #     self.queue_urls_done.get_nowait()
            # except Empty:
            #     # Update msg
            #     self.status = 0
        except Full as e:
            log.info("Wait to finish previous download.")
            self.status = 3
            return e

    def get_status(self):
        return STATUS[self.status]

    def validate_url(self, url):
        #TODO verify if possible to use youtube_dl validator
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
        # TODO stop Threads
        # TODO Notify GUI
        pass


class DownloaderConsumer(threading.Thread, Downloader):

    def __init__(self, path_dir, queue_urls, queue_urls_done):
        #FIXME using derived from BaseClass
        self.path_dir = path_dir
        # TODO adapt to Playlist
        self.queue_urls = queue_urls
        self.queue_urls_done = queue_urls_done
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

        # FIXME update status
        self.status = 2

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
