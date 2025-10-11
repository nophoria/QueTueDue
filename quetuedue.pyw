# QueTueDue v0.5

__version__ = "0.5"

# Import dependecies
import sys
import os
import re

from PyQt6.QtCore import(
    QSize,
    Qt,
    QMimeData
)
from PyQt6.QtGui import(
    QIcon,
    QAction,
    QFont,
    QFontDatabase,
    QDrag
)
from PyQt6.QtWidgets import(
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QWidget,
    QTextEdit,
    QCheckBox,
    QHBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QToolBar,
    QComboBox,
    QFrame,
    QSpacerItem,
    QSizePolicy
)

# Define config file paths.
USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__),
                 "config",
                 "config.config"
                 )
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__),
                                 "config",
                                 "default.config"
                                 )

def config_arg_load(keyword, acceptedValues):
    """Loads a config setting from a defined keyword in the config file.
    If the setting saved in the config.config file is invalid, blank or
    not there it will default to the specified setting in 
    default.config.
    """
    with open(USER_CONFIG_PATH, "r") as f:
        for line in f:
            if line.startswith(keyword):
                phrase =  line.strip().split("=", 1)[1]
                if phrase.strip() != "" and phrase in acceptedValues:
                    return phrase

    with open(DEFAULT_CONFIG_PATH, "r") as f:
        for line in f:
            if line.startswith(keyword):
                return line.strip().split("=", 1)[1]

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



# Define Constants
THEME = config_arg_load("theme", ["dark", "light"])
ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icons")
FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts")
TODO_PATH = os.path.join(os.path.dirname(__file__), "assets", "to-do.txt")
HIDE_WHEN_CLOSED = config_arg_load("HideWhenClosed", ["True", "False"])



class AddWindow(QWidget):
    """The window pop-up for the add task toolbar action."""
    def __init__(self, MainWindow_instance):
        super().__init__()
        self.setWindowTitle("QueTueDue - Add a task")

        # Layouts
        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Widgets
        self.label = QLabel("Add a new task")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                | Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel("Enter the new task below in the text box")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                   | Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.input = QLineEdit()
        self.yes_button = QPushButton("Add")
        self.no_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sub_label)
        self.layout.addWidget(self.input)
        self.layout.addLayout(self.button_layout)
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
        self.close()

    def exit(self):
        self.close()


