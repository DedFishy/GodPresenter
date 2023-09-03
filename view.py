from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from os.path import exists
from cache import Cache
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
class View:

    FONT = QFont("Helvetica", 54, QFont.Bold)

    def __init__(self, index, size: QRect):
        self.window = QWidget()
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.window.setWindowFlags(flags)
        monitor = QDesktopWidget().screenGeometry(index)
        self.window.move(monitor.left(), monitor.top())
        self.window.showFullScreen()
        self.window.setMinimumSize(size.width(), size.height())
        self.layout = QGridLayout()
        self.window.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        self.size = size.size()

        self.add_widgets()
    
    def add_widgets(self):
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("icon.ico"))
        self.layout.addWidget(self.logo, 0,0,1,1, Qt.AlignHCenter)

        self.background = QLabel()
        self.text = QLabel()
        self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video = QVideoWidget()
        self.video_player.setVideoOutput(self.video)

        self.text.setWordWrap(True)
        self.text.setFont(self.FONT)
        self.text.setAlignment(Qt.AlignCenter)
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(1, 1)
        shadow.setBlurRadius(15)
        self.text.setGraphicsEffect(shadow)

        self.layout.addWidget(self.background, 0,0,1,1, Qt.AlignHCenter)
        self.layout.addWidget(self.text, 0,0,1,1, Qt.AlignHCenter)
        self.layout.addWidget(self.video, 0,0,1,1, Qt.AlignHCenter)

        self.video.setFixedSize(self.size)
        self.video.hide()
    
    def showText(self, text):
        self.logo.hide()
        self.video_player.stop()
        self.video.hide()
        self.text.hide()
        self.text.setText(text)
        self.text.show()

    def showBackground(self, background):
        self.logo.hide()
        self.video_player.stop()
        self.video.hide()
        self.background.show()
        if not background:
            self.background.clear()
            return
        if not exists(background):
            background = "nomedia.png"

        if not background in list(Cache.DISPLAY_PIXMAPS.keys()):

            background_map = QPixmap(background)
            background_map = background_map.scaled(self.size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            Cache.DISPLAY_PIXMAPS[background] = background_map
        else:
            background_map = Cache.DISPLAY_PIXMAPS[background]
        self.background.setPixmap(background_map)
    
    def showVideo(self, video):
        self.logo.hide()
        self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(video)))
        if video is not None:
            self.background.hide()
            self.text.hide()
            self.video.show()
            self.video_player.play()
    
    def run(self):
        self.window.show()