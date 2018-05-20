from appJar import gui

from downloader import Downloader
from utils import validate_url

class App():

    def __init__(self):
        self.app = gui("Insert Youtube url", "500x100")
        self.app.setResizable(canResize=True)
        self.app.setOnTop(stay=True)
        self.app.startFrame("LEFT", row=0, column=0)
        self.app.addLabel("url_label", "url:", 0, 0)
        self.app.addValidationEntry("url_value", 0, 1)
        self.app.setEntryMaxLength("url_value", 64)
        self.app.setEntryDefault("url_value", "https://www.youtube.com/...")
        self.app.addButtons(["Download", "Cancel"], self.press, 2, 0, 2)
        self.dl = self.create_downloader()

    def run(self):
        # start the GUI and create the Downloader instance
        self.app.go()
        self.create_downloader()

    def create_downloader(self):
        dl = Downloader()
        self.app.addStatusbar(fields=1)
        self.app.setStatusbar(dl.get_status(), 0)
        return dl

    def press(self, btnName):
        if btnName == "Cancel":
            self.app.clearEntry("url_value", callFunction=False)
        # Download button
        url = self.app.getEntry("url_value").strip()
        try:
            validate_url(url)
            self.app.setValidationEntry("url_value", state="valid")
            self.add_url(url)
        except ValueError:
            # import pdb;
            # pdb.set_trace()
            self.app.setValidationEntry("url_value", state="invalid")
   #      except:
   #          # something wrong happened
   #          self.app.stop()

    def file_ready(self):
        self.app.infoBox("Info", "The file has been downloaded")

    def add_url(self, url):
        self.dl.add_url(url)


if __name__ == "__main__":
    app = App()
    app.run()
