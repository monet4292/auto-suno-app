"""
Auto-generated XPath selectors from Clicknium locators
Source: .locator/suno.cnstore
Generated: 2025-11-09
"""

class SunoSelectors:
    """XPath selectors cho Suno.com tạo nhạc"""
    
    CUSTOMBUTTON = "//div[ancestor::div[contains(@class, 'active')]]"
    SPAN_CUSTOM = "//span[normalize-space(.)='Custom' and ancestor::div[contains(@class, 'active')]]"
    TEXTAREA_WRITE_SOME_LYRICS_OR_A_PROMPT_OR_LEAVE_BLANK_FOR_INSTRU = "//textarea[contains(@placeholder, 'Write some lyrics or a prompt — or leave blank for instrumental') and ancestor::div[contains(@class, 'relative')]]"
    TEXTAREA_INDIE_ELECTRONIC_SYNTHS_120BPM_DISTORTED = "//textarea[contains(@placeholder, 'indie, electronic, synths, 120bpm, distorted') and ancestor::div[contains(@class, 'mb-0')]]"
    INPUT_SONG_TITLE_OPTIONAL = "//input[contains(@placeholder, 'Song Title (Optional)') and ancestor::div[contains(@class, 'css-1is7h4f')]]"
    BUTTON_CREATE_SONG = "//button[@aria-label='Create song' and normalize-space(.)='Create' and @type='button' and ancestor::div[contains(@class, 'flex')]]"
    SPAN_CREATE = "//span[normalize-space(.)='Create' and ancestor::div[contains(@class, 'relative')]]"
    ADVANCEDOPTIONS = "//div[@role='button' and ancestor::div[contains(@class, 'css-1xt3ue1')]]"
    DIV_ADVANCED_OPTIONS = "//div[normalize-space(.)='Advanced Options' and ancestor::div[contains(@class, 'css-6jsm4u')]]"
    INPUT_EXCLUDE_STYLES = "//input[contains(@placeholder, 'Exclude styles') and ancestor::div[contains(@class, 'css-1jy63we')]]"
    BUTTON_MALE = "//button[normalize-space(.)='Male' and @type='button' and @data-selected='false' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    BUTTON_FEMALE = "//button[normalize-space(.)='Female' and @type='button' and @data-selected='false' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    BUTTON_MANUAL = "//button[normalize-space(.)='Manual' and @type='button' and @data-selected='true' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    BUTTON_AUTO = "//button[normalize-space(.)='Auto' and @type='button' and @data-selected='false' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    SLIDER_WEIRDNESS = "//div[@aria-label='Weirdness' and @role='slider' and ancestor::div[contains(@class, 'css-j9om40')]]"
    SLIDER_STYLE_INFLUENCE = "//div[@aria-label='Style Influence' and @role='slider' and ancestor::div[contains(@class, 'css-j9om40')]]"
    SPAN_PERSONA = "//span[normalize-space(.)='Persona' and ancestor::div[contains(@class, 'relative')]]"
    BUTTON_ADD_PERSONA = "//button[@aria-label='Add Persona' and normalize-space(.)='Persona' and @type='button' and ancestor::div[contains(@class, 'css-bxskch')]]"
    INPUT_SEARCH_IN_PERSONA_MODAL = "//input[contains(@placeholder, 'Search') and ancestor::div[contains(@class, 'relative')]]"
    PERSONA_FIST_IN_THE_LIST = "//div[ancestor::div[contains(@class, 'pb-2')]]"
    BUTTON_CLOSE_PERSONA_MODAL = "//button[@aria-label='Close' and @type='button' and ancestor::div[contains(@class, 'absolute')]]"
    BUTTON_SIMPLE = "//button[normalize-space(.)='Simple' and ancestor::div[contains(@class, 'flex')]]"
    SPAN_SIMPLE = "//span[normalize-space(.)='Simple' and ancestor::div[contains(@class, 'active')]]"


# Dictionary for dynamic access
SELECTORS = {
    "Custombutton": SunoSelectors.CUSTOMBUTTON,
    "span_custom": SunoSelectors.SPAN_CUSTOM,
    "textarea_write_some_lyrics_or_a_prompt_or_leave_blank_for_instru": SunoSelectors.TEXTAREA_WRITE_SOME_LYRICS_OR_A_PROMPT_OR_LEAVE_BLANK_FOR_INSTRU,
    "textarea_indie_electronic_synths_120bpm_distorted": SunoSelectors.TEXTAREA_INDIE_ELECTRONIC_SYNTHS_120BPM_DISTORTED,
    "input_song_title_optional": SunoSelectors.INPUT_SONG_TITLE_OPTIONAL,
    "button_create_song": SunoSelectors.BUTTON_CREATE_SONG,
    "span_create": SunoSelectors.SPAN_CREATE,
    "advancedoptions": SunoSelectors.ADVANCEDOPTIONS,
    "div_advanced_options": SunoSelectors.DIV_ADVANCED_OPTIONS,
    "input_exclude_styles": SunoSelectors.INPUT_EXCLUDE_STYLES,
    "button_male": SunoSelectors.BUTTON_MALE,
    "button_female": SunoSelectors.BUTTON_FEMALE,
    "button_manual": SunoSelectors.BUTTON_MANUAL,
    "button_auto": SunoSelectors.BUTTON_AUTO,
    "slider_weirdness": SunoSelectors.SLIDER_WEIRDNESS,
    "slider_style_influence": SunoSelectors.SLIDER_STYLE_INFLUENCE,
    "span_persona": SunoSelectors.SPAN_PERSONA,
    "button_add_persona": SunoSelectors.BUTTON_ADD_PERSONA,
    "input_search_in_persona_modal": SunoSelectors.INPUT_SEARCH_IN_PERSONA_MODAL,
    "persona_fist_in_the_list": SunoSelectors.PERSONA_FIST_IN_THE_LIST,
    "button_close_persona_modal": SunoSelectors.BUTTON_CLOSE_PERSONA_MODAL,
    "button_simple": SunoSelectors.BUTTON_SIMPLE,
    "span_simple": SunoSelectors.SPAN_SIMPLE,
}
