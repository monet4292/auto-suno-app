"""
Suno Prompt Parser - Parse XML prompt files
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SunoPrompt:
    """Parsed Suno prompt data"""
    title: str
    lyrics: str
    style: str
    
    def __str__(self):
        return f"Title: {self.title}\nStyle: {self.style}\nLyrics:\n{self.lyrics[:100]}..."


class SunoPromptParser:
    """Parser for Suno XML prompt files"""
    
    @staticmethod
    def parse_file(file_path: str) -> Optional[SunoPrompt]:
        """
        Parse XML file and extract first prompt
        
        Args:
            file_path: Path to XML file
            
        Returns:
            SunoPrompt object or None if parsing fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return None
            
            content = path.read_text(encoding='utf-8')
            
            # Parse XML
            root = ET.fromstring(f"<root>{content}</root>")
            
            # Extract first occurrence of each tag
            title_elem = root.find('TITLE')
            lyrics_elem = root.find('LYRICS')
            style_elem = root.find('STYLE')
            
            if title_elem is None or lyrics_elem is None or style_elem is None:
                print(f"❌ Missing required tags (TITLE, LYRICS, STYLE)")
                return None
            
            title = (title_elem.text or "").strip()
            lyrics = (lyrics_elem.text or "").strip()
            style = (style_elem.text or "").strip()
            
            if not title or not lyrics or not style:
                print(f"❌ Empty required fields")
                return None
            
            return SunoPrompt(
                title=title,
                lyrics=lyrics,
                style=style
            )
            
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error parsing file: {e}")
            return None
    
    @staticmethod
    def parse_all_from_file(file_path: str) -> list[SunoPrompt]:
        """
        Parse XML file and extract ALL prompts
        
        Args:
            file_path: Path to XML file
            
        Returns:
            List of SunoPrompt objects
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return []
            
            content = path.read_text(encoding='utf-8')
            
            # Parse XML
            root = ET.fromstring(f"<root>{content}</root>")
            
            # Find all sets of TITLE+LYRICS+STYLE
            titles = [t.text.strip() for t in root.findall('TITLE') if t.text]
            lyrics_list = [l.text.strip() for l in root.findall('LYRICS') if l.text]
            styles = [s.text.strip() for s in root.findall('STYLE') if s.text]
            
            # Group them (assuming they appear in order)
            prompts = []
            count = min(len(titles), len(lyrics_list), len(styles))
            
            for i in range(count):
                prompts.append(SunoPrompt(
                    title=titles[i],
                    lyrics=lyrics_list[i],
                    style=styles[i]
                ))
            
            print(f"✓ Parsed {len(prompts)} prompts from file")
            return prompts
            
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing file: {e}")
            return []


# Demo usage
if __name__ == "__main__":
    # Test with your XML file
    xml_file = "src/prompt/suno-prompt.xml"
    
    print("=" * 60)
    print("Parse first prompt:")
    print("=" * 60)
    prompt = SunoPromptParser.parse_file(xml_file)
    if prompt:
        print(f"\n{prompt}")
        print(f"\nFull lyrics:\n{prompt.lyrics}")
    
    print("\n" + "=" * 60)
    print("Parse all prompts:")
    print("=" * 60)
    prompts = SunoPromptParser.parse_all_from_file(xml_file)
    for i, p in enumerate(prompts, 1):
        print(f"\n--- Prompt {i} ---")
        print(f"Title: {p.title}")
        print(f"Style: {p.style}")
        print(f"Lyrics preview: {p.lyrics[:50]}...")
