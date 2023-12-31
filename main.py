from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import qdarktheme
from library import LibraryManager, NO_CONTENT
from slide_preview import SlidePreview
from flow_layout import FlowLayout
from view import View
from cache import Cache
from os.path import exists

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

        self.selected_editing = None

        self.loaded_editing_item = None

        self.current_editing_background = None
        self.current_editing_video = None

        self.item_frames = {}
        self.editor_item_frames = []
        
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
                selected_playlist = self.get_selected_playlist()
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
        item_layout.setAlignment(QtCore.Qt.AlignCenter)
        item_frame.setLayout(item_layout)

        self.item_frames[item] = []

        i = 0

        selected_playlist = self.get_selected_playlist()

        for it_slide in self.library_manager.get_playlist_item_slides(selected_playlist, item):
            if it_slide["type"] == "text":

                if not "text" in it_slide.keys():
                    it_slide["text"] = "Text"
                if not "background" in it_slide.keys():
                    it_slide["background"] = ""

                slide = SlidePreview(it_slide["text"], it_slide["background"], None, self.preview_size, self.show_slide, item, i, playlist=selected_playlist, library=self.library_manager, quick_edit_callback=self.quick_edit_callback)
            
            elif it_slide["type"] == "video":

                if not "video" in it_slide.keys():
                    it_slide["video"] = None

                slide = SlidePreview(None, None, it_slide["video"], self.preview_size, self.show_slide, item, i, playlist=selected_playlist, library=self.library_manager, quick_edit_callback=self.quick_edit_callback)
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
    
    def choose_slide_type(self):
        mode = self.editing_slide_type_dropdown.currentText()
        if mode == "text":
            self.edit_tab_text_pane.show()
            self.edit_tab_bg_button.show()
            self.edit_tab_bg_preview.show()
            self.edit_tab_bg_rem_button.show()

            self.edit_tab_video_button.hide()
            self.edit_tab_video_preview.hide()

            self.load_background_into_editor(self.current_editing_background)
        else:
            self.edit_tab_text_pane.hide()
            self.edit_tab_bg_button.hide()
            self.edit_tab_bg_rem_button.hide()
            self.edit_tab_bg_preview.hide()

            self.edit_tab_video_button.show()
            self.edit_tab_video_preview.show()
        self.edit_current_slide()

    def choose_slide_background(self):
        fileName, _ = QFileDialog.getOpenFileName(filter="PNG (*.png);;JPG (*.jpg);;JPEG (*.jpeg)")
        if fileName:
            self.current_editing_background = fileName
            self.edit_current_slide()
    
    def remove_slide_background(self):
        self.current_editing_background = None
        self.edit_current_slide()
    
    def choose_slide_video(self):
        fileName, _ = QFileDialog.getOpenFileName(filter="MP4 (*.mp4);;WEBM (*.webm);;MOV (*.mov)")
        if fileName:
            self.current_editing_video = fileName
            self.edit_current_slide()
    
    def edit_slide_text(self):
        self.edit_current_slide()

    def quick_edit_callback(self, text):

        self.load_item_into_editor(None)
    
    def edit_current_slide(self):
        text = self.editing_slide_text_in.toPlainText()
        mode = self.editing_slide_type_dropdown.currentText()
        background = self.current_editing_background

        if mode == "video":
            video = self.current_editing_video
        else:
            video = None

        if video:
            text = ""
            background = ""

        if self.selected_editing:

            # Get the slide data in the library
            #slide = self.library_manager.get_playlist_item_slides(self.selected_editing.playlist, self.selected_editing.item)[self.selected_editing.index]
            # Change the data in the library
            self.library_manager.edit_slide(self.selected_editing.playlist, self.selected_editing.item, self.selected_editing.index, mode, text, background, video)
            # Change the edit preview text
            self.selected_editing.setup_text(text)
            self.selected_editing.setup_background(background)
            self.selected_editing.setup_video(video)
            # Change the preview in the presenter tab
            presenter_slide = self.item_frames[self.loaded_editing_item][self.selected_editing.index]
            if presenter_slide:
                presenter_slide.setup_text(text)
                presenter_slide.setup_background(background)
                if mode != "video":
                    self.load_background_into_editor(background)
                else:
                    self.edit_tab_video_preview.setText(video)
                presenter_slide.setup_video(video)

    def remove_prev_editor_slides(self):
        while (olditem := self.edit_tab_slide_layout.takeAt(0)) is not None:
            olditem.widget().deleteLater()
        
        self.selected_editing = None

    def load_item_into_editor(self, item):
        self.loaded_editing_item = item
        self.editor_item_frames = []
        self.remove_prev_editor_slides()
        if item is None:
            return
        playlist = self.get_selected_playlist()

        i = 0

        for item_slide in self.library_manager.get_playlist_item_slides(playlist, item):
            #TODO: Here and in load_item_slides(), replace this if branch with something cleaner
            if item_slide["type"] == "text":
                slide = SlidePreview(item_slide["text"], item_slide["background"], None, self.preview_size, self.load_slide_into_editor, item, i, playlist=playlist, library=self.library_manager)
            elif item_slide["type"] == "video":
                if not "video" in item_slide.keys():
                    item_slide["video"] = None
                slide = SlidePreview(None, None, item_slide["video"], self.preview_size, self.load_slide_into_editor, item, i, playlist=playlist, library=self.library_manager)
            self.edit_tab_slide_layout.addWidget(slide)

            self.editor_item_frames.append(slide)

            slide.context_menu_function = self.editor_context_menu
            i += 1
    
    def load_background_into_editor(self, background):
        if background:
            self.edit_tab_bg_preview.show()
            if not exists(background):
                background = "nomedia.png"
            self.edit_tab_bg_preview.setPixmap(Cache.PREVIEW_PIXMAPS[background])
        else:
            self.edit_tab_bg_preview.hide()
    
    def load_slide_into_editor(self, preview: SlidePreview, item, index, text, background, video):

        self.current_editing_background = background
        self.current_editing_video = video

        preview.setSelected(True)
        if self.selected_editing:
                self.selected_editing.setSelected(False)
        self.selected_editing = preview

        slide_type = None
        if video is not None:
            slide_type = "video"
        else:
            slide_type = "text"
        
        self.editing_slide_type_dropdown.blockSignals(True)
        self.editing_slide_type_dropdown.setCurrentText(slide_type)
        self.editing_slide_type_dropdown.blockSignals(False)


        if slide_type == "text":
            
            self.editing_slide_text_in.blockSignals(True)
            self.editing_slide_text_in.setText(text)
            self.editing_slide_text_in.blockSignals(False)


            self.load_background_into_editor(background)
        else:
            self.editing_slide_text_in.setText("")

        self.choose_slide_type()
    
    def editor_context_menu(self, slide: SlidePreview, event: QContextMenuEvent):
        contextMenu = QMenu()
        add = contextMenu.addAction("Add")
        if slide:
            delete = contextMenu.addAction("Delete")
        else:
            delete = "disabled"
        action = contextMenu.exec_(self.window.mapToGlobal(event.globalPos()))
        if action == delete:
            slide.run_show_function()
            self.library_manager.delete_slide(slide.playlist, slide.item, slide.index)
            slide.deleteLater()
            presenter_slide = self.item_frames[self.loaded_editing_item][self.selected_editing.index]
            if presenter_slide:
                presenter_slide.deleteLater()
            
            self.selected_editing = None

            self.remove_prev_item_slides()
            self.load_playlist_items(self.get_selected_playlist())
            self.load_item_into_editor(self.loaded_editing_item)
        
        if action == add:
            if slide:
                self.library_manager.add_slide(slide.playlist, slide.item, slide.index)
            else:
                self.library_manager.add_slide(self.get_selected_playlist(), self.loaded_editing_item, 0)
            
            if self.selected_editing:
                index = self.selected_editing.index
            else:
                index = 0

            self.remove_prev_item_slides()
            self.load_playlist_items(self.get_selected_playlist())
            self.load_item_into_editor(self.loaded_editing_item)

            self.selected_item = None

            self.remove_prev_item_slides()
            self.load_playlist_items(self.get_selected_playlist())
            self.load_item_into_editor(self.loaded_editing_item)

            self.editor_item_frames[index].run_show_function()

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
        self.playlist_items.clicked.connect(lambda index: self.load_item_into_editor(index.data()))
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

        # Edit tab
        self.edit_tab_layout = QHBoxLayout()
        self.edit_tab.setLayout(self.edit_tab_layout)

        ## The edit tab view for the available slides in the selected item
        self.edit_tab_slide_list = QScrollArea()
        self.edit_tab_slide_list_layout = QVBoxLayout()
        self.edit_tab_slide_list.setLayout(self.edit_tab_slide_list_layout)
        self.edit_tab_layout.addWidget(self.edit_tab_slide_list)

        self.edit_tab_slide_list.contextMenuEvent = lambda event: self.editor_context_menu(None, event)

        self.edit_tab_slide_list_inner = QFrame()
        self.edit_tab_slide_layout = QVBoxLayout()
        self.edit_tab_slide_list_inner.setLayout(self.edit_tab_slide_layout)

        self.edit_tab_slide_layout.addWidget(SlidePreview("Select an item from the playlist to edit", None, None, self.preview_size, lambda *args: None, use_context_menu=False))

        self.edit_tab_slide_list.setWidget(self.edit_tab_slide_list_inner)
        self.edit_tab_slide_list.setWidgetResizable(True)
        self.edit_tab_slide_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        ## The edit tab view for the slide being edited
        self.edit_tab_editing_pane = QFrame()
        self.editing_tab_editing_layout = QVBoxLayout()
        self.edit_tab_editing_pane.setLayout(self.editing_tab_editing_layout)
        self.edit_tab_layout.addWidget(self.edit_tab_editing_pane)

        ### Slide type dropdown
        self.edit_tab_type_pane = QFrame()
        self.edit_tab_type_layout = QHBoxLayout()
        self.edit_tab_type_pane.setLayout(self.edit_tab_type_layout)
        self.edit_tab_type_layout.addWidget(QLabel("Slide Type:"))
        self.editing_slide_type_dropdown = QComboBox()
        self.editing_slide_type_dropdown.addItems(["text", "video"])
        self.edit_tab_type_layout.addWidget(self.editing_slide_type_dropdown)
        self.editing_tab_editing_layout.addWidget(self.edit_tab_type_pane)

        self.editing_slide_type_dropdown.currentTextChanged.connect(self.choose_slide_type)

        ### Slide text area
        self.edit_tab_text_pane = QFrame()
        self.edit_tab_text_layout = QVBoxLayout()
        self.edit_tab_text_pane.setLayout(self.edit_tab_text_layout)
        self.edit_tab_text_layout.addWidget(QLabel("Slide Text:"))
        self.editing_slide_text_in = QTextEdit()
        self.edit_tab_text_layout.addWidget(self.editing_slide_text_in)
        self.editing_tab_editing_layout.addWidget(self.edit_tab_text_pane)

        self.editing_slide_text_in.textChanged.connect(self.edit_slide_text)

        ### Slide background chooser
        self.edit_tab_bg_preview = QLabel()
        self.editing_tab_editing_layout.addWidget(self.edit_tab_bg_preview)
        self.edit_tab_bg_preview.hide()

        self.edit_tab_bg_button = QPushButton("Choose Background")
        self.edit_tab_bg_button.clicked.connect(self.choose_slide_background)
        self.editing_tab_editing_layout.addWidget(self.edit_tab_bg_button)

        self.edit_tab_bg_rem_button = QPushButton("Remove Background")
        self.edit_tab_bg_rem_button.clicked.connect(self.remove_slide_background)
        self.editing_tab_editing_layout.addWidget(self.edit_tab_bg_rem_button)

        self.edit_tab_layout.setStretchFactor(self.edit_tab_slide_list, 0)
        self.edit_tab_layout.setStretchFactor(self.edit_tab_editing_pane, 1)

        ### Slide video chooser
        self.edit_tab_video_preview = QLabel("No video")
        self.editing_tab_editing_layout.addWidget(self.edit_tab_video_preview)
        self.edit_tab_video_preview.hide()

        self.edit_tab_video_button = QPushButton("Choose Video")
        self.edit_tab_video_button.clicked.connect(self.choose_slide_video)
        self.editing_tab_editing_layout.addWidget(self.edit_tab_video_button)
        self.edit_tab_video_button.hide()

        # The display view part
        self.display_view = QFrame()
        self.display_view_layout = QVBoxLayout()
        self.display_view_layout.setAlignment(QtCore.Qt.AlignCenter)
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

        self.display_view_layout.addStretch()

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