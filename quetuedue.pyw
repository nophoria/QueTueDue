# QueTueDue v0.6-b3

__version__ = "v0.6-b3"

# Import dependecies
import json
import os
import re
import sys

from PyQt6.QtCore import (
    QProcess,
    QSize,
    Qt,
)
from PyQt6.QtGui import (
    QAction,
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QPalette,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedLayout,
    QSystemTrayIcon,
    QTextBrowser,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

# Define Constants
ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icons")
FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts")
TODO_PATH = os.path.join(os.path.dirname(__file__), "assets", "todo.json")
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.config")
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "config", "default.config"
)
ROOT_PATH = os.path.dirname(__file__)

if "-n" not in sys.argv and "--no-file-checking" not in sys.argv:
    process = QProcess()
    process.startDetached("python", [os.path.join(ROOT_PATH, "file_checker.py")])
    sys.exit()


def config_arg_load(keyword, acceptedValues):
    """Loads a config setting from a defined keyword in the config file.
    If the setting saved in the config.config file is invalid, blank or
    not there it will default to the specified setting in
    default.config.
    """
    with open(USER_CONFIG_PATH, "r") as f:
        for line in f.readlines():
            if line.startswith(keyword):
                phrase = line.strip().split("=", 1)[1]
                if phrase.strip() != "" and phrase in acceptedValues:
                    return phrase

    with open(DEFAULT_CONFIG_PATH, "r") as f:
        for line in f.readlines():
            if line.startswith(keyword):
                return line.strip().split("=", 1)[1]


# Define config settings
THEME = config_arg_load("theme", ["dark", "light"])
HIDE_WHEN_CLOSED = config_arg_load("HideWhenClosed", ["True", "False"])


def separator(hOrV):
    """Makes a QFrame line to separate categories or sections from one
    another.
    """
    line = QFrame()
    if hOrV == "h":
        line.setFrameShape(QFrame.Shape.HLine)
    elif hOrV == "v":
        line.setFrameShape(QFrame.Shape.VLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setLineWidth(1)
    return line


class AddWindow(QDialog):
    """The window pop-up for the add task toolbar action."""

    def __init__(self, MainWindow_instance, parent=None):
        super().__init__(parent)
        self.app_window = MainWindow_instance
        self.setWindowTitle("QueTueDue - Add a task")

        # Layouts
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label_layout = QHBoxLayout()
        self.label_layout.setSpacing(16)

        # Widgets
        self.label = QLabel("Add a new task")
        self.label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.families[4][0], 32))
        self.label_separator = separator("h")
        self.label_layout.addWidget(self.label)
        self.label_layout.addWidget(self.label_separator)
        self.sub_label = QLabel("Enter the new task below in the text box")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.sub_label.setFont(QFont(self.app_window.families[4][0], 12))
        self.input = QLineEdit()
        self.yes_button = QPushButton("Add")
        self.no_button = QPushButton("Cancel")
        self.yes_button.setFont(QFont(self.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.families[4][0]))
        self.button_layout.addWidget(self.yes_button)
        self.yes_button.setEnabled(False)
        self.button_layout.addWidget(self.no_button)
        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.sub_label)
        self.layout.addWidget(self.input)
        self.layout.addLayout(self.button_layout)
        self.input.textChanged.connect(self.check_for_duplicates)
        self.no_button.clicked.connect(self.exit)
        self.yes_button.clicked.connect(self.append_new_task)
        self.setLayout(self.layout)

    def append_new_task(self):
        """Add a task to the to-do list by appending a line to the todo
        file in the to-do category (t).
        """
        self.app_window.validate_todo_json()
        if not self.check_for_duplicates():
            with open(TODO_PATH, "r", encoding="utf-8") as f:
                try:
                    todo_json = json.load(f)
                except Exception as e:
                    print(e)
                    self.close()
            line = self.input.text()
            item = {
                "name": line,
                "desc": "notImplented",
                "due": "YYYY-MM-DDTHH:MM:SS",
                "category": "white",
            }
            todo_json["todo"].append(item)
            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.write(json.dumps(todo_json, indent=2))

            self.app_window.load_checkboxes()
            self.close()

    def check_for_duplicates(self):
        """Constantly recieves what's in the self.input line edit and
        checks if a task with the same name already exists or if the
        line edit is blank. If it does, the function will grey-out the
        "Add" (self.yes_button) button and set the text to "Task already
        exists".
        """
        with open(TODO_PATH, "r", encoding="utf-8") as f:
            try:
                todo_json = json.load(f)
            except Exception as e:
                print(e)
                self.close()

        line = self.input.text()

        dupe = False
        for progress in todo_json:
            for item in todo_json[progress]:
                if line == item["name"]:
                    dupe = True

        if dupe:
            self.yes_button.setEnabled(False)
            self.yes_button.setText("Task already exists")
            return True
        elif line.strip() == "":
            self.yes_button.setEnabled(False)
            self.yes_button.setText("Enter a task name")
            return True
        else:
            self.yes_button.setEnabled(True)
            self.yes_button.setText("Add")
            return False

    def exit(self):
        self.close()


