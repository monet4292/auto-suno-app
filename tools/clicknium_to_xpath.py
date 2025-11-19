"""
Clicknium Locator to XPath Converter
Đọc file .cnstore và generate XPath selectors
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


class ClickniumToXPath:
    """Convert Clicknium locators sang Selenium XPath"""
    
    def __init__(self, cnstore_path: str):
        """
        Args:
            cnstore_path: Path to .cnstore file
        """
        self.cnstore_path = Path(cnstore_path)
        self.locators = self._load_locators()
    
    def _load_locators(self) -> Dict:
        """Load JSON từ .cnstore file"""
        with open(self.cnstore_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        return data
    
    def _get_identifier(self, locator: Dict) -> Optional[Dict]:
        """Extract identifier từ nested structure"""
        try:
            return locator['content']['childControls'][0]['childControls'][0]['identifier']
        except (KeyError, IndexError):
            return None
    
    def to_xpath(self, locator_name: str) -> Optional[str]:
        """
        Convert một locator thành XPath
        
        Args:
            locator_name: Tên locator trong .cnstore (vd: "button_male")
            
        Returns:
            XPath string hoặc None
        """
        # Tìm locator theo name
        locator = None
        for loc in self.locators.get('locators', []):
            if loc['name'] == locator_name:
                locator = loc
                break
        
        if not locator:
            print(f"❌ Không tìm thấy locator: {locator_name}")
            return None
        
        identifier = self._get_identifier(locator)
        if not identifier:
            print(f"❌ Không parse được identifier: {locator_name}")
            return None
        
        # Build XPath từ identifier
        return self._build_xpath(identifier)
    
    def _build_xpath(self, identifier: Dict) -> str:
        """Build XPath từ identifier object"""
        parts = []
        
        # Tag
        tag = identifier.get('tag', {}).get('value', '*').lower()
        parts.append(f"//{tag}")
        
        conditions = []
        
        # Placeholder
        if 'placeholder' in identifier:
            placeholder_obj = identifier['placeholder']
            if isinstance(placeholder_obj, dict):
                placeholder = placeholder_obj.get('value')
                if placeholder:
                    conditions.append(f"contains(@placeholder, '{placeholder}')")
        
        # ARIA label
        if 'aria-label' in identifier:
            aria_obj = identifier['aria-label']
            if isinstance(aria_obj, dict):
                aria = aria_obj.get('value')
                if aria:
                    conditions.append(f"@aria-label='{aria}'")
        
        # Role
        if 'role' in identifier:
            role_obj = identifier['role']
            if isinstance(role_obj, dict):
                role = role_obj.get('value')
                if role:
                    conditions.append(f"@role='{role}'")
        
        # Text content (sInfo)
        if 'sInfo' in identifier:
            text = identifier['sInfo'].get('value')
            if text:
                conditions.append(f"normalize-space(.)='{text}'")
        
        # Type
        if 'type' in identifier:
            type_val = identifier['type'].get('value')
            if type_val:
                conditions.append(f"@type='{type_val}'")
        
        # data-selected (custom attribute)
        if 'data-selected' in identifier:
            selected_obj = identifier['data-selected']
            if isinstance(selected_obj, dict):
                selected = selected_obj.get('value')
                if selected:
                    conditions.append(f"@data-selected='{selected}'")
        
        # Ancestor class (nếu có)
        ancestor_class = identifier.get('ancestorClass', {}).get('value')
        if ancestor_class:
            # Lấy class đầu tiên (stable nhất)
            first_class = ancestor_class.split()[0]
            conditions.append(f"ancestor::div[contains(@class, '{first_class}')]")
        
        # Combine conditions
        if conditions:
            xpath = parts[0] + '[' + ' and '.join(conditions) + ']'
        else:
            xpath = parts[0]
        
        return xpath
    
    def generate_all(self) -> Dict[str, str]:
        """Generate XPath cho tất cả locators"""
        result = {}
        for locator in self.locators.get('locators', []):
            name = locator['name']
            xpath = self.to_xpath(name)
            if xpath:
                result[name] = xpath
        return result
    
    def print_summary(self):
        """In ra summary của tất cả locators"""
        print("=" * 80)
        print(f"CLICKNIUM LOCATOR SUMMARY: {self.cnstore_path.name}")
        print("=" * 80)
        
        locators = self.locators.get('locators', [])
        print(f"\nTổng số locators: {len(locators)}\n")
        
        for i, loc in enumerate(locators, 1):
            name = loc['name']
            xpath = self.to_xpath(name)
            
            print(f"{i}. {name}")
            print(f"   XPath: {xpath}")
            print()
    
    def export_to_python(self, output_path: str):
        """Export thành Python constants file"""
        all_xpaths = self.generate_all()
        
        content = '''"""
Auto-generated XPath selectors from Clicknium locators
Source: .locator/suno.cnstore
Generated: 2025-11-09
"""

class SunoSelectors:
    """XPath selectors cho Suno.com tạo nhạc"""
    
'''
        
        for name, xpath in all_xpaths.items():
            # Convert name to CONSTANT_CASE
            const_name = name.upper().replace('-', '_')
            content += f'    {const_name} = "{xpath}"\n'
        
        content += '''

# Dictionary for dynamic access
SELECTORS = {
'''
        
        for name, xpath in all_xpaths.items():
            const_name = name.upper().replace('-', '_')
            content += f'    "{name}": SunoSelectors.{const_name},\n'
        
        content += '}\n'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Exported to: {output_path}")


# Demo usage
if __name__ == "__main__":
    converter = ClickniumToXPath(".locator/suno.cnstore")
    
    # Print summary
    converter.print_summary()
    
    print("\n" + "=" * 80)
    print("SPECIFIC EXAMPLES")
    print("=" * 80 + "\n")
    
    # Test specific locators
    test_locators = [
        "button_male",
        "button_female",
        "textarea_write_some_lyrics_or_a_prompt",
        "input_song_title_optional",
        "slider_weirdness",
        "button_create_song"
    ]
    
    for name in test_locators:
        xpath = converter.to_xpath(name)
        print(f"{name}:")
        print(f"  {xpath}\n")
    
    # Export to Python file
    print("=" * 80)
    converter.export_to_python("config/suno_selectors_from_clicknium.py")
