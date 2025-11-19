"""
Suno Selectors - XPath selectors cho tất cả các thành phần Suno.com
"""


class SunoSelectors:
    """XPath selectors cho Suno.com interface"""
    
    # Form Mode
    CUSTOM_BUTTON = "//button[normalize-space(.)='Custom']"
    
    # Basic Input Fields
    LYRICS_TEXTAREA = "//textarea[contains(@placeholder, 'Write some lyrics')]"
    STYLES_TEXTAREA = "//textarea[contains(@placeholder, 'indie, electronic')]"
    CREATE_BUTTON = "//button[@aria-label='Create song']"
    # Title input - chính xác với placeholder "Song Title (Optional)"
    TITLE_INPUT = "//input[@placeholder='Song Title (Optional)']"
    # Fallback nếu placeholder thay đổi
    TITLE_INPUT_ALT = "//input[contains(@placeholder, 'Song Title') and contains(@placeholder, 'Optional')]"
    
    # Advanced Options
    ADVANCED_OPTIONS_BUTTON = "//div[@role='button']//div[contains(text(), 'Advanced Options')]"
    EXCLUDE_STYLES_INPUT = "//input[contains(@placeholder, 'Exclude styles')]"
    
    # Gender Selection
    MALE_BUTTON = "//button[normalize-space(.)='Male']"
    FEMALE_BUTTON = "//button[normalize-space(.)='Female']"
    
    # Lyrics Mode
    MANUAL_LYRICS_BUTTON = "//button[normalize-space(.)='Manual']"
    AUTO_LYRICS_BUTTON = "//button[normalize-space(.)='Auto']"
    
    # Sliders
    WEIRDNESS_SLIDER = "//div[@role='slider' and @aria-label='Weirdness']"
    STYLE_INFLUENCE_SLIDER = "//div[@role='slider' and @aria-label='Style Influence']"
    
    # Persona
    PERSONA_BUTTON = "//button[contains(., 'Persona') or contains(., 'Add Persona')]"
    PERSONA_MODAL_SEARCH = "//div[contains(@class, 'chakra-modal__content')]//input[@placeholder='Search']"
    PERSONA_CONTAINER = "//div[contains(@class, 'group flex w-full cursor-pointer items-center gap-4')]"
