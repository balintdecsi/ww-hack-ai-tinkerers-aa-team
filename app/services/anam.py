import os
import requests
import mimetypes
import time
from flask import current_app

class AnamService:
    def __init__(self):
        self.api_key = os.environ.get('ANAM_API_KEY')
        self.base_url = os.environ.get('ANAM_API_URL', 'https://api.anam.ai/v1')

    def cleanup_old_avatars(self):
        """
        List existing avatars and delete the oldest ones if the limit is reached.
        Anam Free/Pro plans often have a limit on concurrent one-shot avatars (e.g. 10).
        """
        try:
            # 1. List Avatars
            url = f"{self.base_url}/avatars?limit=50" # Adjust limit as needed
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            avatars = response.json().get('data', [])
            
            current_app.logger.info(f"Found {len(avatars)} existing avatars.")
            
            # Keep a safe buffer. Limit is usually 10. Let's keep 5.
            safe_limit = 5 
            if len(avatars) >= safe_limit:
                # Delete excess
                num_to_delete = len(avatars) - safe_limit + 1
                current_app.logger.info(f"Cleaning up {num_to_delete} old avatars to stay under limit...")
                
                # Sort by creation time (Oldest first)
                avatars.sort(key=lambda x: x.get('createdAt', ''), reverse=False)
                
                for i in range(num_to_delete):
                    avatar_to_delete = avatars[i]
                    del_url = f"{self.base_url}/avatars/{avatar_to_delete['id']}"
                    del_response = requests.delete(del_url, headers=headers)
                    
                    if del_response.status_code in [200, 204]:
                        current_app.logger.info(f"Deleted avatar {avatar_to_delete['id']} (Status: {del_response.status_code})")
                    else:
                        current_app.logger.warning(f"Failed to delete avatar {avatar_to_delete['id']}: {del_response.text}")

                # Give the API a moment to propagate changes
                time.sleep(2)
                    
        except Exception as e:
            current_app.logger.error(f"Error cleaning up avatars: {e}")

    def create_avatar_from_image(self, image_path, name, gender='neutral'):
        """
        Create an avatar from an image using Anam API.
        """
        # Attempt cleanup first
        self.cleanup_old_avatars()

        url = f"{self.base_url}/avatars"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Guess MIME type
        mime_type, _ = mimetypes.guess_type(image_path)
        
        # Fallback/Manual map for common types if system registry is empty
        if not mime_type:
            ext = os.path.splitext(image_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.webp':
                mime_type = 'image/webp'
        
        current_app.logger.info(f"Uploading image: {image_path}")
        current_app.logger.info(f"Detected MIME type: {mime_type}")
        current_app.logger.info(f"File size: {os.path.getsize(image_path)} bytes")

        if not mime_type:
            mime_type = 'application/octet-stream'
            
        try:
            with open(image_path, 'rb') as f:
                # Explicitly set filename and content_type
                files = {'imageFile': (os.path.basename(image_path), f, mime_type)}
                # Only send displayName, gender is usually set in persona config or ignored here
                data = {'displayName': name}
                response = requests.post(url, headers=headers, files=files, data=data)
                
            response.raise_for_status()
            data = response.json()
            return data['id']
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Anam API Error (Create Avatar): {e}")
            if e.response is not None:
                current_app.logger.error(f"Response: {e.response.text}")
            raise

    def get_avatar_config(self, avatar_id):
        """
        Get session token and config to embed the avatar.
        """
        url = f"{self.base_url}/auth/session-token"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Complete persona config to satisfy "Legacy session tokens" error
        # We need to define the persona's behavior and traits.
        payload = {
            "personaConfig": {
                "avatarId": avatar_id,
                "name": "Comics Factory Avatar",
                "systemPrompt": "You are a helpful and expressive avatar created from a comic book character.",
                # Using a known valid Voice ID from docs (Cara's voice)
                "voiceId": "6bfbe25a-979d-40f3-a92b-5394170af54b",
                # Using standard Anam LLM ID
                "llmId": "0934d97d-0c3a-4f33-91b0-5e136a0ef466"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Return everything needed for the frontend
            return {
                "sessionToken": data['sessionToken'],
                "avatarId": avatar_id
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Anam API Error (Get Token): {e}")
            if e.response is not None:
                current_app.logger.error(f"Response: {e.response.text}")
            raise

anam_service = AnamService()
