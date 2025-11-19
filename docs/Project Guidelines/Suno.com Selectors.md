1. Main Selector Files
src/ui/components/suno_selectors.py
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
    TITLE_INPUT = "//input[@placeholder='Song Title (Optional)']"
    TITLE_INPUT_ALT = "//input[contains(@placeholder, 'Song Title') and contains(@placeholder, 'Optional)']"
    
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

config/suno_selectors_from_clicknium.py
"""
Auto-generated XPath selectors from Clicknium locators
Source: .locator/suno.cnstore
Generated: 2025-11-09
"""

class SunoSelectors:
    """XPath selectors cho Suno.com tạo nhạc"""
    
    # Form Mode
    CUSTOMBUTTON = "//div[ancestor::div[contains(@class, 'active')]]"
    SPAN_CUSTOM = "//span[normalize-space(.)='Custom' and ancestor::div[contains(@class, 'active')]]"
    
    # Text Areas
    TEXTAREA_WRITE_SOME_LYRICS_OR_A_PROMPT_OR_LEAVE_BLANK_FOR_INSTRU = "//textarea[contains(@placeholder, 'Write some lyrics or a prompt — or leave blank for instrumental') and ancestor::div[contains(@class, 'relative')]]"
    TEXTAREA_INDIE_ELECTRONIC_SYNTHS_120BPM_DISTORTED = "//textarea[contains(@placeholder, 'indie, electronic, synths, 120bpm, distorted') and ancestor::div[contains(@class, 'mb-0')]]"
    
    # Input Fields
    INPUT_SONG_TITLE_OPTIONAL = "//input[contains(@placeholder, 'Song Title (Optional)') and ancestor::div[contains(@class, 'css-1is7h4f')]]"
    BUTTON_CREATE_SONG = "//button[@aria-label='Create song' and normalize-space(.)='Create' and @type='button' and ancestor::div[contains(@class, 'flex')]]"
    
    # Advanced Options
    ADVANCEDOPTIONS = "//div[@role='button' and ancestor::div[contains(@class, 'css-1xt3ue1')]]"
    DIV_ADVANCED_OPTIONS = "//div[normalize-space(.)='Advanced Options' and ancestor::div[contains(@class, 'css-6jsm4u')]]"
    INPUT_EXCLUDE_STYLES = "//input[contains(@placeholder, 'Exclude styles') and ancestor::div[contains(@class, 'css-1jy63we')]]"
    
    # Gender Selection
    BUTTON_MALE = "//button[normalize-space(.)='Male' and @type='button' and @data-selected='false' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    BUTTON_FEMALE = "//button[normalize-space(.)='Female' and @type='button' and @data-selected='false' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    
    # Lyrics Mode
    BUTTON_MANUAL = "//button[normalize-space(.)='Manual' and @type='button' and @data-selected='true' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    BUTTON_AUTO = "//button[normalize-space(.)='Auto' and @type='button' and @data-selected='false' and ancestor::div[contains(@class, 'css-slfj3p')]]"
    
    # Sliders
    SLIDER_WEIRDNESS = "//div[@aria-label='Weirdness' and @role='slider' and ancestor::div[contains(@class, 'css-j9om40')]]"
    SLIDER_STYLE_INFLUENCE = "//div[@aria-label='Style Influence' and @role='slider' and ancestor::div[contains(@class, 'css-j9om40')]]"
    
    # Persona
    SPAN_PERSONA = "//span[normalize-space(.)='Persona' and ancestor::div[contains(@class, 'relative')]]"
    BUTTON_ADD_PERSONA = "//button[@aria-label='Add Persona' and normalize-space(.)='Persona' and @type='button' and ancestor::div[contains(@class, 'css-bxskch')]]"
    
    # Dictionary for dynamic access
    SELECTORS = {
        "Custombutton": SunoSelectors.CUSTOMBUTTON,
        "span_custom": SunoSelectors.SPAN_CUSTOM,
        "textarea_write_some_lyrics_or_a_prompt_or_leave_blank_for_instru": SunoSelectors.TEXTAREA_WRITE_SOME_LYRICS_OR_A_PROMPT_OR_LEAVE_BLANK_FOR_INSTRU,
        # ... more selectors
    }

2. JavaScript Injection Snippets
src/core/js_snippets.py
"""JavaScript snippets used by Selenium automation."""

# Script to set the value of a React-controlled <input> or <textarea> using
# the native property setter so React's internal change handlers pick up the
# change. Expects two arguments when executed via Selenium:
#   arguments[0] -> element
#   arguments[1] -> value (string)
SET_REACT_VALUE_SCRIPT = """
const el = arguments[0];
const value = arguments[1];
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set ||
                  Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
if (nativeSetter) {
    nativeSetter.call(el, value);
} else {
    el.value = value;
}
el.dispatchEvent(new Event('input', { bubbles: true }));
el.dispatchEvent(new Event('change', { bubbles: true }));
"""

3. Form Automation Implementation
src/core/suno_form_automation.py
"""
Form Automation Components for Suno Music Creation
"""

