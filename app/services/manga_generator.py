import os
import json
import re
from pathlib import Path
from PIL import Image
from flask import current_app
from google import genai
from google.genai import types
from app.services.voice_generator import generate_voice

class MangaGeneratorService:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def generate_manga(self, title, text, reference_image_paths):
        """
        Generates manga pages and voiceover from text and reference images.
        """
        if not self.client:
            raise ValueError("GOOGLE_API_KEY not set")

        # 1. Generate Creative Brief
        current_app.logger.info("Generating Creative Brief...")
        brief = self._generate_creative_brief(title, text, reference_image_paths)
        
        voice_description = brief.get("voice_description", "Standard narration voice.")
        final_script = brief.get("narrator_script", text)
        style_reference = brief.get("visual_style", "Manga style")
        pages_prompts = brief.get("pages", [])

        # 2. Generate Voiceover
        current_app.logger.info("Generating Voiceover...")
        audio_filename = f"voiceover_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio', audio_filename)
        
        # Ensure audio dir exists
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        try:
            generate_voice(final_script, voice_description, audio_path)
        except Exception as e:
            current_app.logger.error(f"Voice generation failed: {e}")
            # Continue without voice if fails, or raise?

        # 3. Generate Manga Pages
        current_app.logger.info(f"Generating {len(pages_prompts)} Manga Pages...")
        generated_pages = []
        last_image_path = None

        for i, prompt in enumerate(pages_prompts, start=1):
            page_image_path = self._generate_page_image(i, prompt, style_reference, reference_image_paths, last_image_path)
            if page_image_path:
                generated_pages.append(os.path.basename(page_image_path))
                last_image_path = page_image_path
            else:
                current_app.logger.error(f"Failed to generate page {i}")

        return {
            "title": title,
            "audio_file": audio_filename if os.path.exists(audio_path) else None,
            "pages": generated_pages,
            "script": final_script
        }

    def _generate_creative_brief(self, title, text, reference_image_paths):
        prompt_generation_request = f"""
Your task is to analyze the text and generate the image generation prompts for a manga adaptation. You must keep text in pages across the chapter plot, character, style and voice consistent.
This brief must include both VISUAL prompts for manga page generation and AUDIO directives for voice generation.

To keep CHARACTERS and STYLE consistency across the chapter, in each page image generation prompt include the following:
If images attached:
    use the images for creating a photo of similar art style. This includes: [Composition/Angle]. [Lighting/Atmosphere]. [Style/Media]. Make sure to follow the overal color palitra and shadow/aura fragments.
    Last image will be the previous chapter, use it for knowing [Subject + Adjectives] doing [Action] in [Location/Context].
If no images attached:
    search the title in internet for character/context references.

VOICE TONE IDENTIFICATION:
Analyze the text and images (if provided) to describe the perfect voice for the narrator/character. Include details about age, gender, accent, pitch, speed, and emotional tone (e.g., "Deep, gravelly voice of an ancient warrior, slow and authoritative").

SCRIPT ANNOTATION:
Take the provided Plot text and annotate it for a lively voice cover. maintain the original text but you can add indications for pauses or emotional shifts if allowed by the speech engine, or mainly just ensure the text is segmented well. 
However, for this task, the most important part is the *Voice Description*.
Also provide the full script text to be read.

Respond strictly as a valid JSON object with this structure:
{{
  "visual_style": "<general style guidelines covering composition, palette, medium, lighting>",
  "voice_description": "<detailed description of the voice tone, gender, age, style, accent, temper, etc.>",
  "narrator_script": "<The full text properly formatted for reading (removing stage directions if any)>",
  "pages": [
    "<page 1 detailed prompt consisting of [Subject + Adjectives] doing [Action] in [Location/Context]. [Composition/Angle]. [Lighting/Atmosphere]. [Style/Media]. [Specific Constraint/Text] with dialogue callouts in speech bubbles and sound effects>",
    "<page 2 detailed prompt consisting of [Subject + Adjectives] doing [Action] in [Location/Context]. [Composition/Angle]. [Lighting/Atmosphere]. [Style/Media]. [Specific Constraint/Text] with dialogue callouts in speech bubbles and sound effects>"
  ]
}}

Genres: Manga
Title: {title}
Plot:
{text}
"""
        images = [Image.open(p) for p in reference_image_paths]
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt_generation_request, *images],
                config=types.GenerateContentConfig(
                    response_modalities=['Text'],
                    response_mime_type="application/json"
                ),
            )
            
            raw_text = response.text
            # Cleanup markdown
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:\w+)?\s*", "", raw_text, count=1)
                raw_text = re.sub(r"\s*```$", "", raw_text, count=1)
                
            return json.loads(raw_text)
            
        finally:
            for img in images:
                img.close()

    def _generate_page_image(self, page_num, prompt_text, style_ref, reference_image_paths, prev_image_path=None):
        
        continuation_note = ""
        continuation_image = None
        
        # Load reference images
        contents = [Image.open(p) for p in reference_image_paths]
        
        if prev_image_path:
            continuation_note = "Continue seamlessly from the attached previous page image to preserve character placement, lighting, and action flow."
            try:
                continuation_image = Image.open(prev_image_path)
                contents.append(continuation_image)
            except Exception as e:
                current_app.logger.warning(f"Could not load prev image: {e}")

        page_prompt = "\n\n".join(
            part for part in [style_ref, continuation_note, prompt_text] if part
        ).strip()
        
        contents.insert(0, page_prompt)

        try:
            # Using the specific model from the script
            # Note: User might need to ensure this model is enabled in their project
            response = self.client.models.generate_content(
                model="gemini-3-pro-image-preview", # As requested by user's script
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image'],
                    image_config=types.ImageConfig(
                        aspect_ratio="9:16",
                        image_size="2K"
                    )
                )
            )
            
            for part in response.parts:
                if part.as_image():
                    image = part.as_image()
                    filename = f"manga_page_{uuid.uuid4().hex[:8]}.png"
                    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(output_path)
                    return output_path
                    
        except Exception as e:
            current_app.logger.error(f"Error generating page {page_num}: {e}")
            return None
        finally:
            for img in contents:
                if isinstance(img, Image.Image):
                    img.close()

import uuid
manga_service = MangaGeneratorService()
