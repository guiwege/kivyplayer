
import os
import re

class Song:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_name, self.file_extension = os.path.splitext(self.file_name)
        self.dir_path = os.path.dirname(file_path)
        self.dir_name = os.path.split(os.path.dirname(file_path))[-1]

        self.display_name = re.sub(self.dir_name, '', self.file_name, flags=re.IGNORECASE).strip() # Remove o nome do album do nome da musica
        self.display_name = re.sub(' {2,}', ' ', self.file_name, flags=re.IGNORECASE) # Remove espaços em excesso
        #if not self.dir_name:
        #    self.dir_name = os.path.dirname(file_path)

        self.album_name = self.dir_name
        self.song_name = self.display_name
        self.artist_name = ''

        
    def __hash__(self):
        return hash((self.file_name, self.file_extension, self.file_path))
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.file_name == other.file_name and self.file_extension == other.file_extension and self.file_path == other.file_path
