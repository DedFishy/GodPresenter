from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import qdarktheme
from library import LibraryManager
from slide_preview import SlidePreview
from flow_layout import FlowLayout

class App:
    def __init__(self):
        self.app = QApplication([])
        qdarktheme.setup_theme()
        self.app.setStyle("WindowsVista")
        self.app.setWindowIcon(QIcon("icon.ico"))
        self.window = QWidget()
        self.window.setWindowTitle("GodPresenter")
        self.window.setMinimumSize(500, 500)
        #self.window.showMaximized()
        self.layout = QVBoxLayout()
        self.layout.setDirection(0)
        self.window.setLayout(self.layout)

        self.desktop = QDesktopWidget()

        self.audience_display = 1 #TODO: Make this a setting
        self.audience_display_size = self.desktop.screenGeometry(self.audience_display)

        self.preview_size = self.audience_display_size.size()
        self.preview_size.scale(300, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        
        self.library_manager = LibraryManager()

        self.add_widgets()

        self.load_playlists()
    
    def add_playlist_callback(self):
        print("Add a playlist")
        item = QListWidgetItem()
        item.setText("poopy!")
        self.playlists.addItem(item)
    
    def add_playlist_item_callback(self):
        print("Add a playlist item")
        item = QListWidgetItem()
        item.setText("poopy!")
        self.playlist_items.addItem(item)
    
    def load_playlists(self):
        for playlist in self.library_manager.get_playlists():
            item = QListWidgetItem()
            item.setText(playlist)
            self.playlists.addItem(item)
    
    def load_playlist_items(self, playlist):
        self.playlist_items.clear()
        self.remove_prev_item_slides()
        for pl_item in self.library_manager.get_playlist_items(playlist):
            item = QListWidgetItem()
            item.setText(pl_item)
            self.playlist_items.addItem(item)

            self.presentation_tab_layout.addWidget(QLabel(pl_item))
            self.load_item_slides(pl_item)
    
    def remove_prev_item_slides(self):
        while (olditem := self.presentation_tab_layout.takeAt(0)) is not None:
            olditem.widget().deleteLater()
    
    def load_item_slides(self, item):
        self.window.setEnabled(False)
        
        i = 0

        for it_slide in self.library_manager.get_playlist_item_slides(self.playlists.selectedItems()[0].text(), item):
            slide = SlidePreview(it_slide["text"], it_slide["background"], self.preview_size)
            self.presentation_tab_layout.addWidget(slide)
            i += 1

        self.window.setEnabled(True)
    
    def add_widgets(self):

        # Splitter view
        self.splitter = QSplitter()

        # The container for the library items
        self.library = QFrame()
        self.library_layout = QVBoxLayout()
        self.library.setLayout(self.library_layout)

        # The playlist section

        #  The playlist header
        self.playlists_head = QFrame()
        self.playlists_head.setContentsMargins(0, 0, 0, 0)
        self.playlists_head_layout = QVBoxLayout()
        self.playlists_head.setLayout(self.playlists_head_layout)
        self.playlists_head_layout.setDirection(0)

        self.add_playlist = QToolButton()
        self.add_playlist.setText("+")
        self.add_playlist.clicked.connect(self.add_playlist_callback)
        self.playlists_head_layout.addWidget(QLabel("Playlists"))
        self.playlists_head_layout.addWidget(self.add_playlist)
        self.library_layout.addWidget(self.playlists_head)

        self.playlists = QListWidget()
        self.playlists.setResizeMode(QListView.Fixed)
        self.library_layout.addWidget(self.playlists)
        self.playlists.clicked.connect(lambda index: self.load_playlist_items(index.data()))

        # The playlist item section

        #  The playlist item header
        self.playlist_items_head = QFrame()
        self.playlist_items_head.setContentsMargins(0, 0, 0, 0)
        self.playlist_items_head_layout = QVBoxLayout()
        self.playlist_items_head.setLayout(self.playlist_items_head_layout)
        self.playlist_items_head_layout.setDirection(0)

        self.add_playlist_items = QToolButton()
        self.add_playlist_items.setText("+")
        self.add_playlist_items.clicked.connect(self.add_playlist_item_callback)
        self.playlist_items_head_layout.addWidget(QLabel("Items"))
        self.playlist_items_head_layout.addWidget(self.add_playlist_items)
        self.library_layout.addWidget(self.playlist_items_head)

        self.playlist_items = QListWidget()
        self.playlist_items.setResizeMode(QListView.Fixed)
        self.library_layout.addWidget(self.playlist_items)
        self.playlist_items.clicked.connect(lambda index: self.load_item_slides(index.data()))

        # The main view with tabs
        self.tabs = QTabWidget()
        self.presentation_tab = QWidget()
        self.edit_tab = QWidget()

        # Presentation tab
        self.presentation_tab_scroll = QScrollArea()
        self.presentation_tab_scroll_container = QVBoxLayout()
        self.presentation_tab.setLayout(self.presentation_tab_scroll_container)
        self.presentation_tab_scroll_container.addWidget(self.presentation_tab_scroll)

        self.presentation_tab_scroll_inner = QFrame()
        self.presentation_tab_layout = FlowLayout()
        self.presentation_tab_scroll_inner.setLayout(self.presentation_tab_layout)

        self.presentation_tab_scroll.setWidget(self.presentation_tab_scroll_inner)
        self.presentation_tab_scroll.setWidgetResizable(True)
        self.presentation_tab_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.tabs.addTab(self.presentation_tab, "Presentation")
        self.tabs.addTab(self.edit_tab, "Edit")

        # The display view part
        self.display_view = QFrame()
        self.display_view_layout = QVBoxLayout()
        self.display_view.setLayout(self.display_view_layout)

        self.display_view_layout.addWidget(QLabel("Display"))

        # Adding it all to the splitter
        self.splitter.addWidget(self.library)
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.display_view)

        self.layout.addWidget(self.splitter)
    
    def run(self):
        self.window.show()
        self.app.exec()

app = App()
app.run()