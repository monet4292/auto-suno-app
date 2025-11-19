"""
Suno Auto Music Creation
Tự động tạo nhạc trên Suno.com với Custom Mode

TÍCH HỢP VÀO UI APP (CustomTkinter GUI)
- Dùng SessionManager hiện có để mở browser với profile
- Chạy từ menu "Tạo nhạc" trong UI
- Sử dụng Chrome profile đã đăng nhập

KIẾN TRÚC:
ui/create_music_panel.py → SunoMusicCreator → SessionManager
"""
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import từ project hiện có
from src.core.session_manager import SessionManager
from src.utils.logger import logger


@dataclass
class SunoCreateConfig:
    """Cấu hình tạo nhạc Suno"""
    # Bước 1: Persona (optional)
    persona_name: Optional[str] = None
    
    # Bước 2: Nội dung chính (bắt buộc)
    lyrics: str = ""
    styles: str = ""
    title: Optional[str] = None
    
    # Bước 3: Advanced Options (optional)
    exclude_styles: Optional[str] = None
    vocal_gender: Optional[str] = None  # "Male" hoặc "Female"
    lyrics_mode: Optional[str] = None   # "Manual" hoặc "Auto"
    weirdness: Optional[int] = None     # 0-100
    style_influence: Optional[int] = None  # 0-100
    
    # Tùy chọn khác
    wait_for_generation: bool = True
    timeout: int = 120  # seconds