class DelWindow(QDialog):
    """The window pop-up for the Remove action on the toolbar."""

    def __init__(self, MainWindow_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QueTueDue - Remove a task")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label_layout = QHBoxLayout()
        self.label_layout.setSpacing(16)
        self.label = QLabel("Remove a task")
        self.label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.families[4][0], 32))
        self.label_separator = separator("h")
        self.label_layout.addWidget(self.label)
        self.label_layout.addWidget(self.label_separator)
        self.sub_label = QLabel("Pick a task from the drop down below to remove")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.sub_label.setFont(QFont(self.app_window.families[4][0], 12))
        self.task_list = QComboBox()
        self.yes_button = QPushButton("Remove")

        todo_json = self.app_window.validate_todo_json()

        if (
            len(todo_json["todo"]) + len(todo_json["inprog"]) + len(todo_json["done"])
            == 0
        ):
            self.yes_button.setEnabled(False)
            self.yes_button.setText("No tasks")

        self.no_button = QPushButton("Cancel")
        self.yes_button.setFont(QFont(self.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.families[4][0]))
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)

        todo_json = self.app_window.validate_todo_json()
        for category in ["todo", "inprog", "done"]:
            for item in todo_json[category]:
                print(item)
                self.task_list.addItem(item["name"])

        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.sub_label)
        self.layout.addWidget(self.task_list)
        self.layout.addLayout(self.button_layout)
        self.yes_button.clicked.connect(self.del_task)
        self.no_button.clicked.connect(self.exit)
        self.setLayout(self.layout)

    def del_task(self):
        """Removes a task by filtering the lines in to-do.txt and
        re-writing the file with the filtered lines.
        """
        task_to_del = self.task_list.currentText()
        print(task_to_del)

        todo_json = self.app_window.validate_todo_json()

        for category in ["todo", "inprog", "done"]:
            for item in todo_json[category]:
                if item["name"] == task_to_del:
                    todo_json[category].remove(item)
                    break

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(todo_json, indent=2))

        self.app_window.load_checkboxes()
        self.close()

    def exit(self):
        self.close()


