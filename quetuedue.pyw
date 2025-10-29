# QueTueDue v0.6-b3

__version__ = "v0.6-b3"

# Import dependecies
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
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    QToolBar,
    QVBoxLayout,
    QWidget,
)

# Define Constants
ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icons")
FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts")
TODO_PATH = os.path.join(os.path.dirname(__file__), "assets", "to-do.txt")
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.config")
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "default.config")
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


class AddWindow(QWidget):
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
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
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
        self.no_button.pressed.connect(self.exit)
        self.yes_button.pressed.connect(self.append_new_task)
        self.setLayout(self.layout)

    def append_new_task(self):
        """Add a task to the to-do list by appending a line to the todo
        file in the to-do category (t).
        """
        with open(TODO_PATH, "a", encoding="utf-8") as f:
            line = self.input.text()
            f.write(f"\nt{line}")

        self.app_window.load_checkboxes()
        self.app_window.change_page(self.app_window.main_page, "Tasks")

    def check_for_duplicates(self):
        """Constantly recieves what's in the self.input line edit and
        checks if a task with the same name already exists or if the
        line edit is blank. If it does, the function will grey-out the
        "Add" (self.yes_button) button and set the text to "Task already
        exists".
        """
        with open(TODO_PATH, "r") as f:
            lines = f.readlines()

        line = self.input.text()

        if f"t{line}" in lines or f"i{line}" in lines or f"d{line}" in lines:
            self.yes_button.setEnabled(False)
            self.yes_button.setText("Task already exists")
        elif line.strip() == "":
            self.yes_button.setEnabled(False)
            self.yes_button.setText("Enter a task name")
        else:
            self.yes_button.setEnabled(True)
            self.yes_button.setText("Add")

    def exit(self):
        self.app_window.change_page(self.app_window.main_page, "Tasks")


class DelWindow(QWidget):
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
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
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
        with open(TODO_PATH, "r") as f:
            if not f.read():
                self.yes_button.setEnabled(False)
                self.yes_button.setText("No tasks")
        self.no_button = QPushButton("Cancel")
        self.yes_button.setFont(QFont(self.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.families[4][0]))
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        with open(TODO_PATH, "r+", encoding="utf-8") as f:
            for line in f.readlines():
                if line.strip():
                    task_text = re.split("t|i|d", line, maxsplit=1)[1]
                    task_text = task_text.strip("\n")
                    self.task_list.addItem(task_text)
        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.sub_label)
        self.layout.addWidget(self.task_list)
        self.layout.addLayout(self.button_layout)
        self.yes_button.pressed.connect(self.del_task)
        self.no_button.pressed.connect(self.exit)
        self.setLayout(self.layout)

    def del_task(self):
        """Removes a task by filtering the lines in to-do.txt and
        re-writing the file with the filtered lines.
        """
        task_to_del = self.task_list.currentText()
        print(task_to_del)
        prefixes = [f"t{task_to_del}", f"i{task_to_del}", f"d{task_to_del}"]

        with open(TODO_PATH, "r") as f:
            lines = f.readlines()
            print(lines)

        lines = [line for line in lines if line.strip("\n") not in prefixes]
        print(lines)

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)

        self.app_window.load_checkboxes()
        self.app_window.change_page(self.app_window.main_page, "Tasks")

    def exit(self):
        self.app_window.change_page(self.app_window.main_page, "Tasks")


