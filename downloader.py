import youtube_dl as ydl

# Only one url at the moment
MAX_URLS =  1
STATUS = {0: "Waiting an URL to download",
          1: "Download in progress",
          2: "Download completed",
          3: "Reached maximum number of files to download"}


# TODO use Threads and Queue

class Downloader():

    def __init__(self):
        # TODO adapt for Playlist
        self.urls = []
        self.status = 0
        # TODO calculate & show progress %
        self.progress_bar = 0

    def add_url(self, url):
        if len(self.urls) < MAX_URLS:
            self.urls.append(url)
            self.status = 1
        else:
            self.status = 3

    def convert_to_mp3(self):
        # TODO
        completed = True
        if completed and self.urls:
            self.status = 1

    def get_status(self):
        return STATUS[self.status]

    def reset_status(self):
        self.status = 0
