import os
import uuid
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# A simple mapping of descriptions to pre-made ElevenLabs Voice IDs.
VOICE_MAPPING = {
    "male_deep": "ErXwobaYiN019PkySvjV", # Antoni
    "male_narrator": "TxGEqnHWrfWFTfGW9XjX", # Josh
    "female_soft": "EXAVITQu4vr4xnSDxMaL", # Bella
    "female_energetic": "21m00Tcm4TlvDq8ikWAM", # Rachel
    "default": "21m00Tcm4TlvDq8ikWAM", # Rachel
}

def create_custom_voice(voice_description: str, voice_name: str = None) -> str:
    """
    Uses ElevenLabs 'Voice Design' to generate a voice from text.
    """
    if not voice_name:
        voice_name = f"Custom Voice {uuid.uuid4().hex[:8]}"

    print(f"Creating custom voice: '{voice_name}' based on: '{voice_description}'")
    
    try:
        # 1. Generate the Voice Preview
        response = client.text_to_voice.create_previews(
            voice_description=voice_description,
            text="This is how I sound. Do I fit the character?" 
        )
        
        # 2. Pick the best one (picking the first for automation)
        generated_voice_id = response.previews[0].generated_voice_id
        
        # 3. Save it to Library
        new_voice = client.text_to_voice.create_voice_from_preview(
            voice_name=voice_name,
            voice_description=voice_description,
            generated_voice_id=generated_voice_id
        )
        
        return new_voice.voice_id
    except Exception as e:
        print(f"Error creating custom voice: {e}")
        return VOICE_MAPPING["default"]

def get_voice_id_from_profile(profile: str) -> str:
    """
    Selects a voice ID based on the profile string. 
    If it looks like a description, it tries to generate a custom voice.
    For simplicity in this hack, we'll assume if it's not in mapping, it's a description.
    """
    profile_lower = profile.lower()
    
    # Check if it matches existing keys short codes
    if profile_lower in VOICE_MAPPING:
        return VOICE_MAPPING[profile_lower]
        
    # Fallback logic for old keywords if exact match failed
    if "man" in profile_lower or "male" in profile_lower:
        if "deep" in profile_lower or "gruff" in profile_lower:
            return VOICE_MAPPING["male_deep"]
        return VOICE_MAPPING["male_narrator"]
    
    if "woman" in profile_lower or "female" in profile_lower:
        if "soft" in profile_lower or "gentle" in profile_lower:
            return VOICE_MAPPING["female_soft"]
        return VOICE_MAPPING["female_energetic"]
    
    # If we are here, treat 'profile' as a description for a new voice!
    # To avoid re-creating every time, one might cache this, but for now we create new.
    return create_custom_voice(profile, voice_name=f"Voice for {profile[:20]}")

def generate_voice(text: str, voice_profile: str, output_path: str):
    """
    Generates audio for the given text using a voice matching the profile.
    """
    try:
        voice_id = get_voice_id_from_profile(voice_profile)
        print(f"Using Voice ID: {voice_id} for generation.")
        
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1"
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
                
        print(f"Generated audio: {output_path}")
        
    except Exception as e:
        print(f"Error generating voice for '{text[:20]}...': {e}")