class MarkAllAsDoneWindow(QDialog):
    """The window pop-up for the Mark all as Done toolbar action."""

    def __init__(self, MainWindow_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QueTueDue - Mark all as Done")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label_layout = QHBoxLayout()
        self.label_layout.setSpacing(16)
        self.label = QLabel("Mark off all tasks")
        self.label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.families[4][0], 32))
        self.label_separator = separator("h")
        self.label_layout.addWidget(self.label)
        self.label_layout.addWidget(self.label_separator)
        self.sub_label = QLabel("Mark all tasks as done")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.sub_label.setFont(QFont(self.app_window.families[4][0], 12))
        self.yes_button = QPushButton("Mark as Done")
        self.no_button = QPushButton("Cancel")
        self.yes_button.setFont(QFont(self.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.families[4][0]))

        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.sub_label)
        self.layout.addLayout(self.button_layout)
        self.yes_button.clicked.connect(self.mark_all_as_done)
        self.no_button.clicked.connect(self.exit)
        self.setLayout(self.layout)

        self.sub_label.setText(self.gen_sub_label())

    def mark_all_as_done(self):
        """Loops through each item in todo.json and moves it to the 'done' category"""
        todo_json = self.app_window.validate_todo_json()

        for item in todo_json['todo']:
            todo_json['done'].append(item)
        
        for item in todo_json['inprog']:
            todo_json['done'].append(item)
        
        todo_json['todo'] = []
        todo_json['inprog'] = []

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(todo_json, indent=2))

        self.app_window.load_checkboxes()
        self.close()

    def gen_sub_label(self):
        """Changes the text on a label to mention first affected task
        explicitly and x more.
        """
        todo_json = self.app_window.validate_todo_json()
        label_text = 'Are you sure you want to mark off "'

        tasks = []
        for category in ["todo", "inprog"]:
            for item in todo_json[category]:
                tasks.append(item["name"])

        if len(tasks) > 0:
            label_text += f'{tasks[0]}"'
        else:
            label_text = "There are no tasks in the 'To-Do' or 'In Prog.' categories."
            self.yes_button.setEnabled(False)
            self.yes_button.setText("No tasks")
            no_tasks = True

        if not len(tasks) - 1 < 2:
            label_text += f" and {len(tasks) - 1} others?"
        elif not len(tasks) - 1 < 1:
            label_text += f" and {len(tasks) - 1} other?"
        elif not no_tasks:
            label_text += "?"

        return label_text

    def exit(self):
        """Sets the app page to MainWindow's main_page"""
        self.close()


class DelDoneWindow(QDialog):
    """The window pop-up for the Remove all done toolbar action."""

    def __init__(self, MainWindow_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QueTueDue - Remove all done")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label_layout = QHBoxLayout()
        self.label_layout.setSpacing(16)
        self.label = QLabel("Remove all done tasks")
        self.label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.families[4][0], 32))
        self.label_separator = separator("h")
        self.label_layout.addWidget(self.label)
        self.label_layout.addWidget(self.label_separator)
        self.sub_label = QLabel('Remove all tasks listed in the "Done :)" section')
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.sub_label.setFont(QFont(self.app_window.families[4][0], 12))
        self.yes_button = QPushButton("Remove")
        self.no_button = QPushButton("Cancel")
        self.yes_button.setFont(QFont(self.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.families[4][0]))

        self.app_window.setMinimumSize(400, 250)
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.sub_label)
        self.layout.addLayout(self.button_layout)
        self.yes_button.clicked.connect(self.del_done)
        self.no_button.clicked.connect(self.exit)
        self.setLayout(self.layout)

        self.sub_label.setText(self.gen_sub_label())

    def gen_sub_label(self):
        """Changes the text on a label to mention first affected task
        explicitly and x more.
        """
        todo_json = self.app_window.validate_todo_json()
        label_text = 'Are you sure you want to remove "'

        done_tasks = []
        for item in todo_json["done"]:
            done_tasks.append(item["name"])

        if len(done_tasks) > 0:
            label_text += f'{done_tasks[0]}"?'
        else:
            label_text = "There are no done tasks"
            self.yes_button.setEnabled(False)
            self.yes_button.setText("No done tasks")

        if not len(done_tasks) - 1 < 2:
            label_text += f" and {len(done_tasks) - 1} others?"
        elif not len(done_tasks) - 1 < 1:
            label_text += f" and {len(done_tasks) - 1} other?"
        elif self.yes_button.isEnabled:
            label_text += "?"

        return label_text

    def del_done(self):
        """Removes all lines in to-do.txt beginning with d (the done
        category).
        """
        todo_json = self.app_window.validate_todo_json()

        todo_json["done"] = []

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(todo_json, indent=2))

        self.app_window.load_checkboxes()
        self.close()

    def exit(self):
        self.close()


