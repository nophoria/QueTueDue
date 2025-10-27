# Checks QueTueDue's core files and assets

# Import dependencies
import os
import pathlib
import re
import shutil
import sys
import zipfile

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
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

# Define constants
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config")
ROOT_PATH = os.path.dirname(__file__)

print(os.path.basename(__file__))

# Checking if update happened previously
if os.path.splitext(os.path.basename(__file__))[0] == "file_checker_":  # True if renamed and ran during an update
    print("Detected a previous update, removing and renaming file_checker.py")
    print("Removing old file_checker...")
    if os.path.exists(os.path.join(ROOT_PATH, "file_checker.py")):
        os.remove(os.path.join(ROOT_PATH, "file_checker.py"))
        print("Removed old file_checker.")

    print("Renaming self: file_checker_.py -> file_checker.py")
    os.rename(os.path.abspath(os.path.join(ROOT_PATH, "file_checker_.py")), os.path.join(ROOT_PATH, "file_checker.py"))
    print("Renamed self.")

    print("Starting file_checker as normal...")
    process = QProcess()
    process.startDetached("python", [os.path.join(ROOT_PATH, "file_checker.py")])
    sys.exit()


# Define variables
branch = False

if "-b" in sys.argv:
    index = sys.argv.index("-b")
    if index + 1 < len(sys.argv):
        branch = sys.argv[index + 1]
elif "--branch" in sys.argv:
    index = sys.argv.index("--branch")
    if index + 1 < len(sys.argv):
        branch = sys.argv[index + 1]

r = requests.get("https://api.github.com/repos/nophoria/QueTueDue/tags")
print(r)
if r.status_code == 200:
    tags = r.json()
    if tags:
        newest_version = tags[0]["name"]
    else:
        print("No versions found")
else:
    print("Failed to fetch versions")
    print(f"Response JSON: {r.json()}")

if os.path.exists(os.path.join(os.path.dirname(__file__), "quetuedue.pyw")):
    with open(os.path.join(os.path.dirname(__file__), "quetuedue.pyw"), "r", encoding="utf-8") as f:
        content = f.read()

    qtd_ver = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)

    if qtd_ver:
        target_version = qtd_ver.group(1)
    else:
        target_version = newest_version
        print("Could not find __version__ in quetuedue.py, is the file missing?")

    print("Target ver:  ", target_version)
else:
    target_version = newest_version
    print("Could not find __version__ in quetuedue.py, is the file missing?")
try:
    print("Latest ver:  ", newest_version)
except NameError:
    print("Failed to fetch versions, therefore newest_version is not defined.")
    newest_version = target_version
print("Current ver: ", target_version)


