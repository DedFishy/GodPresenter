import json

"""
The library manager allows us to interact with the library database. This will store playlists and playlist data
"""

class LibraryManager:
    DEFAULT_LIBRARY = {
        "playlists": {
            "Example Playlist": {
                "Example Song": [
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    {"type": "text", "text": "Example Slide", "background": "no.png"},
                    #{"type": "video", "path": "examplevideo.mp4"}
                ]
            }
        }
    }

    def __init__(self):
        self.library = None
        self.load_library()

    def get_playlists(self):
        return list(self.library["playlists"].keys())

    def get_playlist_items(self, playlist):
        return list(self.library["playlists"][playlist].keys())
    
    def get_playlist_item_slides(self, playlist, item):
        return self.library["playlists"][playlist][item]

    def load_library(self):
        with open("library.json", "r+") as library_file:
            library_data = library_file.read()
            if library_data == "":
                self.library = self.DEFAULT_LIBRARY
            else:
                self.library = json.loads(library_data)
        
    def save_library(self):
        with open("library.json", "w+") as library_file:
            library_file.write(json.dumps(self.library))