class SunoMusicCreator:
    """
    Class tự động tạo nhạc trên Suno.com
    
    TÍCH HỢP VÀO UI APP:
    - Dùng SessionManager để mở browser với profile
    - Chạy từ UI panel (CreateMusicPanel)
    - Callback để cập nhật progress trong GUI
    
    Workflow:
    1. UI gọi create_song() với account_name + config
    2. SessionManager mở browser với profile đã lưu
    3. Tự động điền form và tạo nhạc
    4. Callback cập nhật progress bar trong UI
    5. Trả kết quả về UI
    """
    
    def __init__(self, session_manager: SessionManager, progress_callback: Optional[Callable[[str, int], None]] = None):
        """
        Khởi tạo Suno Music Creator
        
        Args:
            session_manager: SessionManager instance (từ app)
            progress_callback: Callback để cập nhật UI
                               Signature: callback(message: str, progress: int)
        """
        self.create_url = "https://suno.com/create"
        self.session_manager = session_manager
        self.progress_callback = progress_callback
        self.driver = None
        self.wait = None
        
    def _update_progress(self, message: str, progress: int):
        """
        Cập nhật progress trong UI
        
        Args:
            message: Thông điệp hiển thị
            progress: % hoàn thành (0-100)
        """
        logger.info(f"[{progress}%] {message}")
        if self.progress_callback:
            self.progress_callback(message, progress)
        
    def create_song(self, account_name: str, config: SunoCreateConfig) -> Dict[str, Any]:
        """
        Tạo bài hát tự động từ account đã lưu
        
        WORKFLOW:
        1. Mở browser với profile account (qua SessionManager)
        2. Navigate đến /create và chuyển Custom mode
        3. Chọn Persona (optional)
        4. Điền Lyrics, Styles, Title
        5. Cấu hình Advanced Options (optional)
        6. Click Create và chờ kết quả
        
        Args:
            account_name: Tên account đã lưu (có profile Chrome)
            config: Cấu hình tạo nhạc
            
        Returns:
            Dict chứa thông tin kết quả
        """
        logger.info(f"Bắt đầu tạo nhạc cho account: {account_name}")
        self._update_progress("Đang chuẩn bị...", 0)
        
        result = {
            "success": False,
            "steps_completed": [],
            "error": None,
            "song_urls": []
        }
        
        try:
            # BƯỚC 0: Mở browser với profile account
            self._update_progress(f"Mở browser với profile '{account_name}'...", 5)
            self.driver = self.session_manager.launch_browser(account_name, headless=False)
            if not self.driver:
                raise Exception(f"Không thể mở browser cho account '{account_name}'")
            
            self.wait = WebDriverWait(self.driver, 10)
            result["steps_completed"].append("open_browser")
            
            # BƯỚC 1: Navigate và chuyển Custom Mode
            self._update_progress("Chuyển sang Custom Mode...", 10)
            self._ensure_custom_mode()
            result["steps_completed"].append("prepare_environment")
            
            # BƯỚC 2: Chọn Persona (nếu có)
            if config.persona_name:
                self._update_progress(f"Chọn Persona '{config.persona_name}'...", 20)
                self._select_persona(config.persona_name)
                result["steps_completed"].append("select_persona")
            else:
                self._update_progress("Bỏ qua Persona...", 20)
                result["steps_completed"].append("skip_persona")
            
            # BƯỚC 3: Nhập nội dung chính
            self._update_progress("Nhập Lyrics, Styles, Title...", 40)
            self._fill_main_content(
                lyrics=config.lyrics,
                styles=config.styles,
                title=config.title
            )
            result["steps_completed"].append("fill_content")
            
            # BƯỚC 4: Advanced Options (nếu có)
            if self._has_advanced_options(config):
                self._update_progress("Cấu hình Advanced Options...", 60)
                self._configure_advanced_options(config)
                result["steps_completed"].append("configure_advanced")
            else:
                self._update_progress("Dùng Advanced Options mặc định...", 60)
                result["steps_completed"].append("skip_advanced")
            
            # BƯỚC 5: Tạo bài hát
            self._update_progress("Đang tạo bài hát...", 70)
            song_urls = self._create_and_wait(config)
            result["steps_completed"].append("create_song")
            result["song_urls"] = song_urls
            
            result["success"] = True
            self._update_progress(f"Hoàn thành! Đã tạo {len(song_urls)} bài hát", 100)
            logger.info(f"Tạo nhạc thành công: {len(song_urls)} bài")
            
        except Exception as e:
            result["error"] = str(e)
            self._update_progress(f"Lỗi: {str(e)}", 0)
            logger.error(f"Lỗi tạo nhạc: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return result
    
    def _ensure_custom_mode(self):
        """Đảm bảo đang ở Custom Mode"""
        logger.info("Navigate đến Suno Create page...")
        self.driver.get(self.create_url)
        time.sleep(5)  # Tăng thời gian chờ page load (DOM heavy)
        
        # DEBUG: Take screenshot to see actual UI
        try:
            screenshot_path = Path("logs/debug_page_load.png")
            screenshot_path.parent.mkdir(exist_ok=True)
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Failed to save screenshot: {e}")
        
        logger.info("Kiểm tra chế độ Custom Mode...")
        try:
            # Wait cho page load - kiểm tra bất kỳ button nào
            logger.info("Đợi page load (wait for any button)...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "button"))
            )
            logger.info("✓ Page đã load (found buttons)")
            
            # Tìm nút Custom - dùng accessible name (Playwright approach)
            logger.info("Tìm nút Custom...")
            # Thử nhiều strategies (verified từ Playwright record)
            custom_selectors = [
                "//button[normalize-space(.)='Custom']",  # Playwright: get_by_role("button", name="Custom")
                "//button[@role='button' and normalize-space(.)='Custom']",  # With role attribute
                "//button[contains(text(), 'Custom')]",  # Contains text fallback
                "//button[@aria-label='Custom']",  # Aria label fallback
            ]
            
            custom_button = None
            for selector in custom_selectors:
                try:
                    custom_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logger.info(f"✓ Found Custom button với: {selector}")
                    break
                except TimeoutException:
                    logger.debug(f"Selector failed: {selector}")
                    continue
            
            if not custom_button:
                logger.warning("⚠️ Không tìm thấy nút Custom với bất kỳ selector nào")
                logger.info("Giả định đã ở Custom Mode, tiếp tục...")
                return
            
            # Kiểm tra xem đã ở Custom mode chưa
            # Check aria-pressed hoặc data-state attribute
            is_active = (
                custom_button.get_attribute("aria-pressed") == "true" or
                custom_button.get_attribute("data-state") == "active" or
                custom_button.get_attribute("focused") == "focused" or
                "active" in (custom_button.get_attribute("class") or "")
            )
            
            if not is_active:
                logger.info("Chuyển sang Custom Mode...")
                custom_button.click()
                time.sleep(2)  # Chờ UI update
                logger.info("✓ Đã chuyển sang Custom Mode")
            else:
                logger.info("✓ Đã ở Custom Mode")
            
        except TimeoutException as e:
            logger.warning(f"Timeout khi tìm nút Custom: {e}")
            logger.warning("Tiếp tục thử fill form...")
        
    def _select_persona(self, persona_name: str):
        """
        Chọn Persona theo tên (Updated 2025-11-09)
        
        Args:
            persona_name: Tên persona cần chọn (vd: "Minh Chien")
            
        Flow:
            1. Click "Add Persona" button
            2. Chờ modal xuất hiện
            3. Nhập tên vào search box
            4. Click kết quả đầu tiên (bỏ qua "Create New Persona")
        """
        logger.info(f"Chọn persona '{persona_name}'...")
        
        # 1. Click Persona button
        try:
            # Scroll lên trên cùng
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            persona_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(., 'Persona') or contains(., 'Add Persona')]"))
            )
            persona_btn.click()
            time.sleep(1.5)
            logger.info(f"✓ Persona modal opened")
        except Exception as e:
            logger.warning(f"Cannot open persona modal: {e}")
            return
        
        # 2. Tìm search input và nhập tên
        try:
            # Chờ modal animation
            time.sleep(1)
            
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
        except Exception as e:
            logger.warning(f"Cannot search persona: {e}")
            return
        
        # 3. Click kết quả đầu tiên (bỏ qua "Create New Persona")
        try:
            persona_containers = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, 
                    "//div[contains(@class, 'group flex w-full cursor-pointer items-center gap-4')]"))
            )
            
            # Lọc bỏ "Create New Persona"
            valid_personas = []
            for container in persona_containers:
                if "Create New Persona" not in container.text:
                    valid_personas.append(container)
            
            if not valid_personas:
                logger.warning(f"No persona found matching '{persona_name}'")
                return
            
            # Click kết quả đầu tiên
            first_result = valid_personas[0]
            
            # Lấy tên để verify
            try:
                name_div = first_result.find_element(By.XPATH, 
                    ".//div[contains(@class, 'text-foreground-primary')]")
                found_name = name_div.text
                logger.info(f"✓ Found persona: '{found_name}'")
            except:
                pass
            
            # Scroll và click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_result)
            time.sleep(0.5)
            first_result.click()
            time.sleep(1)
            
            logger.info(f"✓ Persona '{persona_name}' selected successfully")
            
        except Exception as e:
            logger.warning(f"Cannot click persona: {e}")
            raise
    
    def _fill_main_content(self, lyrics: str, styles: str, title: Optional[str]):
        """
        Nhập Lyrics, Styles, Title với Selenium
        
        VERIFIED SELECTORS từ Playwright record:
        - Lyrics: role="textbox" name="Write some lyrics or a prompt"
        - Styles: role="textbox" name="indie, electronic, synths,"
        - Title: role="textbox" name="Song Title (Optional)"
        
        Strategy: Playwright-compatible XPath (role + aria-label/placeholder)
        
        Args:
            lyrics: Lời bài hát hoặc prompt
            styles: Style tags
            title: Tên bài hát (optional)
        """
        if lyrics:
            logger.info(f"Nhập Lyrics ({len(lyrics)} ký tự)...")
            try:
                # Playwright verified: Suno dùng <textarea> thật, không có role='textbox'
                lyrics_selectors = [
                    "//textarea[contains(@placeholder, 'Write some lyrics or a prompt')]",
                    "//*[@role='textbox' and contains(@placeholder, 'Write some lyrics or a prompt')]",
                    "//*[contains(@aria-label, 'Write some lyrics')]",
                    "//textarea[@aria-label='Lyrics']",
                ]
                
                lyrics_box = None
                for selector in lyrics_selectors:
                    try:
                        lyrics_box = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"✓ Found lyrics box với: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not lyrics_box:
                    raise Exception("Không tìm thấy Lyrics textbox với bất kỳ selector nào")
                
                lyrics_box.click()
                time.sleep(0.5)
                lyrics_box.clear()
                lyrics_box.send_keys(lyrics)
                logger.info("✓ Đã nhập Lyrics")
            except Exception as e:
                logger.error(f"❌ Lỗi khi nhập Lyrics: {e}")
                raise
        else:
            logger.info("Bỏ qua Lyrics (tạo instrumental)")
        
        if styles:
            logger.info(f"Nhập Styles: {styles[:50]}...")
            try:
                # Playwright verified: Suno dùng <textarea> thật
                styles_selectors = [
                    "//textarea[contains(@placeholder, 'indie, electronic, synths')]",
                    "//*[@role='textbox' and contains(@placeholder, 'indie, electronic, synths')]",
                    "//*[contains(@aria-label, 'Style of Music')]",
                    "//textarea[@aria-label='Style of Music']",
                ]
                
                styles_box = None
                for selector in styles_selectors:
                    try:
                        styles_box = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"✓ Found styles box với: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not styles_box:
                    raise Exception("Không tìm thấy Styles textbox với bất kỳ selector nào")
                styles_box.click()
                time.sleep(0.5)
                styles_box.clear()
                styles_box.send_keys(styles)
                logger.info("✓ Đã nhập Styles")
            except Exception as e:
                logger.error(f"❌ Lỗi khi nhập Styles: {e}")
                raise
        else:
            logger.warning("Cảnh báo: Chưa nhập Styles!")
        
        if title:
            logger.info(f"Nhập Title: {title}...")
            try:
                # Playwright verified: Suno dùng <input> thật
                title_selectors = [
                    "//input[contains(@placeholder, 'Song Title (Optional)')]",
                    "//*[@role='textbox' and contains(@placeholder, 'Song Title (Optional)')]",
                    "//*[contains(@aria-label, 'Song Title')]",
                    "//input[@aria-label='Title']",
                ]
                
                title_box = None
                for selector in title_selectors:
                    try:
                        title_box = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"✓ Found title box với: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not title_box:
                    raise Exception("Không tìm thấy Title textbox với bất kỳ selector nào")
                
                title_box.click()
                time.sleep(0.5)
                title_box.clear()
                title_box.send_keys(title)
                logger.info("✓ Đã nhập Title")
            except Exception as e:
                logger.error(f"❌ Lỗi khi nhập Title: {e}")
                raise
        else:
            logger.info("Bỏ qua Title (AI tự tạo)")
        
        logger.info("✓ Đã hoàn thành nhập nội dung")
    
    def _open_advanced_options(self):
        """Mở Advanced Options nếu chưa mở"""
        try:
            # Playwright: get_by_role("button", name="Advanced Options")
            # Multiple selectors vì có thể text thay đổi
            adv_selectors = [
                "//button[normalize-space(.)='Advanced Options']",
                "//button[contains(text(), 'Advanced Options')]",
                "//button[contains(@aria-label, 'Advanced')]",
            ]
            
            adv_btn = None
            for selector in adv_selectors:
                try:
                    adv_btn = self.driver.find_element(By.XPATH, selector)
                    logger.debug(f"Found Advanced Options với: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not adv_btn:
                logger.warning("Không tìm thấy nút Advanced Options - có thể đã mở sẵn")
                return
            
            # Kiểm tra xem đã mở chưa qua attribute expanded
            is_expanded = adv_btn.get_attribute("aria-expanded") == "true"
            
            if not is_expanded:
                adv_btn.click()
                time.sleep(0.5)
                logger.info("✓ Đã mở Advanced Options")
            else:
                logger.info("✓ Advanced Options đã mở sẵn")
        except Exception as e:
            logger.debug(f"Lỗi khi mở Advanced Options: {e} - Tiếp tục...")
    
    def _has_advanced_options(self, config: SunoCreateConfig) -> bool:
        """Kiểm tra có cần cấu hình Advanced Options không"""
        return any([
            config.exclude_styles,
            config.vocal_gender,
            config.lyrics_mode,
            config.weirdness is not None,
            config.style_influence is not None
        ])
    
    def _configure_advanced_options(self, config: SunoCreateConfig):
        """
        Cấu hình Advanced Options
        
        Args:
            config: Cấu hình chứa advanced options
        """
        logger.info("Mở Advanced Options...")
        self._open_advanced_options()
        time.sleep(0.5)
        
        if config.exclude_styles:
            logger.info(f"Exclude Styles: {config.exclude_styles}")
            try:
                # Playwright verified: Suno dùng <input> thật
                exclude_selectors = [
                    "//input[contains(@placeholder, 'Exclude styles')]",
                    "//textarea[contains(@placeholder, 'Exclude styles')]",
                    "//*[@role='textbox' and contains(@placeholder, 'Exclude styles')]",
                ]
                
                exclude_box = None
                for selector in exclude_selectors:
                    try:
                        exclude_box = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except TimeoutException:
                        continue
                
                if exclude_box:
                    exclude_box.clear()
                    exclude_box.send_keys(config.exclude_styles)
                    logger.info("✓ Đã nhập Exclude Styles")
                else:
                    logger.warning("Không tìm thấy Exclude Styles input")
            except Exception as e:
                logger.warning(f"Lỗi khi nhập Exclude Styles: {e}")
        
        if config.vocal_gender:
            logger.info(f"Vocal Gender: {config.vocal_gender}")
            try:
                # Playwright: get_by_role("button", name="Male", exact=True)
                gender_btn = self.driver.find_element(
                    By.XPATH, 
                    f"//button[normalize-space(.)='{config.vocal_gender}']"
                )
                gender_btn.click()
                time.sleep(0.3)
                logger.info(f"✓ Đã chọn {config.vocal_gender}")
            except NoSuchElementException:
                logger.warning(f"Không tìm thấy button {config.vocal_gender}")
        
        if config.lyrics_mode:
            logger.info(f"Lyrics Mode: {config.lyrics_mode}")
            try:
                # Playwright: get_by_role("button", name="Manual")
                mode_btn = self.driver.find_element(
                    By.XPATH,
                    f"//button[normalize-space(.)='{config.lyrics_mode}']"
                )
                mode_btn.click()
                time.sleep(0.3)
                logger.info(f"✓ Đã chọn {config.lyrics_mode}")
            except NoSuchElementException:
                logger.warning(f"Không tìm thấy button {config.lyrics_mode}")
        
        if config.weirdness is not None:
            logger.info(f"Weirdness: {config.weirdness}%")
            try:
                # Set slider value qua JavaScript
                weirdness_slider = self.driver.find_element(By.XPATH, "//input[@type='range' and contains(@aria-label, 'weirdness')]")
                self.driver.execute_script(f"arguments[0].value = {config.weirdness}; arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", weirdness_slider)
            except NoSuchElementException:
                logger.warning("Không tìm thấy Weirdness slider")
        
        if config.style_influence is not None:
            logger.info(f"Style Influence: {config.style_influence}%")
            try:
                # Set slider value qua JavaScript
                influence_slider = self.driver.find_element(By.XPATH, "//input[@type='range' and contains(@aria-label, 'style influence')]")
                self.driver.execute_script(f"arguments[0].value = {config.style_influence}; arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", influence_slider)
            except NoSuchElementException:
                logger.warning("Không tìm thấy Style Influence slider")
        
        logger.info("✓ Đã cấu hình Advanced Options")
    
    def _create_and_wait(self, config: SunoCreateConfig) -> list:
        """
        Click Create và chờ kết quả
        
        Args:
            config: Cấu hình (chứa wait_for_generation và timeout)
            
        Returns:
            List các URL bài hát đã tạo
        """
        logger.info("Click nút 'Create'...")
        try:
            # Tìm nút Create - có thể là "Create" hoặc "Create song"
            create_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') and not(@disabled)]"))
            )
            create_btn.click()
            logger.info("✓ Đã click Create")
        except TimeoutException:
            logger.error("Nút Create không khả dụng (có thể thiếu thông tin)")
            return []
        
        if not config.wait_for_generation:
            logger.info("Không chờ generation (tắt wait_for_generation)")
            return []
        
        logger.info(f"Chờ AI tạo nhạc (timeout: {config.timeout}s)...")
        
        # Polling để chờ bài hát xuất hiện
        start_time = time.time()
        song_urls = []
        
        while time.time() - start_time < config.timeout:
            try:
                # Tìm các song cards mới (có class chứa "song" hoặc "clip")
                song_cards = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'song-card') or contains(@class, 'clip-card')]//a[contains(@href, '/song/')]"
                )
                
                if song_cards:
                    # Extract URLs
                    song_urls = [card.get_attribute('href') for card in song_cards[:2]]  # Suno tạo 2 version
                    logger.info(f"✓ Tìm thấy {len(song_urls)} bài hát")
                    break
                
                # Chờ 5s trước khi kiểm tra lại
                elapsed = int(time.time() - start_time)
                logger.info(f"Đang chờ... ({elapsed}s/{config.timeout}s)")
                time.sleep(5)
                
            except Exception as e:
                logger.warning(f"Lỗi khi tìm song cards: {e}")
                time.sleep(5)
        
        if not song_urls:
            logger.warning(f"Timeout sau {config.timeout}s, không thấy bài hát")
        
        return song_urls


