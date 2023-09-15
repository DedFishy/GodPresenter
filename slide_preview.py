from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui
from os.path import exists
from cache import Cache
from library import LibraryManager

class SlidePreview(QWidget):
    """
    Custom Qt Widget to show a preview of a slide
    """

    FONT = QFont("Helvetica", 10, QFont.Bold)
    PLAY_FONT = QFont("Helvetica", 20, QFont.Bold)

    def __init__(self, text=None, background=None, video=None, size=QtCore.QSize(100, 100), show_function = lambda *args: None, item = None, index = None, playlist = None, use_context_menu=True, library: LibraryManager = None, *args, **kwargs):
        super(SlidePreview, self).__init__(*args, **kwargs)

        self._layout = QGridLayout()

        self._size = size

        if use_context_menu:
            self._context_menu = QMenu(self)
            self._context_menu.addAction("Quick Edit").triggered.connect(self.quick_edit)
            self.library = library

        self._background = QLabel()
        self._text = QLabel()
        self._video = QLabel()
        self._selectedline = QFrame()
        lineheight = 5
        self._selectedline.setMinimumSize(size.width(), lineheight)
        self._selectedline.setMaximumSize(size.width(), lineheight)
        self._selectedline.setStyleSheet("background-color: transparent")

        self.text = text
        self.background = background
        self.video = video

        self.show_function = show_function
        self.item = item
        self.index = index
        self.playlist = playlist

        self._text.setWordWrap(True)
        self._text.setFont(self.FONT)
        self._text.setAlignment(QtCore.Qt.AlignCenter)
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(1, 1)
        shadow.setBlurRadius(15)
        self._text.setGraphicsEffect(shadow)

        self._video.setFont(self.PLAY_FONT)

        if background:
            self.setup_background(background)

        if text:
           self.setup_text(text)
        
        if video:
            self._video.setText(video)
        
        self._layout.addWidget(self._background, 0,0,1,1, QtCore.Qt.AlignHCenter)
        self._layout.addWidget(self._text, 0,0,1,1, QtCore.Qt.AlignHCenter)
        self._layout.addWidget(self._video, 0,0,1,1, QtCore.Qt.AlignHCenter)
        self._layout.addWidget(self._selectedline, 1,0,1,1)


        self.setLayout(self._layout)

        self.setMaximumSize(size)
        self.setMinimumSize(size)
    
    def contextMenuEvent(self, event):
        self._context_menu.exec(event.globalPos())
    
    def quick_edit(self, e):
        text, ok = QInputDialog.getMultiLineText(self, 'Slide Text', 'Set the slide\'s text', self._text.text())
        if ok:
            self.setup_text(text)
            self.text = text
            self.library.edit_slide(self.playlist, self.item, self.index, text=text)
    
    def setSelected(self, selected):
        if selected:
            self._selectedline.setStyleSheet("background-color: white")
        else:
            self._selectedline.setStyleSheet("background-color: transparent")
    
    def setup_video(self, video):
        if video is not None:
            self._video.setText(video)
        else:
            self._video.setText("")
        self.video = video
    
    def setup_background(self, background):
        if not background:
            self._background.clear()
            return
        if not exists(background):
            background = "nomedia.png"

        if not background in list(Cache.PREVIEW_PIXMAPS.keys()):

            background_map = QPixmap(background)
            background_map = background_map.scaled(self._size, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation)
            Cache.PREVIEW_PIXMAPS[background] = background_map
        else:
            background_map = Cache.PREVIEW_PIXMAPS[background]
        self._background.setPixmap(background_map)
        self.background = background
    
    def setup_text(self, text):
        self._text.setText(text)
        self.text = text

    def mousePressEvent(self, a0):
        if a0.button() == QtCore.Qt.LeftButton:
            self.show_function(self, self.item, self.index, self.text, self.background, self.video)