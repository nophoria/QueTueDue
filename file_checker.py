# Checks QueTueDue's core files and assets

# Import dependencies
import os
import sys

import requests
from PyQt6.QtCore import (
    QProcess,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QFont,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

# Define constants
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config")
ROOT_PATH = os.path.dirname(__file__)


class CheckSysFiles(QThread):
    """Uses requests to check all files and download any missing ones
    from the GitHub repo.
    """

    finished = pyqtSignal(bool)  # True if all files exist after requesting

    def run(self):
        all_good = True

        files = [
            os.path.join(ROOT_PATH, "quetuedue.pyw"),
            os.path.join(ROOT_PATH, "logo.png"),
            os.path.join(ROOT_PATH, "LICENSE"),
            os.path.join(ROOT_PATH, "README.md"),
            os.path.join(ASSET_PATH, "to-do.txt"),
            os.path.join(ASSET_PATH, "fonts", "AdwaitaMono-Bold.ttf"),
            os.path.join(ASSET_PATH, "fonts", "AdwaitaMono-BoldItalic.ttf"),
            os.path.join(ASSET_PATH, "fonts", "AdwaitaMono-Italic.ttf"),
            os.path.join(ASSET_PATH, "fonts", "AdwaitaMono-Regular.ttf"),
            os.path.join(ASSET_PATH, "fonts", "AdwaitaSans-Regular.ttf"),
            os.path.join(ASSET_PATH, "fonts", "AdwaitaSans-Italic.ttf"),
            os.path.join(ASSET_PATH, "icons", "logo.svg"),
            os.path.join(ASSET_PATH, "icons", "logo-full.svg"),
            os.path.join(ASSET_PATH, "icons", "logo-full.png"),
            os.path.join(ASSET_PATH, "icons", "add_task_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "add_task_icon_light.png"),
            os.path.join(ASSET_PATH, "icons", "del_all_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "del_all_icon_light.png"),
            os.path.join(ASSET_PATH, "icons", "del_done_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "del_done_icon_light.png"),
            os.path.join(ASSET_PATH, "icons", "del_task_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "del_task_icon_light.png"),
            os.path.join(ASSET_PATH, "icons", "open_app_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "open_app_icon_light.png"),
            os.path.join(ASSET_PATH, "icons", "quit_app_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "quit_app_icon_light.png"),
            os.path.join(ASSET_PATH, "icons", "settings_task_icon_dark.png"),
            os.path.join(ASSET_PATH, "icons", "settings_task_icon_light.png"),
            os.path.join(CONFIG_PATH, "config.config"),
            os.path.join(CONFIG_PATH, "default.config"),
        ]

        url_files = [
            "quetuedue.pyw",
            "logo.png",
            "LICENSE",
            "README.md",
            "assets/to-do.txt",
            "assets/fonts/AdwaitaMono-Bold.ttf",
            "assets/fonts/AdwaitaMono-BoldItalic.ttf",
            "assets/fonts/AdwaitaMono-Italic.ttf",
            "assets/fonts/AdwaitaMono-Regular.ttf",
            "assets/fonts/AdwaitaSans-Regular.ttf",
            "assets/fonts/AdwaitaSans-Italic.ttf",
            "assets/icons/logo.svg",
            "assets/icons/logo-full.svg",
            "assets/icons/logo-full.png",
            "assets/icons/add_task_icon_dark.png",
            "assets/icons/add_task_icon_light.png",
            "assets/icons/del_all_icon_dark.png",
            "assets/icons/del_all_icon_light.png",
            "assets/icons/del_done_icon_dark.png",
            "assets/icons/del_done_icon_light.png",
            "assets/icons/del_task_icon_dark.png",
            "assets/icons/del_task_icon_light.png",
            "assets/icons/open_app_icon_dark.png",
            "assets/icons/open_app_icon_light.png",
            "assets/icons/quit_app_icon_dark.png",
            "assets/icons/quit_app_icon_light.png",
            "assets/icons/settings_task_icon_dark.png",
            "assets/icons/settings_task_icon_light.png",
            "config/config.config",
            "config/default.config",
        ]

        for file, url_file in zip(files, url_files):
            if not os.path.exists(file):
                try:
                    r = requests.get(
                        f"https://github.com/nophoria/QueTueDue/raw/refs/heads/Experimental/{url_file}",
                        headers={"Accept": "application/vnd.github.v3.raw"},
                        stream=True,
                    )
                    print(file)
                    print(r)
                    if r.status_code == 200:
                        os.makedirs(os.path.dirname(file), exist_ok=True)

                        with open(file, "wb") as f:
                            f.write(r.content)
                    else:
                        all_good = False

                except requests.exceptions.RequestException:
                    all_good = False
                    break

        self.finished.emit(all_good)

    def fetch_file_size(self, url):
        """Finds and returns size of requested GitHub file"""
        r = requests.get(url, stream=True)
        return int(r.headers.get("Content-Length", 0))


class FetchFileError(QDialog):
    """Dialog that appears if fetching a file through
    MainWindow.download_file() fails.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error")

        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel("Could not download file :(")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel(
            "There was an error while trying to fetch a missing file. Check your internet connection."
        )
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.yes_button = QPushButton("Launch Anyway")
        self.no_button = QPushButton("Exit")
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sub_label)
        self.layout.addLayout(self.button_layout)
        self.no_button.clicked.connect(self.close_app)
        self.yes_button.clicked.connect(self.hide_app)
        self.setLayout(self.layout)

    def close_app(self):
        sys.exit()

    def hide_app(self):
        process = QProcess()
        process.startDetached("python", [os.path.join(ROOT_PATH, "quetuedue.pyw")])
        sys.exit()


def error_handler(all_good):
    if all_good:
        process = QProcess()
        process.startDetached("python", [os.path.join(ROOT_PATH, "quetuedue.pyw")])
        sys.exit()
    else:
        global dlg
        dlg = FetchFileError()
        dlg.show()


app = QApplication(sys.argv)


# Splash setup
splash = QLabel()
splash.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # No title bar
splash.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Allows for image transparency

# Splash image
if os.path.exists(os.path.join(ASSET_PATH, "icons", "logo-full.png")):
    pixmap = QPixmap(os.path.join(ASSET_PATH, "icons", "logo-full.png"))
    pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
    splash.setPixmap(pixmap)
    splash.setAlignment(Qt.AlignmentFlag.AlignCenter)
    splash.resize(pixmap.size())
    splash.show()

# Check file thread setup
thread = CheckSysFiles()
thread.finished.connect(error_handler)
thread.start()

QApplication.processEvents()

app.exec()