# ============================================
# DEMO USAGE
# ============================================

def demo_with_ui_integration():
    """
    Demo: Tích hợp với UI App
    Giả lập gọi từ CreateMusicPanel
    """
    from src.core.session_manager import SessionManager
    
    # 1. Khởi tạo SessionManager (từ app)
    session_manager = SessionManager()
    
    # 2. Callback để cập nhật progress bar
    def update_progress(message: str, progress: int):
        print(f"[UI Progress] {progress}%: {message}")
    
    # 3. Tạo MusicCreator
    creator = SunoMusicCreator(
        session_manager=session_manager,
        progress_callback=update_progress
    )
    
    # 4. Config bài hát
    config = SunoCreateConfig(
        lyrics="""[Verse 1]
Sáng nay thức dậy thấy trời quá đẹp
Nắng vàng chan hòa khắp con phố

[Chorus]
Hãy cùng nhau vui ca hát
Cuộc sống thật tuyệt vời""",
        
        styles="Vietnamese Pop, upbeat, 128bpm, major key, guitar, piano, cheerful",
        title="Sáng Nắng",
        vocal_gender="Female",
        lyrics_mode="Manual",
        weirdness=30,
        style_influence=70,
    )
    
    # 5. Tạo bài hát từ account đã lưu
    account_name = "thang"  # Account trong suno_accounts.json
    result = creator.create_song(account_name, config)
    
    # 6. Xử lý kết quả
    if result["success"]:
        print(f"\n✅ Tạo nhạc thành công!")
        print(f"Steps: {', '.join(result['steps_completed'])}")
        print(f"Songs:")
        for url in result["song_urls"]:
            print(f"  🎵 {url}")
    else:
        print(f"\n❌ Lỗi: {result['error']}")


