"""
Form Automation Components for Suno Music Creation
Extracted from legacy_modules/suno_auto_create.py

Part of Clean Architecture refactor
"""
import time
from typing import Optional, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.utils.logger import logger


class SunoFormFiller:
    """
    Handles form filling operations for Suno music creation

    Responsibilities:
    - Fill lyrics textarea
    - Fill styles textarea
    - Fill title input
    - Validate form completion
    """

    def __init__(self, driver):
        """
        Initialize form filler

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def fill_lyrics(self, lyrics: str) -> bool:
        """
        Fill the lyrics textarea

        Args:
            lyrics: Song lyrics or prompt text

        Returns:
            True if successful, False otherwise
        """
        if not lyrics:
            logger.info("Skipping lyrics (instrumental mode)")
            return True

        logger.info(f"Filling lyrics ({len(lyrics)} characters)...")

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
        """
        Fill the styles textarea

        Args:
            styles: Music style tags

        Returns:
            True if successful, False otherwise
        """
        if not styles:
            logger.warning("⚠️ No styles provided!")
            return False

        logger.info(f"Filling styles: {styles[:50]}...")

        selectors = [
            "//textarea[contains(@placeholder, 'indie, electronic, synths')]",
            "//*[@role='textbox' and contains(@placeholder, 'indie, electronic, synths')]",
            "//*[contains(@aria-label, 'Style of Music')]",
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

    def fill_title(self, title: Optional[str]) -> bool:
        """
        Fill the title input (optional)

        Args:
            title: Song title

        Returns:
            True if successful or skipped, False on error
        """
        if not title:
            logger.info("Skipping title (AI will generate)")
            return True

        logger.info(f"Filling title: {title}")

        selectors = [
            "//input[contains(@placeholder, 'Song Title (Optional)')]",
            "//*[@role='textbox' and contains(@placeholder, 'Song Title (Optional)')]",
            "//*[contains(@aria-label, 'Song Title')]",
            "//input[@aria-label='Title']",
        ]

        for selector in selectors:
            try:
                title_box = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                title_box.click()
                time.sleep(0.5)
                title_box.clear()
                title_box.send_keys(title)
                logger.info("✓ Title filled successfully")
                return True
            except TimeoutException:
                continue

        logger.error("❌ Could not find title input")
        return False

    def fill_form(self, lyrics: str, styles: str, title: Optional[str] = None) -> bool:
        """
        Fill the complete form

        Args:
            lyrics: Song lyrics or prompt
            styles: Music style tags
            title: Optional song title

        Returns:
            True if all required fields filled successfully
        """
        logger.info("Starting form fill process...")

        success = True
        success &= self.fill_lyrics(lyrics)
        success &= self.fill_styles(styles)
        success &= self.fill_title(title)

        if success:
            logger.info("✓ Form fill completed successfully")
        else:
            logger.error("❌ Form fill failed")

        return success


class SunoPersonaSelector:
    """
    Handles persona selection for Suno music creation
    """

    def __init__(self, driver):
        """
        Initialize persona selector

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def select_persona(self, persona_name: str) -> bool:
        """
        Select a persona by name

        Args:
            persona_name: Name of the persona to select

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Selecting persona: {persona_name}")

        try:
            # Click "Add Persona" button
            persona_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(., 'Persona') or contains(., 'Add Persona')]"))
            )
            persona_btn.click()
            time.sleep(1.5)
            logger.info("✓ Persona modal opened")

            # Search for persona
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//div[contains(@class, 'chakra-modal__content')]//input[@placeholder='Search']"))
            )
            search_input.click()
            time.sleep(0.3)
            search_input.clear()
            search_input.send_keys(persona_name.lower())
            time.sleep(1.5)
            logger.info(f"✓ Searched for '{persona_name}'")

            # Click first valid result (exclude "Create New Persona")
            persona_containers = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH,
                    "//div[contains(@class, 'group flex w-full cursor-pointer items-center gap-4')]"))
            )

            valid_personas = []
            for container in persona_containers:
                if "Create New Persona" not in container.text:
                    valid_personas.append(container)

            if not valid_personas:
                logger.warning(f"No persona found matching '{persona_name}'")
                return False

            # Click first result
            first_result = valid_personas[0]
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_result)
            time.sleep(0.5)
            first_result.click()
            time.sleep(1)

            logger.info(f"✓ Persona '{persona_name}' selected successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to select persona '{persona_name}': {e}")
            return False


class SunoModeSelector:
    """
    Handles mode selection (Custom mode) for Suno
    """

    def __init__(self, driver):
        """
        Initialize mode selector

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def ensure_custom_mode(self) -> bool:
        """
        Ensure Custom mode is selected

        Returns:
            True if Custom mode is active, False otherwise
        """
        logger.info("Checking Custom mode...")

        try:
            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "button"))
            )

            # Find Custom button
            custom_selectors = [
                "//button[normalize-space(.)='Custom']",
                "//button[@role='button' and normalize-space(.)='Custom']",
                "//button[contains(text(), 'Custom')]",
                "//button[@aria-label='Custom']",
            ]

            custom_button = None
            for selector in custom_selectors:
                try:
                    custom_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logger.debug(f"✓ Found Custom button with: {selector}")
                    break
                except TimeoutException:
                    continue

            if not custom_button:
                logger.warning("⚠️ Custom button not found, assuming already in Custom mode")
                return True

            # Check if already active
            is_active = (
                custom_button.get_attribute("aria-pressed") == "true" or
                custom_button.get_attribute("data-state") == "active" or
                "active" in (custom_button.get_attribute("class") or "")
            )

            if not is_active:
                logger.info("Switching to Custom mode...")
                custom_button.click()
                time.sleep(2)
                logger.info("✓ Switched to Custom mode")
            else:
                logger.info("✓ Already in Custom mode")

            return True

        except Exception as e:
            logger.warning(f"⚠️ Error checking Custom mode: {e}")
            return False


