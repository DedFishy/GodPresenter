from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import qdarktheme
from library import LibraryManager
from slide_preview import SlidePreview
from flow_layout import FlowLayout
from view import View

class App:
    def __init__(self):
        self.app = QApplication([])
        qdarktheme.setup_theme()
        self.app.setStyle("WindowsVista")
        self.app.setWindowIcon(QIcon("icon.ico"))
        self.window = QWidget()
        self.window.setWindowTitle("GodPresenter")
        self.window.setMinimumSize(500, 500)
        self.window.showMaximized()
        def onclose(event):
            self.library_manager.save_library()
            self.app.quit()
        self.window.closeEvent = onclose
        self.layout = QVBoxLayout()
        self.layout.setDirection(0)
        self.window.setLayout(self.layout)

        self.desktop = QDesktopWidget()

        self.audience_display_index = 1 #TODO: Make this a setting
        self.audience_display_size = self.desktop.screenGeometry(self.audience_display_index)
        self.audience_display_enabled = False

        self.audience_display = View(self.audience_display_index, self.audience_display_size)

        self.preview_size = self.audience_display_size.size()
        self.preview_size.scale(300, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.header_font = QFont("Times", 10, QFont.Bold)

        self.selected_item = None
        self.selected_index = None

        self.item_frames = {}
        
        self.library_manager = LibraryManager()

        self.add_widgets()

        self.load_playlists()
    
    def add_playlist_callback(self):
        name, ok = QInputDialog.getText(self.window, 'New Playlist', 'What will the name of the playlist be?')
        if ok:
            self.library_manager.add_playlist(name)
            self.load_playlists()
    
    def add_playlist_item_callback(self):
        if len(self.playlists.selectedItems()) > 0:
            name, ok = QInputDialog.getText(self.window, 'New Playlist Item', 'What will the name of the item be?')
            if ok:
                selected_playlist = self.get_selected_playlist
                self.library_manager.add_playlist_item(selected_playlist, name)
                self.load_playlist_items(selected_playlist)
    
    def get_selected_playlist(self):
        return self.playlists.selectedItems()[0].text()
    
    def load_playlists(self):
        self.playlists.clear()
        for playlist in self.library_manager.get_playlists():
            item = QListWidgetItem()
            item.setText(playlist)
            self.playlists.addItem(item)
    
    def load_playlist_items(self, playlist):
        self.playlist_items.clear()
        self.remove_prev_item_slides()
        self.item_frames = {}
        for pl_item in self.library_manager.get_playlist_items(playlist):
            item = QListWidgetItem()
            item.setText(pl_item)
            self.playlist_items.addItem(item)

            item_label = QLabel(pl_item)
            item_label.setFont(self.header_font)
            self.presentation_tab_layout.addWidget(item_label)
            self.load_item_slides(pl_item)
    
    def remove_prev_item_slides(self):
        while (olditem := self.presentation_tab_layout.takeAt(0)) is not None:
            olditem.widget().deleteLater()
    
    def load_item_slides(self, item):
        item_frame = QFrame()
        item_layout = FlowLayout()
        item_frame.setLayout(item_layout)

        self.item_frames[item] = []

        i = 0

        selected_playlist = self.get_selected_playlist()

        for it_slide in self.library_manager.get_playlist_item_slides(selected_playlist, item):
            if it_slide["type"] == "text":
                slide = SlidePreview(it_slide["text"], it_slide["background"], None, self.preview_size, self.show_slide, item, i, playlist=selected_playlist, library=self.library_manager)
            elif it_slide["type"] == "video":
                slide = SlidePreview(None, None, it_slide["video"], self.preview_size, self.show_slide, item, i, playlist=selected_playlist, library=self.library_manager)
            item_layout.addWidget(slide)
            self.item_frames[item].append(slide)
            i += 1
        
        self.presentation_tab_layout.addWidget(item_frame)
    
    def show_slide(self, widget, item, index, text, background, video):
        if self.selected_item in list(self.item_frames.keys()):
            self.item_frames[self.selected_item][self.selected_index].setSelected(False)

        self.selected_item = item
        self.selected_index = index
        widget.setSelected(True)

        if background:
            self.display_preview.setup_background(background)
            self.audience_display.showBackground(background)

        self.display_preview.setup_text(text)
        self.audience_display.showText(text)

        if video:
            self.audience_display.showVideo(video)
    
    def clear_text(self):
        self.display_preview.setup_text("")
        self.audience_display.showText("")

    def clear_background(self):
        self.display_preview.setup_background(None)
        self.audience_display.showBackground(None)

    def clear_video(self):
        self.audience_display.showVideo(None)
    
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
        self.presentation_tab_layout = QVBoxLayout()
        self.presentation_tab_scroll_inner.setLayout(self.presentation_tab_layout)

        self.presentation_tab_scroll.setWidget(self.presentation_tab_scroll_inner)
        self.presentation_tab_scroll.setWidgetResizable(True)
        self.presentation_tab_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.tabs.addTab(self.presentation_tab, "Presentation")
        self.tabs.addTab(self.edit_tab, "Edit")

        # The display view part
        self.display_view = QFrame()
        self.display_view_layout = FlowLayout()
        self.display_view.setLayout(self.display_view_layout)

        self.display_preview = SlidePreview(None, None, None, self.preview_size, use_context_menu=False)
        self.display_view_layout.addWidget(self.display_preview)

        self.layer_control = QFrame()
        self.layer_control_layout = QHBoxLayout()
        self.layer_control.setLayout(self.layer_control_layout)

        self.clear_layer_label = QLabel("Clear")
        self.clear_text_button = QPushButton("Text")
        self.clear_text_button.clicked.connect(self.clear_text)
        self.clear_background_button = QPushButton("Background")
        self.clear_background_button.clicked.connect(self.clear_background)
        self.clear_video_button = QPushButton("Video")
        self.clear_video_button.clicked.connect(self.clear_video)

        self.layer_control_layout.addWidget(self.clear_layer_label)
        self.layer_control_layout.addWidget(self.clear_text_button)
        self.layer_control_layout.addWidget(self.clear_background_button)
        self.layer_control_layout.addWidget(self.clear_video_button)

        self.display_view_layout.addWidget(self.layer_control)

        self.display_checkboxes = QFrame()
        self.display_checkbox_layout = QHBoxLayout()
        self.display_checkboxes.setLayout(self.display_checkbox_layout)

        self.audience_display_checkbox = QCheckBox("Audience")
        self.stage_display_checkbox = QCheckBox("Stage")
        self.display_checkbox_layout.addWidget(self.audience_display_checkbox)
        self.display_checkbox_layout.addWidget(self.stage_display_checkbox)

        self.display_view_layout.addWidget(self.display_checkboxes)

        # Adding it all to the splitter
        self.splitter.addWidget(self.library)
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.display_view)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)

        self.layout.addWidget(self.splitter)
    
    def run(self):
        self.window.show()
        self.audience_display.run()
        self.app.exec()

app = App()
app.run()