class MarkAllAsDoneWindow(QWidget):
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
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
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
        self.yes_button.pressed.connect(self.mark_all_as_done)
        self.no_button.pressed.connect(self.exit)
        self.setLayout(self.layout)

        self.sub_label.setText(self.gen_sub_label())

    def mark_all_as_done(self):
        """Reads the lines in assets/to-do.txt and replaces the first
        character in each with d to change the category to done."""
        with open(TODO_PATH, "r") as f:
            lines = f.readlines()

        lines = ["d" + line[1:] if line.strip() else line for line in lines]

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)

        self.app_window.load_checkboxes()
        self.app_window.change_page(self.app_window.main_page, "Tasks")

    def gen_sub_label(self):
        """Changes the text on a label to mention first affected task
        explicitly and x more.
        """
        label_text = 'Are you sure you want to mark off "'

        with open(TODO_PATH, "r") as f:
            tasks = []

            for line in f.readlines():
                if line:
                    tasks.append(line[1:])

        if len(tasks) > 0:
            label_text += f'{tasks[0]}"?'
        else:
            label_text = "There are no tasks"
            self.yes_button.setEnabled(False)
            self.yes_button.setText("No tasks")

        if not len(tasks) - 1 < 2:
            label_text += f" and {len(tasks) - 1} others?"
        elif not len(tasks) - 1 < 1:
            label_text += f" and {len(tasks) - 1} other?"

        return label_text

    def exit(self):
        """Sets the app page to MainWindow's main_page"""
        self.app_window.change_page(self.app_window.main_page, "Tasks")


class DelDoneWindow(QWidget):
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
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
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
        self.yes_button.pressed.connect(self.del_done)
        self.no_button.pressed.connect(self.exit)
        self.setLayout(self.layout)

        self.sub_label.setText(self.gen_sub_label())

    def gen_sub_label(self):
        """Changes the text on a label to mention first affected task
        explicitly and x more.
        """
        label_text = 'Are you sure you want to remove "'

        with open(TODO_PATH, "r") as f:
            done_tasks = []

            for line in f.readlines():
                if line.startswith("d"):
                    done_tasks.append(line.strip()[1:])

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

        return label_text

    def del_done(self):
        """Removes all lines in to-do.txt beginning with d (the done
        category).
        """
        with open(TODO_PATH, "r") as f:
            lines = f.readlines()

        lines = [line for line in lines if not line.startswith("d")]
        lines = [line for line in lines if line.strip()]

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)

        self.app_window.load_checkboxes()
        self.app_window.change_page(self.app_window.main_page, "Tasks")

    def exit(self):
        self.app_window.change_page(self.app_window.main_page, "Tasks")


class DelAllWindow(QWidget):
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
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
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
        self.yes_button.pressed.connect(self.DelAllSureWindow)
        self.no_button.pressed.connect(self.exit)
        self.setLayout(self.layout)

        self.sub_label.setText(self.gen_sub_label())

    def gen_sub_label(self):
        """Changes the text on a label to mention first affected task
        explicitly and x more.
        """
        label_text = 'Are you sure you want to remove "'

        with open(TODO_PATH, "r") as f:
            tasks = []

            for line in f.readlines():
                if line:
                    tasks.append(line[1:])

        if len(tasks) > 0:
            label_text += f'{tasks[0]}"?'
        else:
            label_text = "There are no tasks"
            self.yes_button.setEnabled(False)
            self.yes_button.setText("No tasks")

        if not len(tasks) - 1 < 2:
            label_text += f" and {len(tasks) - 1} others?"
        elif not len(tasks) - 1 < 1:
            label_text += f" and {len(tasks) - 1} other?"

        return label_text

    def exit(self):
        """Sets the app page to MainWindow's main_page"""
        self.app_window.change_page(self.app_window.main_page, "Tasks")

    def DelAllSureWindow(self):
        """Shows the confirm window pop-up."""
        self.w = DelAllSureWindow(self)
        self.w.show()


