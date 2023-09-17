import json

"""
The library manager allows us to interact with the library database. This will store playlists and playlist data
"""

class NO_CONTENT:
    pass

class LibraryManager:
    DEFAULT_LIBRARY = {
        "playlists": {
            "Example Playlist": {
                "Example Song": [
                    {"type": "text", "text": "Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you", "background": "rickey.png"},
                    {"type": "text", "text": "We've known each other for so long\nYour heart's been aching but you're too shy to say it\nI think we both know what's been going on\nYou know the game and you're gonna play it", "background": "rickey.png"},
                    {"type": "text", "text": "*SCREAMS*", "background": None},
                    {"type": "text", "text": "Example Slide", "background": "rickey.png"},
                    {"type": "text", "text": "Example Slide", "background": "rickey.png"},
                    {"type": "text", "text": "Example Slide", "background": "rickey.png"},
                    {"type": "text", "text": "Example Slide", "background": "rickey.png"},
                    {"type": "text", "text": "Example Slide", "background": "rickey.png"},
                    {"type": "text", "text": "Example Slide", "background": "rickey.png"},
                    {"type": "text", "text": "Don't you get the point? The slides are all examples! Give up already.", "background": "no.png"},
                    {"type": "video", "video": "nggyu.mp4"}
                ]
            }
        }
    }

    def __init__(self):
        self.library = None
        self.load_library()
    
    def delete_slide(self, playlist, item, index):
        del self.library["playlists"][playlist][item][index]

    def add_slide(self, playlist, item, index, slide=None):
        if not slide:
            slide = {"type": "text", "text": "I didn't change the text of this slide. Sue me!", "background": None}
        self.library["playlists"][playlist][item].insert(index+1, slide)

    def edit_slide(self, playlist, item, index, type=NO_CONTENT, text=NO_CONTENT, background=NO_CONTENT, video=NO_CONTENT):
        editing = self.library["playlists"][playlist][item][index]
        if type is not NO_CONTENT:
            editing["type"] = type
        if text is not NO_CONTENT:
            editing["text"] = text
        if background is not NO_CONTENT:
            editing["background"] = background
        if video is not NO_CONTENT:
            if video is None:
                if "video" in editing.keys():
                    del editing["video"]
            else:
                editing["video"] = video

    def get_playlists(self):
        return list(self.library["playlists"].keys())

    def get_playlist_items(self, playlist):
        return list(self.library["playlists"][playlist].keys())
    
    def get_playlist_item_slides(self, playlist, item):
        return self.library["playlists"][playlist][item]
    
    def add_playlist_item(self, playlist, item):
        self.library["playlists"][playlist][item] = []
    
    def add_playlist(self, playlist):
        self.library["playlists"][playlist] = {}

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