class DelAllWindow(QDialog):
    """The window pop-up for the Remove ALL Items toolbar action."""

    def __init__(self, MainWindow_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QueTueDue - Remove all done")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label_layout = QHBoxLayout()
        self.label_layout.setSpacing(16)
        self.label = QLabel("Remove ALL tasks")
        self.label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.families[4][0], 32))
        self.label_separator = separator("h")
        self.label_layout.addWidget(self.label)
        self.label_layout.addWidget(self.label_separator)
        self.sub_label = QLabel("Remove EVERY task")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.sub_label.setFont(QFont(self.app_window.families[4][0], 12))
        self.yes_button = QPushButton("Remove")
        self.no_button = QPushButton("Cancel")
        self.yes_button.setFont(QFont(self.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.families[4][0]))

        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.sub_label)
        self.layout.addLayout(self.button_layout)
        self.yes_button.clicked.connect(self.DelAllSureWindow)
        self.no_button.clicked.connect(self.exit)
        self.setLayout(self.layout)

        self.sub_label.setText(self.gen_sub_label())

    def gen_sub_label(self):
        """Changes the text on a label to mention first affected task
        explicitly and x more.
        """
        label_text = 'Are you sure you want to remove "'

        todo_json = self.app_window.validate_todo_json()

        tasks = []
        for category in ["todo", "inprog", "done"]:
            for item in todo_json[category]:
                tasks.append(item["name"])

        if len(tasks) > 0:
            label_text += f'{tasks[0]}"'
        else:
            label_text = "There are no tasks"
            self.yes_button.setEnabled(False)
            self.yes_button.setText("No tasks")
            no_tasks = True

        if not len(tasks) - 1 < 2:
            label_text += f" and {len(tasks) - 1} others?"
        elif not len(tasks) - 1 < 1:
            label_text += f" and {len(tasks) - 1} other?"
        elif not no_tasks:
            label_text += "?"

        return label_text

    def exit(self):
        """Sets the app page to MainWindow's main_page"""
        self.close()

    def DelAllSureWindow(self):
        """Shows the confirm window pop-up."""
        self.w = DelAllSureWindow(self)
        self.w.show()


class DelAllSureWindow(QDialog):
    """The window pop-up that asks the user to confirm removing all
    tasks via the Remove ALL Items toolbar action.
    """

    def __init__(self, DelAllWindow_instance):
        super().__init__()
        self.app_window = DelAllWindow_instance
        self.setWindowTitle("Are you sure?")

        self.label = QLabel(
            "Are you VERY sure you want to PERMANENTLY DELETE ALL ITEMS?!"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.app_window.families[4][0], 32))
        self.yes_button = QPushButton("Remove ALL ITEMS")
        self.no_button = QPushButton("Nevermind")
        self.yes_button.setFont(QFont(self.app_window.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.app_window.families[4][0]))

        self.yes_button.clicked.connect(self.delAll)
        self.no_button.clicked.connect(self.exit)

        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

    def delAll(self):
        with open(TODO_PATH, "w") as f:
            clear_json = {"todo": [], "inprog": [], "done": []}
            f.write(json.dumps(clear_json, indent=2))

        self.app_window.app_window.load_checkboxes()
        self.app_window.close()
        self.close()

    def exit(self):
        self.close()


class ParseTodoErrorWindow(QDialog):
    """Dialog that appears if parsing the todo list as JSON fails."""

    def __init__(self, MainWindow_instance):
        super().__init__()
        self.setWindowTitle("Error")

        self.main = MainWindow_instance

        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.label = QLabel("Corrupt or erroneous todo list!")
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self.label.setFont(QFont(self.main.families[4][0], 32))

        self.sub_label = QLabel(
            "There was an error while trying to parse your todo list! If you have modified it externally, check the formatting."
        )
        self.sub_label.setFont(QFont(self.main.families[4][0], 12))
        self.sub_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self.error_label = QTextBrowser()
        self.error_label.setText(str(self.main.todo_error))
        self.error_label.setFont(QFont(self.main.families[4][0], 8))
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.yes_button = QPushButton("Create blank list")

        self.no_button = QPushButton("Exit")

        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sub_label)
        self.layout.addWidget(self.error_label)
        self.layout.addLayout(self.button_layout)

        self.no_button.clicked.connect(self.close_app)
        self.yes_button.clicked.connect(self.clear_todo)

        self.setLayout(self.layout)

    def close_app(self):
        sys.exit()

    def clear_todo(self):
        with open(TODO_PATH, "w") as f:
            f.write(json.dumps('{"todo": [], "inprog": [], "done": []}', indent=2))

        self.close()