class DelAllSureWindow(QWidget):
    """The window pop-up that asks the user to confirm removing all
    tasks via the Remove ALL Items toolbar action.
    """

    def __init__(self, DelAllWindow_instance):
        super().__init__()
        self.app_window = DelAllWindow_instance
        self.setWindowTitle("Are you sure?")

        self.label = QLabel("Are you VERY sure you want to PERMANENTLY DELETE ALL ITEMS?!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(self.app_window.app_window.families[4][0], 32))
        self.yes_button = QPushButton("Remove ALL ITEMS")
        self.no_button = QPushButton("Nevermind")
        self.yes_button.setFont(QFont(self.app_window.app_window.families[4][0]))
        self.no_button.setFont(QFont(self.app_window.app_window.families[4][0]))

        self.yes_button.pressed.connect(self.delAllDone)
        self.no_button.pressed.connect(self.exit)

        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

    def delAllDone(self):
        with open(TODO_PATH, "w"):
            pass

        self.app_window.app_window.load_checkboxes()
        self.app_window.app_window.change_page(self.app_window.app_window.main_page, "Tasks")
        self.close()

    def exit(self):
        self.app_window.app_window.change_page(self.app_window.app_window.main_page, "Tasks")
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
                process.startDetached("python", [os.path.join(ROOT_PATH, "file_checker.py")])
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
        self.open_app_tray_action.setIcon(QIcon(os.path.join(ICON_PATH, f"open_app_icon_{THEME}.png")))

        self.quit_app_tray_action = QAction("𝗤𝘂𝗶𝘁 𝗤𝘂𝗲𝗧𝘂𝗲𝗗𝘂𝗲")
        self.quit_app_tray_action.triggered.connect(self.quit_app)
        self.quit_app_tray_action.setIcon(QIcon(os.path.join(ICON_PATH, f"quit_app_icon_{THEME}.png")))

        self.tray.setContextMenu(self.tray_menu)

        # Toolbar
        self.toolbar = QToolBar("Utilities")
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        self.add_action = QAction(QIcon(os.path.join(ICON_PATH, f"add_task_icon_{THEME}.png")), "Add", self)
        self.add_action.setStatusTip("Add a new task")
        self.add_action.triggered.connect(lambda: self.change_page(self.add_page, "Add a Task"))

        self.del_action = QAction(QIcon(os.path.join(ICON_PATH, f"del_task_icon_{THEME}.png")), "Remove", self)
        self.del_action.setStatusTip("Remove a task")
        self.del_action.triggered.connect(lambda: self.change_page(self.del_page, "Remove a Task"))

        self.mark_all_as_done_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"mark_all_as_done_icon_{THEME}.png")), "Mark all as Done", self
        )
        self.mark_all_as_done_action.setStatusTip("Mark all items off as Done")
        self.mark_all_as_done_action.triggered.connect(lambda: self.change_page(self.mark_off_page, "Mark all as Done"))

        self.del_done_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"del_done_icon_{THEME}.png")), "Remove Done", self
        )
        self.del_done_action.setStatusTip("Remove all tasks marked as done")
        self.del_done_action.triggered.connect(lambda: self.change_page(self.del_done_page, "Remove Done Tasks"))

        self.del_all_action = QAction(
            QIcon(os.path.join(ICON_PATH, f"del_all_icon_{THEME}.png")), "Remove ALL Items", self
        )
        self.del_all_action.setStatusTip("Remove ALL ITEMS PERMANENTLY")
        self.del_all_action.triggered.connect(lambda: self.change_page(self.del_all_page, "Remove ALL Tasks"))

        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.del_action)
        self.toolbar.addAction(self.mark_all_as_done_action)
        self.toolbar.addAction(self.del_done_action)
        self.toolbar.addAction(self.del_all_action)

        # Main layouts
        self.window_layout = QVBoxLayout()
        self.stack_layout = QStackedLayout()
        self.main_layout = QVBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.todo_layout = QVBoxLayout()
        self.todo_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.in_prog_layout = QVBoxLayout()
        self.in_prog_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.done_layout = QVBoxLayout()
        self.done_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
        self.header_menu_add.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_add)
        self.header_menu_remove = QAction("Remove")
        self.header_menu_remove.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_remove)
        self.header_menu_mark_off = QAction("Mark Off")
        self.header_menu_mark_off.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_mark_off)
        self.header_menu_edit = QAction("Edit")
        self.header_menu_edit.setFont(QFont(self.families[4][0]))
        self.header_menu.addAction(self.header_menu_edit)

        self.header_menu_button = QPushButton()
        self.header_menu_button.setIcon(QIcon(os.path.join(ICON_PATH, f"header_menu_icon_{THEME}.png")))
        self.header_menu_button.setIconSize(QSize(24, 24))
        self.header_menu_button.setFixedSize(48, 32)
        self.header_menu_button.setFlat(True)
        self.header_menu_button.setMenu(self.header_menu)

        self.header_page_label = QLabel("Tasks")
        self.header_page_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.header_page_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.header_page_label.setFont(QFont(self.families[4][0]))

        self.header_menu_layout.addWidget(self.header_menu_button)
        self.header_menu_layout.addWidget(self.header_page_label)

        self.header_label = QLabel("QueTueDue")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_label.setContentsMargins(0, 4, 0, 4)
        self.header_label.setFont(QFont(self.families[4], 12))

        self.header_sub_label = QLabel(f"{__version__}")
        self.header_sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.header_sub_label_palette = self.header_sub_label.palette()
        self.header_sub_label_palette.setColor(QPalette.ColorRole.WindowText, QColor(50, 50, 50))
        self.header_sub_label.setPalette(self.header_sub_label_palette)
        self.header_sub_label.setFont(QFont(self.families[4], 10))

        self.header_title_layout.addWidget(self.header_label)
        self.header_title_layout.addWidget(self.header_sub_label)

        self.header_layout.addLayout(self.header_menu_layout)
        self.header_layout.addStretch()
        self.header_layout.addLayout(self.header_title_layout)
        self.header_layout.addStretch()
        self.header_layout.addSpacing((self.header_menu_layout.sizeHint().width()))

        self.header_separator = separator("h")
        self.window_layout.addLayout(self.header_layout)
        self.window_layout.addWidget(self.header_separator)

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

        self.header_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addItem(self.header_spacer)

        self.todo_header = QLabel("To-Do")
        try:
            self.todo_header.setFont(QFont(self.families[0], 32))
        except IndexError:
            self.todo_header.setFont(QFont("", 32))
        self.todo_layout.addWidget(self.todo_header)
        self.todo_header.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.in_prog_header = QLabel("In Prog.")
        try:
            self.in_prog_header.setFont(QFont(self.families[0], 32))
        except IndexError:
            self.in_prog_header.setFont(QFont("", 32))
        self.in_prog_layout.addWidget(self.in_prog_header)
        self.in_prog_header.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.done_header = QLabel("Done :)")
        try:
            self.done_header.setFont(QFont(self.families[0], 32))
        except IndexError:
            self.done_header.setFont(QFont("", 32))
        self.done_layout.addWidget(self.done_header)
        self.done_header.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.load_checkboxes()
        container = QWidget()
        container.setLayout(self.main_layout)

        self.setCentralWidget(container)

        # Pages
        self.main_page = QWidget()
        self.main_page.setLayout(self.main_layout)
        self.stack_layout.addWidget(self.main_page)

        self.add_page = AddWindow(self)
        self.stack_layout.addWidget(self.add_page)

        self.del_page = DelWindow(self)
        self.stack_layout.addWidget(self.del_page)

        self.mark_off_page = MarkAllAsDoneWindow(self)
        self.stack_layout.addWidget(self.mark_off_page)

        self.del_done_page = DelDoneWindow(self)
        self.stack_layout.addWidget(self.del_done_page)

        self.del_all_page = DelAllWindow(self)
        self.stack_layout.addWidget(self.del_all_page)

        self.change_page(self.main_page, "Tasks")
        self.window_layout.addLayout(self.stack_layout)

        self.window_wrapper = QWidget()
        self.window_wrapper.setLayout(self.window_layout)
        self.setCentralWidget(self.window_wrapper)

    def clear_layout(self, layout, start):
        """Removes all widgets in a given layout."""
        for i in reversed(range(start, layout.count())):
            task = layout.takeAt(i)
            widget = task.widget()
            if widget:
                widget.deleteLater()

    def load_checkboxes(self):
        """Clears layouts and system tray list and re-adds checkboxes
        from to-do.txt.
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

        with open(TODO_PATH, "r") as f:
            checkbox = ""
            for line in f.readlines():
                if not line.strip():
                    continue

                self.blockSignals(True)

                task_text = line[1:].strip()
                checkbox = QCheckBox(task_text)

                max_width = max(50, int((self.width() / 3) - self.toolbar.width()))
                checkbox.setMaximumWidth(max_width)
                checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

                try:
                    checkbox.setFont(QFont(self.families[4]))
                except IndexError:
                    continue

                # Add checkboxes and tray tasks depending on category
                if line.startswith("t"):
                    checkbox.setCheckState(Qt.CheckState.Unchecked)
                    self.todo_layout.addWidget(checkbox)
                    checkbox_tray_action = QAction(task_text)
                    self.tray_actions.append(checkbox_tray_action)
                    self.tray_menu.addAction(checkbox_tray_action)
                elif line.startswith("i"):
                    checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
                    self.in_prog_layout.addWidget(checkbox)
                elif line.startswith("d"):
                    checkbox.setCheckState(Qt.CheckState.Checked)
                    self.done_layout.addWidget(checkbox)
                else:
                    continue

                self.blockSignals(False)

                checkbox.setProperty("task", task_text)
                checkbox.setTristate(True)
                checkbox.stateChanged.connect(lambda state, cb=checkbox: self.moveCheckbox(cb, state))

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

    def open_popup_window(self, WindowInstance, checked=False):
        """Open the specified popup window (WindowInstance). This is used for the
        toolbar and button actions."""
        self.w = WindowInstance(self)
        self.w.show()

    def open_app(self):
        """Open the main app when the Open full app system tray context
        menu option is triggered.
        """
        self.show()

    def quit_app(self):
        """Quit the whole process when the Quit QueTueDue system tray
        context menu option is triggered.
        """
        sys.exit()

    def moveCheckbox(self, cb, state):
        """Deletes specified task (cb) from to-do.txt and re-adds it
        with a new prefix based on the state (state) of the checkbox.
        """
        text = cb.text()
        prefixes = (f"t{text}", f"i{text}", f"d{text}")
        if state == 0:
            self.todo_layout.addWidget(cb)

            with open(TODO_PATH, "r") as f:
                lines = f.readlines()

            lines = [line for line in lines if not any(line.startswith(p) for p in prefixes)]
            lines = [line for line in lines if line.strip()]
            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            with open(TODO_PATH, "a", encoding="utf-8") as f:
                f.write(f"\nt{text}")

        elif state == 1:
            max_width = max(50, int((self.width() / 3) - self.toolbar.width()))
            cb.setMaximumWidth(max_width)
            cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.in_prog_layout.addWidget(cb)

            with open(TODO_PATH, "r") as f:
                lines = f.readlines()

            lines = [line for line in lines if not any(line.startswith(p) for p in prefixes)]
            lines = [line for line in lines if line.strip()]

            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            with open(TODO_PATH, "a", encoding="utf-8") as f:
                f.write(f"\ni{text}")

        elif state == 2:
            max_width = max(50, int((self.width() / 3) - self.toolbar.width()))
            cb.setMaximumWidth(max_width)
            cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.done_layout.addWidget(cb)

            with open(TODO_PATH, "r") as f:
                lines = f.readlines()

            lines = [line for line in lines if not any(line.startswith(p) for p in prefixes)]

            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            with open(TODO_PATH, "a", encoding="utf-8") as f:
                f.write(f"\nd{text}")

    def resizeEvent(self, event):
        self.load_checkboxes()
        super().resizeEvent(event)

    def change_page(self, page, header_label):
        if self.stack_layout.currentWidget() == page:
            self.stack_layout.setCurrentWidget(self.main_page)
            self.header_page_label.setText("Tasks")
            return
        self.stack_layout.setCurrentWidget(page)
        self.header_page_label.setText(header_label)


app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
app.exec()
