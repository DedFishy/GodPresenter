from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from os.path import exists
from cache import Cache

class SlidePreview(QWidget):
    """
    Custom Qt Widget to show a preview of a slide
    """

    def __init__(self, text=None, background=None, size=QtCore.QSize(100, 100), *args, **kwargs):
        super(SlidePreview, self).__init__(*args, **kwargs)

        self._layout = QGridLayout()

        self._background = QLabel()
        self._text = QLabel()

        if background:
            if not exists(background):
                background = "nomedia.png"

            if not background in list(Cache.PIXMAPS.keys()):

                background_map = QPixmap(background)
                background_map = background_map.scaled(size, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation)
                Cache.PIXMAPS[background] = background_map
            else:
                background_map = Cache.PIXMAPS[background]
            self._background.setPixmap(background_map)

        if text:
           self._text.setText(text)
        
        self._layout.addWidget(self._background, 0,0,1,1, QtCore.Qt.AlignHCenter)
        self._layout.addWidget(self._text, 0,0,1,1, QtCore.Qt.AlignHCenter)


        self.setLayout(self._layout)

        self.setMaximumSize(size)
        self.setMinimumSize(size)