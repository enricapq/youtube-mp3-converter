import os
import threading

import youtube_dl


# Only one url at the moment
MAX_URLS =  1
STATUS = {0: "Waiting an URL to download",
          1: "Download in progress",
          2: "Download completed",
          3: "Reached maximum number of files to download"}
PATH = "/"

# TODO use Threads and Queue

class Downloader():

    def __init__(self):
        # TODO adapt for Playlist
        self.urls = []
        self.status = 0
        # TODO calculate & show progress %
        self.progress_bar = 0

    def create_dir(self):
        # create directory
        savedir = ""
        if not os.path.exists(savedir):
            os.makedirs(savedir)

    def add_url(self, url):
        if len(self.urls) < MAX_URLS:
            self.urls.append(url)
            self.status = 1
            self.convert_to_mp3(url)
        else:
            self.status = 3

    def convert_to_mp3(self, url):

        options = {'format': 'bestaudio/best',
                   'extractaudio': True,  # only keep the audio
                   'audioformat': "mp3",  # convert to mp3
                   'outtmpl': '%(id)s',  # name the file the ID of the video
                   'noplaylist': True  # only download single song, not playlist
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            dl_thread = threading.Thread(target=ydl.download, args=(['https://www.youtube.com/watch?v='],))
            dl_thread.start()

        completed = True
        if completed and self.urls:
            self.status = 1

    def get_status(self):
        return STATUS[self.status]

    def reset_status(self):
        self.status = 0
