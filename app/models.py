from datetime import datetime, timezone

class AvatarProject:
    def __init__(self, id, title, protagonist_image_path, comic_file_path, anam_avatar_id):
        self.id = id
        self.title = title
        self.protagonist_image_path = protagonist_image_path
        self.comic_file_path = comic_file_path
        self.anam_avatar_id = anam_avatar_id
        self.created_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f'<AvatarProject {self.title}>'