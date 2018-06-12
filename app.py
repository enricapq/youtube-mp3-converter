import logging as log
from queue import Full

from appJar import gui

from downloader import DownloadManager
from utils import get_download_path


class GUIApp():

    def __init__(self):
        self.app = gui("Youtube to mp3 converter", "550x230")
        self.app.setResizable(canResize=True)
        self.app.setOnTop(stay=True)
        self.app.startFrame("LEFT", row=0, column=0)
        self.app.setBg("#4EC5C1")
        self.app.setFont(15)

        self.app.addLabel("url_label", "Insert Youtube url:", 0, 0)
        self.app.addValidationEntry("url_value", 0, 1)
        self.app.setFocus("url_value")
        self.app.setEntryMaxLength("url_value", 80)
        self.app.setEntryFg("url_value", "#000000")
        self.app.setEntryDefault("url_value", "https://www.youtube.com/...")

        self.app.addButtons(["Download", "Cancel"], self.press, 2, 0, 2)
        self.app.setButtonState("Download", "normal")
        self.app.setButtonState("Cancel", "normal")
        self.app.setButtonRelief("Download", "groove")
        self.app.setButtonRelief("Cancel", "groove")

        # Return default user's download path for Linux, macOS or Windows
        self.app.save_dir = get_download_path()

        self.dl = self.create_downloader()

        # add status bar on the bottom of the window
        self.app.addStatusbar(fields=1)
        self.app.setStatusbarBg("#000000", 0)
        # every second check the status of Download and update the status bar
        self.app.registerEvent(self.update_status)

        self.app.go()

    def stop_app(self):
        log.info("app stopped")
        self.app.stop()
        #TODO stop all downloads, kill threads
        # self.dl.stop_downloads(self)

    def create_downloader(self):
        # Instantiate class that takes care of downloading videos
        dl = DownloadManager(self.app.save_dir)
        return dl

    def clear_entry(self):
        self.app.clearEntry("url_value", callFunction=False)

    def press(self, btnName):
        if btnName == "Cancel":
            # TODO stop current download
            self.clear_entry()
            return
        # Download button pressed
        # test: url = 'https://www.youtube.com/watch?v=r_xpgogcNwg'
        url = self.app.getEntry("url_value").strip()
        try:
            self.dl.validate_url(url)
            self.app.setValidationEntry("url_value", state="valid")
            # When the download is finished, call download_completed
            self.app.threadCallback(self.download_url, self.download_completed, url)
        except ValueError:
            self.app.queueFunction(self.app.setValidationEntry, "url_value", state="invalid")

        except Exception as e:
            # Something wrong happened
            log.error(f"Error {e}")
            self.stop_app()

    def download_url(self, url):
        try:
            self.dl.download_url(url)
            return url
        except Exception as e:
            log.error(f"Reached max number of contemporary downloads {e}")
            if isinstance(e, Full):
                import time;
                time.sleep(1)

    def update_status(self):
        # update the status bar and the buttons with the status of download every second
        (status, msg, msg_color, dl_color, cancel_color,
         status_button_dl, status_button_cl)= self.dl.get_status()
        # update status bar
        self.app.setStatusbar(msg, 0)
        self.app.setStatusbarFg(msg_color, 0)
        # update buttons
        self.app.setButtonBg("Download", dl_color)
        self.app.setButtonBg("Cancel", cancel_color)
        self.app.setButtonState("Download", status_button_dl)
        self.app.setButtonState("Cancel", status_button_cl)

    def download_completed(self, url):
        # TODO re-enable Download button

        log.info(f"Download of {url} completed!!")
        self.clear_entry()


if __name__ == "__main__":
    GUIApp()
