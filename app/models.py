from datetime import datetime, timezone

class AvatarProject:
    def __init__(self, id, title, protagonist_image_path, comic_file_path, anam_avatar_id):
        self.type = 'avatar'
        self.id = id
        self.title = title
        self.protagonist_image_path = protagonist_image_path
        self.comic_file_path = comic_file_path
        self.anam_avatar_id = anam_avatar_id
        self.created_at = datetime.now(timezone.utc)

class MangaProject:
    def __init__(self, id, title, script, audio_path, pages):
        self.type = 'manga'
        self.id = id
        self.title = title
        self.script = script
        self.audio_path = audio_path
        self.pages = pages # List of filenames
        self.created_at = datetime.now(timezone.utc)