class CheckSysFiles(QThread):
    """Uses requests to check all files and download any missing ones
    from the GitHub repo.
    """

    finished = pyqtSignal(bool)  # True if all files exist after requesting
    update_needed = pyqtSignal(str)  # Whether to send out a beta or a stable update prompt
    update_progress = pyqtSignal(str, int, int, int)  # What the progress label should say on the update prompt

    def __init__(self):
        super().__init__()

    def run(self):
        self.check_for_update()
        self.check_files()

    def check_files(self):
        """Checks core files such as assets and downloads them if they
        are missing depending on the current version of QueTueDue
        (quetuedue.pyw).
        """
        all_good = True

        if target_version == newest_version:
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
                        if branch:
                            r = requests.get(
                                f"https://github.com/nophoria/QueTueDue/raw/{branch}/{url_file}",
                                headers={"Accept": "application/vnd.github.v3.raw"},
                                stream=True,
                            )
                        else:
                            r = requests.get(
                                f"https://github.com/nophoria/QueTueDue/raw/refs/tags/{target_version}/{url_file}",
                                headers={"Accept": "application/vnd.github.v3.raw"},
                                stream=True,
                            )

                        print(file)
                        print(url_file)
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

    def check_for_update(self):
        """Checks latest version tags on GitHub and prompts the user to
        update if the current target_version is older than the newest
        tag, also, if the current target_version end is b* then prompt
        the user also on beta updates.
        """
        global target_version

        if target_version == newest_version:
            print("Same version, skipping update...")
            return

        elif re.search(r"-b\d+$", target_version) and re.search(r"-b\d+$", newest_version):
            print("Current version is a beta and so is update, prompting user to upgrade to a beta update.")
            self.update_needed.emit("beta")

        elif re.search(r"-b\d+$", newest_version) and not re.search(
            r"-b\d+$", target_version
        ):  # True if only newest is beta
            print("Update is from stable to beta, skipping...")
            target_version = newest_version
            return

        else:
            print("Prompting for update...")
            self.update_needed.emit("stable")

    def update(self):
        if branch:
            print(f"-b/--branch detected, requesting for {branch}.zip")
            self.update_progress.emit(f"-b/--branch detected, retrieving files from {branch}", 1, 0, 1)
            r = requests.get(
                f"https://github.com/nophoria/QueTueDue/zipball/{branch}",
                headers={"Accept": "application/vnd.github.v3+json"},
                stream=True,
            )
        else:
            print(f"Requesting for {target_version}.zip")
            self.update_progress.emit("Retrieving files", 1, 0, 1)
            r = requests.get(
                f"https://api.github.com/repos/nophoria/QueTueDue/zipball/{target_version}",
                headers={"Accept": "application/vnd.github.v3+json"},
                stream=True,
            )

        if r.status_code == 200:
            print("Downloaded successfully!")
            self.update_progress.emit("Retrieving files", 1, 1, 1)

            print("Checking for old update .temp folder...")
            self.update_progress.emit("Removing older update files", 2, 0, 1)
            if os.path.exists(os.path.join(ROOT_PATH, ".temp")):
                shutil.rmtree(os.path.join(ROOT_PATH, ".temp"))
                print("Removed old update .temp folder.")
            self.update_progress.emit("Removing older update files", 2, 1, 1)

            with open(os.path.join(ROOT_PATH, f"{target_version}.zip"), "wb") as f:
                print("Writing zip...")
                self.update_progress.emit("Gathering update files", 3, 0, 1)
                f.write(r.content)
                print(f"{target_version}.zip successfully downloaded and written!")
                self.update_progress.emit("Gathering update files", 3, 1, 1)

            print("Extracting files to .temp folder...")
            with zipfile.ZipFile(os.path.join(ROOT_PATH, f"{target_version}.zip")) as z:
                file_num = 0
                for file in z.infolist():
                    file_num += 1
                    if file.is_dir():
                        print(f"{file} has been detected as a folder, not a file. Skipping...")
                        file_num -= 1  # Subtract of total files if not a file
                        continue  # Skip folders

                    self.update_progress.emit(
                        "Extracting files...",
                        4,
                        file_num,
                        sum(1 for file in pathlib.Path(os.path.join(ROOT_PATH, ".temp")).rglob("*") if file.is_file()),
                    )

                    print(f"Extracting {file} to .temp...")
                    z.extract(file, path=os.path.join(ROOT_PATH, ".temp"))  # Extract to .temp

            print("Renaming file_checker.py in .temp folder...")
            for folder in os.listdir(os.path.join(ROOT_PATH, ".temp")):
                if re.match(r"nophoria-QueTueDue-.*", folder):
                    global zip_folder
                    zip_folder = os.path.join(ROOT_PATH, ".temp", folder)
                    print("Zip folder: ", zip_folder)
                    print("Exists? ", os.path.exists(zip_folder))
                    break

            print("Moving files...")
            file_num = 0
            for root, dirs, files in os.walk(zip_folder):
                for file in files:
                    file_num += 1
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, zip_folder)
                    dst_path = os.path.join(ROOT_PATH, rel_path)
                    print(f"""
                    Source:      {src_path}
                    Relative:    {rel_path}
                    Destination: {dst_path}""")

                    if file == "file_checker.py":
                        dst_path = os.path.join(ROOT_PATH, "file_checker_.py")
                        print(f"file_checker.py detected! Destination is now {dst_path}")

                    if file == "to-do.txt" or file == "config.config":
                        print(f"Skipped user modified files: {file}")
                        file_num -= 1
                        continue

                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    print(f"Moving {src_path} to {dst_path}...")
                    shutil.move(src_path, dst_path)
                    print("Moved successfully!")
                    self.update_progress.emit(
                        "Moving and overwriting files...",
                        5,
                        file_num,
                        sum(1 for file in pathlib.Path(os.path.join(ROOT_PATH, ".temp")).rglob("*") if file.is_file()),
                    )

            print("Cleaning up...")
            self.update_progress.emit("Cleaning up...", 6, 0, 2)
            shutil.rmtree(os.path.join(ROOT_PATH, ".temp"))
            print(".temp folder removed!")
            self.update_progress.emit("Cleaning up...", 6, 1, 2)
            os.remove(os.path.join(ROOT_PATH, f"{target_version}.zip"))
            print("Zip file removed!")
            self.update_progress.emit("Cleaning up...", 6, 2, 2)

            print("Update completed! Quitting current file_checker and running file_checker_.py")
            self.update_progress.emit("Finished!", 7, 1, 1)
            process = QProcess()
            process.startDetached("python", [os.path.join(ROOT_PATH, "file_checker_.py")])
            sys.exit()

    def fetch_file_size(self, url):
        """Finds and returns size of requested GitHub file"""
        r = requests.get(url)
        return int(r.headers.get("Content-Length", 0))


