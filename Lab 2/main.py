import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, QMenuBar
from PyQt5.QtGui import QIcon
from state_manager import State


class MHoverAbleButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(48, 48)
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
        track = State.get().access().track
        if track.is_playing:
            self.setIcon(QIcon("resources/images/icon_pause.png"))
        else:
            self.setIcon(QIcon("resources/images/icon_play.png"))

    def toggle_music(self):
        track = State.get().access().track
        track.is_playing = not track.is_playing
        self.update_button_icon()


class MenuBar(QMenuBar):
    def on_exit(self):
        self.parent_window.close()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setGeometry(0, 0, 800, 21)
        self.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu("File", self)
        self.menuFile.setObjectName("menuFile")

        self.menuOptions = QtWidgets.QMenu("Help", self)
        self.menuOptions.setObjectName("menuOptions")

        self.actionOpen = QtWidgets.QAction("Open", self)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExport_As = QtWidgets.QAction("Export As", self)
        self.actionExport_As.setObjectName("actionExport_As")
        self.actionClose = QtWidgets.QAction("Exit", self)
        self.actionClose.setObjectName("actionClose")
        self.actionClose.triggered.connect(self.on_exit)
        self.actionManual = QtWidgets.QAction("Manual", self)
        self.actionManual.setObjectName("actionManual")
        self.actionConfig = QtWidgets.QAction("Properties", self)
        self.actionConfig.setObjectName("actionConfig")

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionExport_As)
        self.menuFile.addAction(self.actionClose)

        self.menuOptions.addAction(self.actionManual)
        self.menuOptions.addAction(self.actionConfig)

        self.addMenu(self.menuFile)
        self.addMenu(self.menuOptions)


class ProgressBar(QVBoxLayout):
    def __init__(self, parent):
        super().__init__(parent)
        state = State.get().access()
        track = state.track
        self.name_label = QtWidgets.QLabel()
        self.name_label.setText(track.track_name)
        self.bar_layout = QHBoxLayout()
        self.current_time_label = QtWidgets.QLabel()
        self.current_time_label.setText(f"{track.current_second}")

        self.slider = QtWidgets.QSlider()

        self.duration_label = QtWidgets.QLabel()
        self.duration_label.setText(f"{track.duration_seconds}")

        self.bar_layout.addWidget(self.current_time_label)
        self.bar_layout.addWidget(self.slider)
        self.bar_layout.addWidget(self.duration_label)
        self.addWidget(self.name_label)
        self.addLayout(self.bar_layout)


class MainWindow(QMainWindow):

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("M_o_u_s_e Music Player")
        state = State().get().access()
        self.resize(state.preferred_width, state.preferred_height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

    def __init__(self):
        super().__init__()
        self.setupUi()

        self.layout = QVBoxLayout()
        self.tools = QHBoxLayout()
        self.bar = ProgressBar(self)
        self.layout.addLayout(self.bar)
        self.layout.addLayout(self.tools)
        self.play_stop_button = PlayStopButton(self)
        self.looping_checkbox = LoopCheckBox(self)
        self.tools.addWidget(self.play_stop_button)
        self.tools.addWidget(self.looping_checkbox)
        self.centralwidget.setLayout(self.layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
