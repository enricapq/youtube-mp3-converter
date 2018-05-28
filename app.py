import logging as log
from queue import Full # Queue,

from appJar import gui

from downloader import Downloader
from utils import create_dir, get_download_path


class App():

    def __init__(self):
        self.app = gui("Insert Youtube url", "500x100")
        self.app.setResizable(canResize=True)
    #    self.app.setOnTop(stay=True)
        self.app.startFrame("LEFT", row=0, column=0)
        self.app.addLabel("url_label", "url:", 0, 0)
        self.app.addValidationEntry("url_value", 0, 1)
        self.app.setEntryMaxLength("url_value", 64)
        self.app.setEntryDefault("url_value", "https://www.youtube.com/...")
        self.app.addButtons(["Download", "Cancel"], self.press, 2, 0, 2)
        self.app.save_dir = self.get_save_dir()
        self.dl = self.create_downloader()
        self.app.go()

        #TODO Add button to select where store files
        # Button to browse for location
        #from TK b_folder_choose = Button(self, text="Choose output directory",
        # command=self.ask_directory)
        # b_folder_choose.place(x=150, y=90)

    def get_save_dir(self):
        # Return default user's download path for Linux, macOS or Windows
        return get_download_path()
        #If Add button to select directory
        #TODO Add button to select where store files
        # savedir = "pathdir_where_storing_files"
        # try:
        #     create_dir(savedir)
        # except Exception as e:
        #     log.error(f"Error {e}")
        #     self.stop_app()

    def stop_app(self):
        log.info("app stopped")
        self.app.stop()
        #TODO stop all downloads, kill threads
        # self.dl.stop_downloads(self)

    def create_downloader(self):
        # Instantiate class that takes care of downloading videos
        dl = Downloader(self.app.save_dir)
        self.app.addStatusbar(fields=1)
        self.app.setStatusbar(dl.get_status(), 0)
        return dl

    def clear_entry(self):
        self.app.clearEntry("url_value", callFunction=False)

    def press(self, btnName):
        if btnName == "Cancel":
            self.clear_entry()
        # Download button pressed
        url = 'https://www.youtube.com/watch?v=r_xpgogcNwg' #self.app.getEntry("url_value").strip()
        try:
            self.dl.validate_url(url)
            self.app.setValidationEntry("url_value", state="valid")
            self.app.queueFunction(self.app.setStatusbar, self.dl.get_status(), 0)
            # Download completed
         #   import pdb; pdb.set_trace()
            self.app.threadCallback(self.download_url, self.download_completed, url)
        except ValueError:
            self.app.queueFunction(self.app.setValidationEntry, "url_value", state="invalid")
            self.app.queueFunction(self.app.setStatusbar, self.dl.get_status())
            self.app.setStatusbarBg("red", 0)
        except Exception as e:
            # Something wrong happened
            self.stop_app()

    def download_completed(self, url):
        # TODO re-enable Download button
        log.info(f"Download of {url} completed!!")
        self.app.queueFunction(self.app.setStatusbar, self.dl.get_status(), 0)
        self.clear_entry()

    def download_url(self, url):
        try:
            self.dl.download_url(url)
        # TODO implement retry in case the queue will have space
            return url
        except Exception as e:
            if isinstance(e, Full):
                import time;
                time.sleep(2)
            #TODO block Add button

        # TODO adapt to Playlist and multiple files
        # while self.dl.is_queue_free():
        #  #   if self.dl.queue_url(url):
        #     self.dl.add_url(url)
        # else:
        #     #TODO implement retry in case the queue will have later space
        #     #TODO block Add button
        #     import time;
        #     time.sleep(30)



if __name__ == "__main__":
    app = App()