class SunoFormFiller:
    """Handles form filling operations for Suno music creation"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def fill_lyrics(self, lyrics: str) -> bool:
        """Fill the lyrics textarea"""
        if not lyrics:
            logger.info("Skipping lyrics (instrumental mode)")
            return True
        
        selectors = [
            "//textarea[contains(@placeholder, 'Write some lyrics or a prompt')]",
            "//*[@role='textbox' and contains(@placeholder, 'Write some lyrics or a prompt')]",
            "//*[contains(@aria-label, 'Write some lyrics')]",
            "//textarea[@aria-label='Lyrics']",
        ]
        
        for selector in selectors:
            try:
                lyrics_box = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                lyrics_box.click()
                time.sleep(0.5)
                lyrics_box.clear()
                lyrics_box.send_keys(lyrics)
                logger.info("✓ Lyrics filled successfully")
                return True
            except TimeoutException:
                continue
        
        logger.error("❌ Could not find lyrics textarea")
        return False
    
    def fill_styles(self, styles: str) -> bool:
        """Fill the styles textarea"""
        if not styles:
            logger.warning("⚠️ No styles provided!")
            return False
        
        selectors = [
            "//textarea[contains(@placeholder, 'indie, electronic, synths')]",
            "//*[@role='textbox' and contains(@placeholder, 'indie, electronic, synths')]",
            "//*[contains(@aria, 'Style of Music')]",
            "//textarea[@aria-label='Style of Music']",
        ]
        
        for selector in selectors:
            try:
                styles_box = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                styles_box.click()
                time.sleep(0.5)
                styles_box.clear()
                styles_box.send_keys(styles)
                logger.info("✓ Styles filled successfully")
                return True
            except TimeoutException:
                continue
        
        logger.error("❌ Could not find styles textarea")
        return False
    
4. Selector Categories
4.1 Form Elements
Element	Primary Selector	Fallback Selectors	Notes
Custom Button	//button[normalize-space(.)='Custom']	//div[ancestor::div[contains(@class, 'active')]]	Main creation mode
Lyrics Textarea	//textarea[contains(@placeholder, 'Write some lyrics')]	Multiple variations	React-controlled input
Styles Textarea	//textarea[contains(@placeholder, 'indie, electronic')]	Multiple variations	React-controlled input
Title Input	//input[@placeholder='Song Title (Optional)']	//input[contains(@placeholder, 'Song Title') and contains(@placeholder, 'Optional)]	Optional field
Create Button	//button[@aria-label='Create song']	//button[@aria-label='Create song' and normalize-space(.)='Create']	Submit form
4.2 Advanced Options
Element	Selector	Notes
Advanced Options Button	//div[@role='button']//div[contains(text(), 'Advanced Options')]	Toggles advanced panel
Exclude Styles Input	//input[contains(@placeholder, 'Exclude styles')]	Style exclusion
Weirdness Slider	//div[@role='slider' and @aria-label='Weirdness']	0-100 range
Style Influence Slider	//div[@role='slider' and @aria-label='Style Influence']	0-100 range
4.3 Gender Selection
Element	Selector	Notes
Male Button	//button[normalize-space(.)='Male']	Gender selection
Female Button	//button[normalize-space(.)='Female']	Gender selection
4.4 Lyrics Mode
Element	Selector	Notes
Manual Lyrics Button	//button[normalize-space(.)='Manual']	Manual lyrics mode
Auto Lyrics Button	//button[normalize-space(.)='Auto']	Auto-generated lyrics
4.5 Persona Selection
Element	Selector	Notes
Persona Button	//button[contains(., 'Persona') or contains(., 'Add Persona')]	Opens persona modal
Persona Modal Search	//div[contains(@class, 'chakra-modal__content')]//input[@placeholder='Search']	Search in modal
Persona Container	//div[contains(@class, 'group flex w-full cursor-pointer items-center gap-4')]	Persona list container

5. Selector Maintenance Strategy
5.1 Fallback Mechanisms
def find_element_with_fallbacks(driver, primary_selector, fallback_selectors):
    """Try multiple selectors until one works"""
    try:
        return WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, primary_selector))
        )
    except TimeoutException:
        for fallback in fallback_selectors:
            try:
                return WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, fallback))
                )
            except TimeoutException:
                continue
    raise NoSuchElementException("All selectors failed")

5.2 Dynamic Selector Updates
def update_selectors_for_ui_changes():
    """Update selectors when Suno.com UI changes"""
    # Monitor for UI changes
    # Update selector constants
    # Test new selectors
    # Update documentation
    pass

6. Best Practices for Selector Usage
6.1 React Component Handling
# Use JavaScript injection for React-controlled components
driver.execute_script(
    SET_REACT_VALUE_SCRIPT,
    {"element": lyrics_element, "value": lyrics_text}
)

6.2 Wait Strategies
# Use explicit waits
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))

# Use visibility checks
if element.is_displayed():
    element.click()

6.3 Error Handling
try:
    element = driver.find_element(By.XPATH, selector)
    element.click()
except NoSuchElementException:
    logger.error(f"Element not found: {selector}")
    # Try fallback selector
except ElementClickInterceptedException:
    logger.error(f"Element click intercepted: {selector}")
    # Try JavaScript click
    driver.execute_script("arguments[0].click()", element)

7. Selector Testing Framework
def test_all_selectors():
    """Test all selectors against current Suno.com UI"""
    test_results = {}
    
    for name, selector in SELECTORS.items():
        try:
            element = driver.find_element(By.XPATH, selector)
            test_results[name] = {
                "found": True,
                "visible": element.is_displayed(),
                "enabled": element.is_enabled()
            }
        except Exception as e:
            test_results[name] = {
                "found": False,
                "error": str(e)
            }
    
    return test_results

This comprehensive selector documentation provides everything needed to recreate the automation functionality in any programming language. The selectors are organized by functionality, include fallbacks, and show best practices for handling React components and dynamic UI elements.