class SunoAdvancedOptionsConfigurator:
    """
    Handles advanced options configuration
    """

    def __init__(self, driver):
        """
        Initialize advanced options configurator

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open_advanced_options(self) -> bool:
        """
        Open advanced options panel if not already open

        Returns:
            True if panel is open, False otherwise
        """
        try:
            adv_selectors = [
                "//button[normalize-space(.)='Advanced Options']",
                "//button[contains(text(), 'Advanced Options')]",
                "//button[contains(@aria-label, 'Advanced')]",
            ]

            adv_btn = None
            for selector in adv_selectors:
                try:
                    adv_btn = self.driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue

            if not adv_btn:
                logger.warning("Advanced Options button not found")
                return False

            is_expanded = adv_btn.get_attribute("aria-expanded") == "true"
            if not is_expanded:
                adv_btn.click()
                time.sleep(0.5)
                logger.info("✓ Opened Advanced Options")
            else:
                logger.info("✓ Advanced Options already open")

            return True

        except Exception as e:
            logger.debug(f"Error opening Advanced Options: {e}")
            return False

    def configure_exclude_styles(self, exclude_styles: str) -> bool:
        """
        Configure exclude styles

        Args:
            exclude_styles: Styles to exclude

        Returns:
            True if successful, False otherwise
        """
        if not exclude_styles:
            return True

        logger.info(f"Setting exclude styles: {exclude_styles}")

        try:
            selectors = [
                "//input[contains(@placeholder, 'Exclude styles')]",
                "//textarea[contains(@placeholder, 'Exclude styles')]",
                "//*[@role='textbox' and contains(@placeholder, 'Exclude styles')]",
            ]

            exclude_box = None
            for selector in selectors:
                try:
                    exclude_box = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if exclude_box:
                exclude_box.clear()
                exclude_box.send_keys(exclude_styles)
                logger.info("✓ Exclude styles set")
                return True
            else:
                logger.warning("Exclude styles input not found")
                return False

        except Exception as e:
            logger.warning(f"Error setting exclude styles: {e}")
            return False

    def configure_vocal_gender(self, gender: str) -> bool:
        """
        Configure vocal gender

        Args:
            gender: "Male" or "Female"

        Returns:
            True if successful, False otherwise
        """
        if not gender:
            return True

        logger.info(f"Setting vocal gender: {gender}")

        try:
            gender_btn = self.driver.find_element(
                By.XPATH,
                f"//button[normalize-space(.)='{gender}']"
            )
            gender_btn.click()
            time.sleep(0.3)
            logger.info(f"✓ Vocal gender set to {gender}")
            return True
        except NoSuchElementException:
            logger.warning(f"Vocal gender button '{gender}' not found")
            return False

    def configure_lyrics_mode(self, mode: str) -> bool:
        """
        Configure lyrics mode

        Args:
            mode: "Manual" or "Auto"

        Returns:
            True if successful, False otherwise
        """
        if not mode:
            return True

        logger.info(f"Setting lyrics mode: {mode}")

        try:
            mode_btn = self.driver.find_element(
                By.XPATH,
                f"//button[normalize-space(.)='{mode}']"
            )
            mode_btn.click()
            time.sleep(0.3)
            logger.info(f"✓ Lyrics mode set to {mode}")
            return True
        except NoSuchElementException:
            logger.warning(f"Lyrics mode button '{mode}' not found")
            return False

    def configure_weirdness(self, weirdness: int) -> bool:
        """
        Configure weirdness slider

        Args:
            weirdness: Value 0-100

        Returns:
            True if successful, False otherwise
        """
        if weirdness is None:
            return True

        logger.info(f"Setting weirdness: {weirdness}%")

        try:
            slider = self.driver.find_element(By.XPATH,
                "//input[@type='range' and contains(@aria-label, 'weirdness')]")
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                slider, weirdness
            )
            logger.info(f"✓ Weirdness set to {weirdness}%")
            return True
        except NoSuchElementException:
            logger.warning("Weirdness slider not found")
            return False

    def configure_style_influence(self, influence: int) -> bool:
        """
        Configure style influence slider

        Args:
            influence: Value 0-100

        Returns:
            True if successful, False otherwise
        """
        if influence is None:
            return True

        logger.info(f"Setting style influence: {influence}%")

        try:
            slider = self.driver.find_element(By.XPATH,
                "//input[@type='range' and contains(@aria-label, 'style influence')]")
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                slider, influence
            )
            logger.info(f"✓ Style influence set to {influence}%")
            return True
        except NoSuchElementException:
            logger.warning("Style influence slider not found")
            return False

    def configure_options(self, exclude_styles: Optional[str] = None,
                         vocal_gender: Optional[str] = None,
                         lyrics_mode: Optional[str] = None,
                         weirdness: Optional[int] = None,
                         style_influence: Optional[int] = None) -> bool:
        """
        Configure all advanced options

        Args:
            exclude_styles: Styles to exclude
            vocal_gender: "Male" or "Female"
            lyrics_mode: "Manual" or "Auto"
            weirdness: Weirdness level 0-100
            style_influence: Style influence 0-100

        Returns:
            True if all configurations successful
        """
        logger.info("Configuring advanced options...")

        # Open panel first
        if not self.open_advanced_options():
            return False

        success = True
        success &= self.configure_exclude_styles(exclude_styles or "")
        success &= self.configure_vocal_gender(vocal_gender or "")
        success &= self.configure_lyrics_mode(lyrics_mode or "")
        success &= self.configure_weirdness(weirdness)
        success &= self.configure_style_influence(style_influence)

        if success:
            logger.info("✓ Advanced options configured successfully")
        else:
            logger.warning("⚠️ Some advanced options failed to configure")

        return success