import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QMainWindow, QMenuBar
from PyQt5.QtGui import QIcon
from state_manager import State


class MHoverAbleButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.setIconSize(self.size())
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,0.1);
            }
        """)


class LoopCheckBox(MHoverAbleButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setChecked(False)
        self.update_button_icon()
        self.clicked.connect(self.toggle_looping)

    def update_button_icon(self):
        state = State.get().access()
        if state.is_looping:
            self.setIcon(QIcon("resources/images/icon_loop.png"))
        else:
            self.setIcon(QIcon("resources/images/icon_dont_loop.png"))

    def toggle_looping(self):
        state = State.get().access()
        state.is_looping = not state.is_looping
        self.update_button_icon()


class PlayStopButton(MHoverAbleButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_button_icon()
        self.clicked.connect(self.toggle_music)

    def update_button_icon(self):
        state = State.get().access()
        if state.is_playing:
            self.setIcon(QIcon("resources/images/icon_pause.png"))
        else:
            self.setIcon(QIcon("resources/images/icon_play.png"))

    def toggle_music(self):
        state = State.get().access()
        state.is_playing = not state.is_playing
        self.update_button_icon()


class MenuBarController(QMenuBar):
    @staticmethod
    def create_bar(parent):
        bar = QtWidgets.QMenuBar(parent)
        bar.setGeometry(0, 0, 800, 21)
        bar.setObjectName("menubar")
        bar.menuFile = QtWidgets.QMenu("File", bar)
        bar.menuFile.setObjectName("menuFile")

        bar.menuOptions = QtWidgets.QMenu("Help", bar)
        bar.menuOptions.setObjectName("menuOptions")

        bar.actionOpen = QtWidgets.QAction("Open", bar)
        bar.actionOpen.setObjectName("actionOpen")
        bar.actionExport_As = QtWidgets.QAction("Export As", bar)
        bar.actionExport_As.setObjectName("actionExport_As")
        bar.actionClose = QtWidgets.QAction("Close", bar)
        bar.actionClose.setObjectName("actionClose")
        bar.actionManual = QtWidgets.QAction("Manual", bar)
        bar.actionManual.setObjectName("actionManual")
        bar.actionConfig = QtWidgets.QAction("Properties", bar)
        bar.actionConfig.setObjectName("actionConfig")

        bar.menuFile.addAction(bar.actionOpen)
        bar.menuFile.addAction(bar.actionExport_As)
        bar.menuFile.addAction(bar.actionClose)

        bar.menuOptions.addAction(bar.actionManual)
        bar.menuOptions.addAction(bar.actionConfig)

        bar.addMenu(bar.menuFile)
        bar.addMenu(bar.menuOptions)

        return bar



class MainWindow(QMainWindow):

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("M_o_u_s_e Music Player")
        state = State().get().access()
        self.setGeometry(state.preferred_x, state.preferred_y, state.preferred_width, state.preferred_height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.menubar = MenuBarController.create_bar(self)
        self.setMenuBar(self.menubar)

    def __init__(self):
        super().__init__()
        self.setupUi()
        layout = QHBoxLayout()
        self.play_stop_button = PlayStopButton(self)
        self.looping_checkbox = LoopCheckBox(self)
        layout.addWidget(self.play_stop_button)
        layout.addWidget(self.looping_checkbox)
        self.centralwidget.setLayout(layout)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