class PromptBetaUpdate(QDialog):
    """Dialog that appears if a newer beta update is found and the
    current version is beta (ends in -b*).
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Found")

        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel("Update Found!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel(
            f"Would you like to update from\n{target_version} to {newest_version}?"
            "\nHowever, this is a beta update and might be unstable."
            "\nThis beta update has only been suggested to you as you are currently on a beta version."
        )
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(7)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Starting update... (Action 0 of 7 - %p%)")
        self.progress_bar.setVisible(False)
        self.yes_button = QPushButton("Update")
        self.no_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sub_label)
        self.layout.addLayout(self.button_layout)
        self.no_button.clicked.connect(self.close_app)
        self.yes_button.clicked.connect(self.update)
        thread.update_progress.connect(self.update_progress_handler)
        self.setLayout(self.layout)

    def close_app(self):
        global target_version
        target_version = newest_version
        thread.check_files()
        self.close()

    def update(self):
        global target_version
        target_version = newest_version
        self.yes_button.setText("Updating...")
        QApplication.processEvents()
        thread.update()

    def update_progress_handler(self, update_progress, action_num, value, maximum):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setFormat(f"{update_progress}... (Action {action_num} of 7 - %p%)")
        QApplication.processEvents()


class PromptUpdate(QDialog):
    """Dialog that appears if a newer beta update is found and the
    current version is beta (ends in -b*).
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Found")
        print("Update prompt launched")

        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel("Update Found!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel(f"Would you like to update from\n{target_version} to {newest_version}?")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(7)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Starting update... (Action 0 of 7 - %p%)")
        self.progress_bar.hide()
        self.yes_button = QPushButton("Update")
        self.no_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sub_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addLayout(self.button_layout)
        self.no_button.clicked.connect(self.close_app)
        self.yes_button.clicked.connect(self.update)
        thread.update_progress.connect(self.update_progress_handler)
        self.setLayout(self.layout)

    def close_app(self):
        global target_version
        target_version = newest_version
        thread.check_files()
        self.close()

    def update(self):
        global target_version
        target_version = newest_version
        self.yes_button.setText("Updating...")
        QApplication.processEvents()
        thread.update()

    def update_progress_handler(self, update_progress, action_num, value, maximum):
        self.progress_bar.show()
        self.progress_bar.setValue(value)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setFormat(f"{update_progress}... (Action {action_num} of 7 - %p%)")


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
        process.startDetached("python", [os.path.join(ROOT_PATH, "quetuedue.pyw"), "-n"])
        sys.exit()


def error_handler(all_good):
    if all_good:
        process = QProcess()
        process.startDetached("python", [os.path.join(ROOT_PATH, "quetuedue.pyw"), "-n"])
        sys.exit()
    else:
        global dlg
        dlg = FetchFileError()
        dlg.exec()


def update_handler(update_type):
    global dlg
    if update_type == "stable":
        dlg = PromptUpdate()
    elif update_type == "beta":
        dlg = PromptBetaUpdate()
    dlg.exec()


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
thread.update_needed.connect(update_handler)
thread.start()

QApplication.processEvents()

app.exec()