class MainWindow(QMainWindow):
    """The main app window containing all the categories, tasks toolbars
    and more.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("QueTueDue")
        self.setWindowIcon(QIcon(os.path.join(ICON_PATH, "logo.svg")))
        self.setMinimumWidth(800)

        # Define fonts
        self.fonts = [
            "AdwaitaMono-Regular.ttf",
            "AdwaitaMono-Bold.ttf",
            "AdwaitaMono-Italic.ttf",
            "AdwaitaMono-BoldItalic.ttf",
            "AdwaitaSans-Regular.ttf",
            "AdwaitaSans-Italic.ttf",
        ]
        self.font_dialogs = []
        self.families = []
        for self.font in self.fonts:
            self.fontfile = os.path.join(FONT_PATH, self.font)
            if not os.path.exists(self.fontfile):
                process.startDetached(
                    "python", [os.path.join(ROOT_PATH, "file_checker.py")]
                )
                sys.exit()
            else:
                id = QFontDatabase.addApplicationFont(self.fontfile)
                self.families.append(QFontDatabase.applicationFontFamilies(id))

        # System tray icon
        self.icon = QIcon(os.path.join(ICON_PATH, "logo.svg"))

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        self.tray.show()

        self.tray_menu = QMenu()

        self.title_action = QAction("𝗤𝘂𝗲𝗧𝘂𝗲𝗗𝘂𝗲")
        self.title_action.setIcon(QIcon(os.path.join(ICON_PATH, "logo.svg")))

        self.open_app_tray_action = QAction("𝗢𝗽𝗲𝗻 𝗳𝘂𝗹𝗹 𝗮𝗽𝗽")
        self.open_app_tray_action.triggered.connect(self.open_app)
        self.open_app_tray_action.setIcon(
            QIcon(os.path.join(ICON_PATH, f"open_app_icon_{THEME}.png"))
        )

        self.quit_app_tray_action = QAction("𝗤𝘂𝗶𝘁 𝗤𝘂𝗲𝗧𝘂𝗲𝗗𝘂𝗲")
        self.quit_app_tray_action.triggered.connect(self.quit_app)
        self.quit_app_tray_action.setIcon(
            QIcon(os.path.join(ICON_PATH, f"quit_app_icon_{THEME}.png"))
        )

        self.tray.setContextMenu(self.tray_menu)

        # Main layouts
        self.stack_layout = QStackedLayout()
        self.main_layout = QVBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.todo_layout = QVBoxLayout()
        self.todo_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.in_prog_layout = QVBoxLayout()
        self.in_prog_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.done_layout = QVBoxLayout()
        self.done_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tabbar_layout = QHBoxLayout()

        # Toolbar
        self.toolbar = QToolBar("Utilities")
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.toolbar)

        self.add_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"add_task_icon_{THEME}.png")), "Add", self
        )
        self.add_action.setStatusTip("Add a new task")
        self.add_action.triggered.connect(self.add_task_window)

        self.mark_all_done_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"mark_all_as_done_icon_{THEME}.png")),
            "Mark All Done",
            self,
        )
        self.mark_all_done_action.triggered.connect(self.mark_all_done_window)
        self.mark_all_done_action.setStatusTip('Mark all current tasks "Done"')

        self.del_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"del_task_icon_{THEME}.png")), "Remove", self
        )
        self.del_action.setStatusTip("Remove a task")
        self.del_action.triggered.connect(self.del_task_window)

        self.del_done_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"del_done_icon_{THEME}.png")),
            "Remove Done",
            self,
        )
        self.del_done_action.setStatusTip("Remove all tasks marked as done")
        self.del_done_action.triggered.connect(self.del_done_window)

        self.del_all_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"del_all_icon_{THEME}.png")),
            "Remove ALL Items",
            self,
        )
        self.del_all_action.setStatusTip("Remove ALL ITEMS PERMANENTLY")
        self.del_all_action.triggered.connect(self.del_all_window)

        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.del_action)
        self.toolbar.addAction(self.mark_all_done_action)
        self.toolbar.addAction(self.del_done_action)
        self.toolbar.addAction(self.del_all_action)

        # Widgets
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(8)
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.header_menu_layout = QHBoxLayout()
        self.header_title_layout = QHBoxLayout()

        self.header_menu = QMenu()
        self.header_menu_file = QAction("File")
        self.header_menu_file.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_file)

        self.header_menu_add = QAction("Add")
        self.header_menu_add.triggered.connect(lambda: self.add_task_window())
        self.header_menu_add.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_add)

        self.header_menu_remove_menu = QMenu("Remove")
        self.header_menu_remove_menu.setFont(QFont(self.families[4][0]))

        self.header_menu_remove = QAction("Remove")
        self.header_menu_remove.triggered.connect(lambda: self.del_task_window())
        self.header_menu_remove.setFont(QFont(self.families[4][0]))

        self.header_menu_remove_all = QAction("Remove ALL")
        self.header_menu_remove_all.triggered.connect(lambda: self.del_all_window())
        self.header_menu_remove_all.setFont(QFont(self.families[4][0]))

        self.header_menu_remove_menu.addAction(self.header_menu_remove)
        self.header_menu_remove_menu.addAction(self.header_menu_remove_all)
        self.header_menu.addMenu(self.header_menu_remove_menu)

        self.header_menu_mark_off = QAction("Mark Off All")
        self.header_menu_mark_off.triggered.connect(lambda: self.mark_all_done_window())
        self.header_menu_mark_off.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_mark_off)

        self.header_menu_edit = QAction("Edit")
        self.header_menu_edit.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_edit)

        self.header_menu.addSeparator()

        self.header_menu_settings = QAction("Settings")
        # self.header_menu_settings.triggered.connect() # TO-DO make settings page
        self.header_menu_settings.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_settings)

        self.header_menu_about = QAction("About")
        # self.header_menu_settings.triggered.connect() # TO-DO make About (fullscreen) page
        self.header_menu_about.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_about)

        self.header_menu_button = QToolButton()
        self.header_menu_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup
        )
        self.header_menu_button.setIcon(
            QIcon(os.path.join(ICON_PATH, f"header_menu_icon_{THEME}.png"))
        )
        self.header_menu_button.setIconSize(QSize(24, 24))
        self.header_menu_button.setFixedSize(32, 32)
        # self.header_menu_button.setFlat(True)
        self.header_menu_button.setMenu(self.header_menu)

        # self.header_page_label = QLabel("Tasks")
        # self.header_page_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # self.header_page_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        # self.header_page_label.setFont(QFont(self.families[4][0]))

        self.header_menu_layout.addWidget(self.header_menu_button)
        # self.header_menu_layout.addWidget(self.header_page_label)

        self.header_icon = QLabel()
        pixmap = QPixmap(os.path.join(ASSET_PATH, "icons", "logo.png"))
        pixmap = pixmap.scaledToWidth(24, Qt.TransformationMode.SmoothTransformation)
        self.header_icon.setPixmap(pixmap)
        self.header_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_icon.resize(pixmap.size())

        self.header_label = QLabel("QueTueDue")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.header_label.setContentsMargins(0, 4, 0, 4)
        self.header_label.setFont(QFont(self.families[4], 12))

        self.header_sub_label = QLabel(f"{__version__}")
        self.header_sub_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.header_sub_label_palette = self.header_sub_label.palette()
        self.header_sub_label_palette.setColor(
            QPalette.ColorRole.WindowText, QColor(50, 50, 50)
        )
        self.header_sub_label.setPalette(self.header_sub_label_palette)
        self.header_sub_label.setFont(QFont(self.families[4], 10))

        self.header_title_layout.addWidget(self.header_icon)
        self.header_title_layout.addWidget(self.header_label)
        self.header_title_layout.addWidget(self.header_sub_label)
        self.header_title_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.header_layout.addLayout(self.header_menu_layout)
        self.header_layout.addLayout(self.header_title_layout)
        self.main_layout.addLayout(self.header_layout)

        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.addLayout(self.todo_layout)
        self.tasks_layout.addWidget(separator("v"))
        self.tasks_layout.addLayout(self.in_prog_layout)
        self.tasks_layout.addWidget(separator("v"))
        self.tasks_layout.addLayout(self.done_layout)

        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.in_prog_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.done_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_layout.addLayout(self.tasks_layout)

        self.header_spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.main_layout.addItem(self.header_spacer)

        self.todo_header = QLabel("To-Do")
        try:
            self.todo_header.setFont(QFont(self.families[0], 32))
        except IndexError:
            self.todo_header.setFont(QFont("", 32))
        self.todo_layout.addWidget(self.todo_header)
        self.todo_header.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self.in_prog_header = QLabel("In Prog.")
        try:
            self.in_prog_header.setFont(QFont(self.families[0], 32))
        except IndexError:
            self.in_prog_header.setFont(QFont("", 32))
        self.in_prog_layout.addWidget(self.in_prog_header)
        self.in_prog_header.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self.done_header = QLabel("Done :)")
        try:
            self.done_header.setFont(QFont(self.families[0], 32))
        except IndexError:
            self.done_header.setFont(QFont("", 32))
        self.done_layout.addWidget(self.done_header)
        self.done_header.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self.load_checkboxes()
        container = QWidget()
        container.setLayout(self.main_layout)

        self.setCentralWidget(container)

        self.setMinimumWidth(800)
        QApplication.processEvents()
        self.load_checkboxes()

    def add_task_window(self, checked=False):
        """Open the Add task toolbar task window pop-up."""
        self.w = AddWindow(self)
        self.w.show()

    def mark_all_done_window(self, checked=False):
        """Open the Add task toolbar task window pop-up."""
        self.w = MarkAllAsDoneWindow(self)
        self.w.show()

    def del_task_window(self, checked=False):
        """Open the Remove task toolbar task window pop-up."""
        self.w = DelWindow(self)
        self.w.show()

    def del_done_window(self, checked=False):
        """Open the Remove all done toolbar task window pop-up."""
        self.w = DelDoneWindow(self)
        self.w.show()

    def del_all_window(self, checked=False):
        """Open the Remove ALL Items toolbar task window pop-up."""
        self.w = DelAllWindow(self)
        self.w.show()

    def open_app(self):
        """Open the main app when the Open full app system tray context
        menu option is triggered.
        """
        self.show()

    def clear_layout(self, layout, start):
        """Removes all widgets in a given layout."""
        for i in reversed(range(start, layout.count())):
            task = layout.takeAt(i)
            widget = task.widget()
            if widget:
                widget.deleteLater()

    def load_checkboxes(self):
        """Clears layouts and system tray list and re-adds checkboxes
        from to-do.
        """

        # Clear checkboxes
        self.clear_layout(self.todo_layout, 1)
        self.clear_layout(self.in_prog_layout, 1)
        self.clear_layout(self.done_layout, 1)

        # Clear and re-add static tray tasks (except open full app).
        self.tray_menu.clear()

        self.tray_actions = []
        self.tray_menu.addAction(self.title_action)
        self.tray_menu.addSeparator()

        todo_json = self.validate_todo_json()

        for item in todo_json["todo"]:
            task_text = item["name"]
            task_desc = item["desc"]

            checkbox = QCheckBox(task_text)

            max_width = max(50, int(self.width() / 3) - 2)
            checkbox.setMaximumWidth(max_width)
            checkbox.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )

            try:
                checkbox.setFont(QFont(self.families[4]))
            except IndexError:
                continue

            # Add checkboxes and tray tasks depending on category
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            checkbox.toolTip = task_desc
            self.todo_layout.addWidget(checkbox)
            checkbox_tray_action = QAction(task_text)
            self.tray_actions.append(checkbox_tray_action)
            self.tray_menu.addAction(checkbox_tray_action)

            self.blockSignals(False)

            checkbox.setProperty("task", task_text)
            checkbox.setTristate(True)
            checkbox.stateChanged.connect(
                lambda state, cb=checkbox: self.moveCheckbox(cb, state)
            )

        for item in todo_json["inprog"]:
            task_text = item["name"]
            task_desc = item["desc"]

            checkbox = QCheckBox(task_text)

            max_width = max(50, int(self.width() / 3) - 2)
            checkbox.setMaximumWidth(max_width)
            checkbox.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )

            try:
                checkbox.setFont(QFont(self.families[4]))
            except IndexError:
                continue

            # Add checkboxes and tray tasks depending on category
            checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
            checkbox.toolTip = task_desc
            self.in_prog_layout.addWidget(checkbox)

            self.blockSignals(False)

            checkbox.setProperty("task", task_text)
            checkbox.setTristate(True)
            checkbox.stateChanged.connect(
                lambda state, cb=checkbox: self.moveCheckbox(cb, state)
            )

        for item in todo_json["done"]:
            task_text = item["name"]
            task_desc = item["desc"]

            checkbox = QCheckBox(task_text)

            max_width = max(50, int(self.width() / 3) - 2)
            checkbox.setMaximumWidth(max_width)
            checkbox.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )

            try:
                checkbox.setFont(QFont(self.families[4]))
            except IndexError:
                continue

            # Add checkboxes and tray tasks depending on category
            checkbox.setCheckState(Qt.CheckState.Checked)
            checkbox.toolTip = task_desc
            self.done_layout.addWidget(checkbox)

            self.blockSignals(False)

            checkbox.setProperty("task", task_text)
            checkbox.setTristate(True)
            checkbox.stateChanged.connect(
                lambda state, cb=checkbox: self.moveCheckbox(cb, state)
            )

        # Add final static tray tasks and refresh the tray context menu
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.open_app_tray_action)
        self.tray_menu.addAction(self.quit_app_tray_action)
        self.tray.setContextMenu(self.tray_menu)

    def closeEvent(self, e):
        """Override the close signal and hide the window instead of
        closing it, meaning that the process is not killed and the
        system tray icon remains.
        """
        if HIDE_WHEN_CLOSED == "True":
            e.ignore()
            self.hide()
        else:
            super().closeEvent(e)

    def open_popup_window(self, WindowInstance, checked=False):
        """Open the specified popup window (WindowInstance). This is used for the
        toolbar and button actions."""
        self.w = WindowInstance(self)
        self.w.show()

    def quit_app(self):
        """Quit the whole process when the Quit QueTueDue system tray
        context menu option is triggered.
        """
        sys.exit()

    def moveCheckbox(self, cb, state):
        """Deletes specified task (cb) from to-do.json and re-adds it
        in the new category based on the state (state) of the checkbox.
        """
        print(state)
        todo_text = cb.text()
        todo_json = self.validate_todo_json()

        if state == 1:
            for item in todo_json["todo"]:
                if item["name"] == todo_text:
                    todo_json["inprog"].append(item)
                    print("appended")
                    todo_json["todo"].remove(item)
                    print("removed")
                    break
        elif state == 2:
            for item in todo_json["inprog"]:
                if item["name"] == todo_text:
                    todo_json["done"].append(item)
                    print("appended")
                    todo_json["inprog"].remove(item)
                    print("removed")
                    break
        elif state == 0:
            for item in todo_json["done"]:
                if item["name"] == todo_text:
                    todo_json["todo"].append(item)
                    print("appended")
                    todo_json["done"].remove(item)
                    print("removed")
                    break

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(todo_json, indent=2))

        self.load_checkboxes()

    def validate_todo_json(self):
        """Validates and returns the todo list as a JSON python object."""
        todo_json = None
        with open(TODO_PATH, "r") as f:
            try:
                todo_json = json.load(f)
            except json.decoder.JSONDecodeError as e:
                self.todo_error = e
                todo_error_dlg = ParseTodoErrorWindow(self)
                todo_error_dlg.show()

        if todo_json:
            return todo_json
        else:
            return "{}"

    def resizeEvent(self, event):
        #        self.load_checkboxes()
        print(self.height())
        print(self.header_label.height())
        print(self.height() - self.header_label.height())
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