class DelWindow(QWidget):
    """The window pop-up for the Remove action on the toolbar."""
    def __init__(self, MainWindow_instance):
        super().__init__()
        self.setWindowTitle("QueTueDue - Remove a task")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel("Remove a task")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                | Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel("Pick a task below in the drop-down to remove")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                   | Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.task_list = QComboBox()
        self.yes_button = QPushButton("Remove")
        self.no_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        with open(TODO_PATH, "r+", encoding="utf-8") as f:
            for line in f:
                # TODO: this causes newlines at the end of every object
                # except last one.
                if line.strip():
                    task_text = re.split("t|i|d", line, maxsplit=1)[1]
                    self.task_list.addItem(task_text)
        self.layout.addWidget(self.label)
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
        prefixes = [f"t{task_to_del}", f"i{task_to_del}", f"d{task_to_del}"]

        with open(TODO_PATH, "r") as f:
            lines = f.readlines()
        
        lines = [line for line in lines if line not in prefixes]

        with open(TODO_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        self.app_window.load_checkboxes()
        self.close()
    
    def exit(self):
        self.close()

class DelDoneWindow(QWidget):
    """The window pop-up for the Remove all done toolbar action."""
    def __init__(self, MainWindow_instance):
        super().__init__()
        self.setWindowTitle("QueTueDue - Remove all done")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel("Remove done tasks.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                | Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel("if you see this then something has not applied"
        " (or ran) :3")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                   | Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.yes_button = QPushButton("Remove")
        self.no_button = QPushButton("Cancel")

        self.app_window.setMinimumSize(400, 250)
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addWidget(self.label)
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
        label_text = "Are you sure you want to remove \""
        
        with open(TODO_PATH, "r") as f:
            done_tasks = []

            for line in f:
                if line.startswith("d"):
                    done_tasks.append(line.strip()[1:])
            
        if len(done_tasks) > 0:
            label_text += f"{done_tasks[0]}\"?"
        else:
            label_text = "There are no done tasks"
            self.yes_button.setEnabled(False)

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
        self.close()

    def exit(self):
        self.close()

class DelAllWindow(QWidget):
    """The window pop-up for the Remove ALL Items toolbar action."""
    def __init__(self, MainWindow_instance):
        super().__init__()
        self.setWindowTitle("QueTueDue - Remove all done")

        self.app_window = MainWindow_instance
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel("Remove\nALL\ntasks.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                | Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("", 32))
        self.sub_label = QLabel("if you see this then something has not applied"
        " (or ran) :3")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                   | Qt.AlignmentFlag.AlignTop)
        self.sub_label.setWordWrap(True)
        self.yes_button = QPushButton("Remove")
        self.no_button = QPushButton("Cancel")

        self.app_window.setMinimumSize(400, 250)
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        self.layout.addWidget(self.label)
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
        label_text = "Are you sure you want to remove \""
        
        with open(TODO_PATH, "r") as f:
            tasks = []

            for line in f:
                if line:
                    tasks.append(line[1:])
            
        if len(tasks) > 0:
            label_text += f"{tasks[0]}\"?"
        else:
            label_text = "There are no tasks"
            self.yes_button.setEnabled(False)

        if not len(tasks) - 1 < 2:
            label_text += f" and {len(tasks) - 1} others?"
        elif not len(tasks) - 1 < 1:
            label_text += f" and {len(tasks) - 1} other?"

        return label_text

    def exit(self):
        """Closes the window pop-up."""
        self.close()
    
    def DelAllSureWindow(self):
        """Shows the confirm window pop-up."""
        self.w = DelAllSureWindow(self)
        self.w.show()

class DelAllSureWindow(QWidget):
    """The window pop-up that asks the user to confirm removing all
    tasks via the Remove ALL Items toolbar action.
    """
    def __init__(self, DelAllWindowInstance):
        super().__init__()

        self.app_window = DelAllWindowInstance
        self.label = QLabel("Are you VERY sure you want to "
        "PERMANENTLY DELETE ALL ITEMS?!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("", 20))
        self.yes_button = QPushButton("Remove ALL ITEMS")
        self.no_button = QPushButton("Nevermind")
        
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
        with open(TODO_PATH, "w") as f:
            pass

        self.app_window.app_window.load_checkboxes()
        self.app_window.close()
        self.close()

    def exit(self):
        self.close()

class MainWindow(QMainWindow):
    """The main app window containing all the categories, tasks toolbars
    and more.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QueTueDue")
        self.setWindowIcon(QIcon(os.path.join(ICON_PATH,
                           f"logo.svg")))

        # Layout
        self.main_layout = QVBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.todo_layout = QVBoxLayout()
        self.in_prog_layout = QVBoxLayout()
        self.done_layout = QVBoxLayout()

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
        
        # Widgets
        self.about_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum,
                                       QSizePolicy.Policy.Expanding)
        self.about_label = QLabel(f"QueTueDue V{__version__}")
        self.about_Separator = separator("h")
        self.main_layout.addItem(self.about_spacer)
        self.main_layout.addWidget(self.about_Separator)
        self.main_layout.addWidget(self.about_label)

        self.todo_header = QLabel("To-Do")
        self.todo_header.setFont(QFont("", 20))
        self.todo_layout.addWidget(self.todo_header)
        self.todo_header.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                     | Qt.AlignmentFlag.AlignTop)

        self.in_prog_header = QLabel("In Progress")
        self.in_prog_header.setFont(QFont("", 20))
        self.in_prog_layout.addWidget(self.in_prog_header)
        self.in_prog_header.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                       | Qt.AlignmentFlag.AlignTop)

        self.done_header = QLabel("Done :)")
        self.done_header.setFont(QFont("", 20))
        self.done_layout.addWidget(self.done_header)
        self.done_header.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                     | Qt.AlignmentFlag.AlignTop)

        self.toolbar = QToolBar("Utilities")
        self.addToolBar(self.toolbar)

        self.add_action = QAction(QIcon(os.path.join(ICON_PATH,
                                 f"add_task_icon_{THEME}.png")),
                                 "Add", self)
        self.add_action.setStatusTip("Add a new task")
        self.add_action.triggered.connect(self.add_task_window)

        self.del_action = QAction(QIcon(os.path.join(ICON_PATH,
                                 f"del_task_icon_{THEME}.png")),
                                 "Remove", self)
        self.del_action.setStatusTip("Remove a task")
        self.del_action.triggered.connect(self.del_task_window)

        self.del_done_action = QAction(QIcon(os.path.join(ICON_PATH,
                                     f"del_done_icon_{THEME}.png")),
                                     "Remove Done", self)
        self.del_done_action.setStatusTip("Remove all tasks marked as done")
        self.del_done_action.triggered.connect(self.del_done_window)

        self.del_all_action = QAction(QIcon(os.path.join(ICON_PATH,
                                    f"del_all_icon_{THEME}.png")),
                                    "Remove ALL Items", self)
        self.del_all_action.setStatusTip("Remove ALL ITEMS PERMANENTLY")
        self.del_all_action.triggered.connect(self.del_all_window)

        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.del_action)
        self.toolbar.addAction(self.del_done_action)
        self.toolbar.addAction(self.del_all_action)

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
        self.open_app_tray_action.setIcon(QIcon(os.path.join(ICON_PATH,
                                       f"open_app_icon_{THEME}.png")))

        self.quit_app_tray_action = QAction("𝗤𝘂𝗶𝘁 𝗤𝘂𝗲𝗧𝘂𝗲𝗗𝘂𝗲")
        self.quit_app_tray_action.triggered.connect(self.quit_app)
        self.quit_app_tray_action.setIcon(QIcon(os.path.join(ICON_PATH,
                                       f"quit_app_icon_{THEME}.png")))

        self.tray.setContextMenu(self.tray_menu)

        self.load_checkboxes()
        container = QWidget()
        container.setLayout(self.main_layout)


        self.setCentralWidget(container)
    
    def clearCheckboxes(self, layout):
        """Removes all widgets in a given layout."""
        for i in reversed(range(1, layout.count())):
            task = layout.takeAt(i)
            widget = task.widget()
            if widget:
                widget.deleteLater()
        
    def load_checkboxes(self):
        """Clears layouts and system tray list and re-adds checkboxes
        from to-do.txt.
        """

        # Clear checkboxes
        self.clearCheckboxes(self.todo_layout)
        self.clearCheckboxes(self.in_prog_layout)
        self.clearCheckboxes(self.done_layout)
        
        # Clear and re-add static tray tasks (except open full app).
        self.tray_menu.clear()
        
        self.tray_actions = []
        self.tray_menu.addAction(self.title_action)
        self.tray_menu.addSeparator()

        with open(TODO_PATH, "r") as f:
            checkbox = ""
            for line in f:
                if not line.strip():
                    continue

                self.blockSignals(True)
                
                task_text = line[1:].strip()
                checkbox = QCheckBox(task_text)

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
                checkbox.stateChanged.connect(lambda state,
                                              cb=checkbox:
                                              self.moveCheckbox(cb, state))

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

    def add_task_window(self, checked=False):
        """Open the Add task toolbar task window pop-up."""
        self.w = AddWindow(self)
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

            lines = [line for line in lines if not any(line.startswith(p) for
                     p in prefixes)]
            lines = [line for line in lines if line.strip()]
            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            with open(TODO_PATH, "a", encoding="utf-8") as f:
                f.write(f"\nt{text}")

        elif state == 1:
            self.in_prog_layout.addWidget(cb)

            with open(TODO_PATH, "r") as f:
                lines = f.readlines()

            lines = [line for line in lines if not any(line.startswith(p) for
                     p in prefixes)]
            lines = [line for line in lines if line.strip()]

            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            with open(TODO_PATH, "a", encoding="utf-8") as f:
                f.write(f"\ni{text}")

        elif state == 2:
            self.done_layout.addWidget(cb)

            with open(TODO_PATH, "r") as f:
                lines = f.readlines()

            lines = [line for line in lines if not any(line.startswith(p) for
                     p in prefixes)]

            with open(TODO_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            with open(TODO_PATH, "a", encoding="utf-8") as f:
                f.write(f"\nd{text}")


app = QApplication(sys.argv)
# app.setStyle("Fusion")
mainWindow = MainWindow()
mainWindow.show()
app.exec()