def demo_create_pop_song():
    """Demo: Tạo bài Pop Việt Nam (Legacy - Standalone)"""
    print("⚠️  Demo này cần SessionManager từ UI app")
    print("Dùng demo_with_ui_integration() thay thế")
    return
    
    config = SunoCreateConfig(
        # Bước 1: Không dùng persona
        persona_name=None,
        
        # Bước 2: Nội dung chính
        lyrics="""[Verse 1]
Sáng nay thức dậy thấy trời quá đẹp
Nắng vàng chan hòa khắp con phố

[Chorus]
Hãy cùng nhau vui ca hát
Cuộc sống thật tuyệt vời""",
        
        styles="Vietnamese Pop, upbeat, 128bpm, major key, guitar, piano, cheerful, catchy melody",
        
        title="Sáng Nắng",
        
        # Bước 3: Advanced Options
        vocal_gender="Female",
        lyrics_mode="Manual",
        weirdness=30,
        style_influence=70,
    )
    
    creator = SunoAutoCreator()
    result = creator.create_song(config)
    
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ:")
    print(f"   Success: {result['success']}")
    print(f"   Steps: {', '.join(result['steps_completed'])}")
    if result['song_urls']:
        print(f"   Songs:")
        for url in result['song_urls']:
            print(f"      - {url}")
    print("=" * 60)


