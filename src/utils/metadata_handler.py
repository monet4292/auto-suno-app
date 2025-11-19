"""
Metadata Handler for Suno Audio Files
Extracted from legacy_modules/suno_batch_download.py

Handles embedding metadata and cover art into MP3 files using Mutagen
"""
import os
from typing import Optional, Dict, Any
from pathlib import Path

from src.utils.logger import logger


class SunoMetadataHandler:
    """
    Handles metadata embedding for Suno audio files

    Responsibilities:
    - Embed ID3 tags (title, artist, album, genre)
    - Embed cover art/thumbnail
    - Handle metadata extraction from clip info
    """

    def __init__(self):
        """Initialize metadata handler"""
        self._mutagen_available = self._check_mutagen_availability()

    def _check_mutagen_availability(self) -> bool:
        """Check if mutagen library is available"""
        try:
            import mutagen
            import mutagen.id3
            import mutagen.mp3
            return True
        except ImportError:
            logger.warning("Mutagen library not available - metadata embedding disabled")
            return False

    def embed_metadata(self, audio_path: str, clip_info: Dict[str, Any],
                      thumbnail_path: Optional[str] = None) -> bool:
        """
        Embed metadata into MP3 file

        Args:
            audio_path: Path to the MP3 file
            clip_info: Clip information dictionary
            thumbnail_path: Optional path to thumbnail image

        Returns:
            True if successful, False otherwise
        """
        if not self._mutagen_available:
            logger.info("Skipping metadata embedding (mutagen not available)")
            return False

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return False

        try:
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TPUB, WOAR, APIC
            from mutagen.mp3 import MP3

            # Load audio file
            audio = MP3(audio_path, ID3=ID3)

            # Delete existing ID3 tags if present
            try:
                audio.delete()
                audio.save()
            except Exception:
                # No existing tags, continue
                pass

            # Reload file and add new tags
            audio = MP3(audio_path, ID3=ID3)
            
            # Add tags (will create new tag structure)
            try:
                audio.add_tags()
            except Exception:
                # Tags already exist after reload, clear them
                audio.tags.clear()

            # Basic metadata
            title = clip_info.get('title', '')
            if title:
                audio.tags.add(TIT2(encoding=3, text=title))

            # Artist (display_name)
            display_name = clip_info.get('display_name', '')
            if display_name:
                audio.tags.add(TPE1(encoding=3, text=display_name))

            # Album (can be same as artist or custom)
            if display_name:
                audio.tags.add(TALB(encoding=3, text=f"{display_name} - Suno AI"))

            # Genre from tags
            tags = clip_info.get('metadata', {}).get('tags', [])
            if tags:
                genre_text = ', '.join(tags)
                audio.tags.add(TCON(encoding=3, text=genre_text))

            # Publisher (same as artist)
            if display_name:
                audio.tags.add(TPUB(encoding=3, text=display_name))

            # Song URL
            clip_id = clip_info.get('id', '')
            if clip_id:
                song_url = f"https://suno.com/song/{clip_id}"
                audio.tags.add(WOAR(url=song_url))

            # Cover art
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._embed_cover_art(audio, thumbnail_path)

            audio.save()
            logger.info(f"✓ Embedded metadata for: {Path(audio_path).name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to embed metadata: {e}")
            return False

    def _embed_cover_art(self, audio: 'MP3', thumbnail_path: str) -> bool:
        """
        Embed cover art into audio file

        Args:
            audio: Mutagen MP3 object
            thumbnail_path: Path to thumbnail image

        Returns:
            True if successful, False otherwise
        """
        try:
            from mutagen.id3 import APIC

            with open(thumbnail_path, 'rb') as img_file:
                image_data = img_file.read()

            # Determine MIME type
            mime_type = self._get_image_mime_type(thumbnail_path)

            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=image_data
                )
            )

            logger.info("✓ Embedded cover art")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to embed cover art: {e}")
            return False

    def _get_image_mime_type(self, image_path: str) -> str:
        """
        Determine MIME type from file extension

        Args:
            image_path: Path to image file

        Returns:
            MIME type string
        """
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')

    def extract_metadata(self, clip_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata fields from clip info

        Args:
            clip_info: Raw clip information

        Returns:
            Cleaned metadata dictionary
        """
        metadata = {
            'title': clip_info.get('title', ''),
            'artist': clip_info.get('display_name', ''),
            'album': '',
            'genre': '',
            'year': '',
            'url': '',
            'tags': []
        }

        # Set album
        if metadata['artist']:
            metadata['album'] = f"{metadata['artist']} - Suno AI"

        # Extract tags as genre
        tags = clip_info.get('metadata', {}).get('tags', [])
        if tags:
            metadata['genre'] = ', '.join(tags)
            metadata['tags'] = tags

        # Song URL
        clip_id = clip_info.get('id', '')
        if clip_id:
            metadata['url'] = f"https://suno.com/song/{clip_id}"

        return metadata

    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate that file is a valid audio file

        Args:
            audio_path: Path to audio file

        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(audio_path):
            return False

        if not self._mutagen_available:
            # Basic check without mutagen
            return audio_path.lower().endswith(('.mp3', '.wav', '.flac', '.m4a'))

        try:
            from mutagen import File
            audio = File(audio_path)
            return audio is not None and hasattr(audio, 'info')
        except Exception:
            return False