def demo_create_edm_with_persona():
    """Demo: Tạo EDM với Persona"""
    config = SunoCreateConfig(
        # Bước 1: Dùng persona
        persona_name="DJ Storm",
        
        # Bước 2: Instrumental (không lời)
        lyrics="",  # Để trống
        styles="festival anthem, epic drop, build-up",
        title="Neon Pulse",
        
        # Bước 3: Advanced
        weirdness=65,
        style_influence=85,
    )
    
    creator = SunoAutoCreator()
    result = creator.create_song(config)
    
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ:")
    print(f"   Success: {result['success']}")
    print(f"   Steps: {', '.join(result['steps_completed'])}")
    if result['song_urls']:
        print(f"   Songs:")
        for url in result['song_urls']:
            print(f"      - {url}")
    print("=" * 60)


def demo_create_ballad_with_persona():
    """Demo: Tạo Ballad với Persona 'Thang'"""
    config = SunoCreateConfig(
        # Bước 1: Dùng persona có sẵn
        persona_name="Thang",
        
        # Bước 2: Nội dung
        lyrics="""[Verse 1]
Đêm nay trăng sáng như ngày xưa
Em còn nhớ không những lời thề

[Chorus]
Dù xa cách nhưng tình vẫn mãi
Mãi trong tim anh không phai""",
        
        styles="",  # Persona sẽ tự động điền
        title="Đêm Trăng Nhớ",
        
        # Bước 3: Minimal advanced options
        lyrics_mode="Manual",
    )
    
    creator = SunoAutoCreator()
    result = creator.create_song(config)
    
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ:")
    print(f"   Success: {result['success']}")
    print(f"   Steps: {', '.join(result['steps_completed'])}")
    if result['song_urls']:
        print(f"   Songs:")
        for url in result['song_urls']:
            print(f"      - {url}")
    print("=" * 60)


if __name__ == "__main__":
    print("🎵 SUNO AUTO MUSIC CREATION - DEMO")
    print("=" * 60)
    print("Chọn demo:")
    print("1. Tạo bài Pop Việt Nam (không persona)")
    print("2. Tạo EDM với Persona 'DJ Storm'")
    print("3. Tạo Ballad với Persona 'Thang'")
    print("=" * 60)
    
    choice = input("Nhập số (1-3): ").strip()
    
    if choice == "1":
        demo_create_pop_song()
    elif choice == "2":
        demo_create_edm_with_persona()
    elif choice == "3":
        demo_create_ballad_with_persona()
    else:
        print("❌ Lựa chọn không hợp lệ!")
