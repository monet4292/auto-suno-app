"""
Batch Song Creator - Business logic tạo nhiều bài hát
"""
import time
import math
import random
from typing import List, Callable, Dict, Any, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from src.utils.prompt_parser import SunoPrompt
from src.ui.components.suno_selectors import SunoSelectors
from src.utils import logger
from src.utils.stealth_driver import add_human_delays, create_stealth_driver
from src.models import SongCreationRecord
from src.core.song_creation_history_manager import SongCreationHistoryManager


class BatchSongCreator:
    """
    Business logic tạo nhiều bài hát cùng lúc
    
    Features:
    - Mở nhiều tabs Chrome
    - Fill form song song
    - Apply advanced options
    - Auto-submit (optional)
    - Progress callback
    """
    
    def __init__(self, profile_path: Path):
        """
        Args:
            profile_path: Đường dẫn đến Chrome profile
        """
        self.profile_path = profile_path
        self.driver = None
    
    def create_songs_batch(
        self,
        prompts: List[SunoPrompt],
        songs_per_session: int,
        advanced_options: Dict[str, Any],
        auto_submit: bool,
        progress_callback: Callable[[str, int, Optional[str], str, str], None],
        account_name: str | None = None,
        history_manager: SongCreationHistoryManager | None = None
    ) -> List[Dict[str, Any]]:
        """
        Tạo nhiều bài hát theo batch
        
        Args:
            prompts: List of SunoPrompt
            batch_size: Số bài mỗi batch
            advanced_options: Dict chứa advanced settings
            keep_browser: Giữ browser mở 30s sau khi xong
            auto_submit: Tự động bấm Create (có thể gặp CAPTCHA)
            progress_callback: Callback(message, progress_percent)
        
        Returns:
            List of {title, success, error}
        """
        results: List[Dict[str, Any]] = []
        if not prompts:
            return results

        progress_callback = progress_callback or (lambda *_: None)
        session_size = max(1, songs_per_session)
        total_songs = len(prompts)
        session_count = (total_songs + session_size - 1) // session_size

        completed_songs = 0

        try:
            self._initialize_driver()
            for session_index in range(session_count):
                start_idx = session_index * session_size
                session_prompts = prompts[start_idx:start_idx + session_size]
                logger.info(f"⏳ Session {session_index + 1}/{session_count} contains {len(session_prompts)} prompts")

                try:
                    session_results = self._run_session(
                        session_prompts,
                        advanced_options,
                        auto_submit,
                        progress_callback,
                        session_index,
                        session_count,
                        completed_songs,
                        total_songs,
                        account_name=account_name,
                        history_manager=history_manager
                    )
                    results.extend(session_results)
                except Exception as exc:
                    logger.error(f"❌ Session error: {exc}")
                    results.append({'title': 'SESSION ERROR', 'success': False, 'error': str(exc)})
                finally:
                    completed_songs += len(session_prompts)
        finally:
            self._teardown_driver()

        progress_callback("✅ Hoàn thành!", 100, None, "complete", "Batch finished")
        return results

    def _initialize_driver(self) -> None:
        if self.driver:
            self.driver.quit()
        self.driver = create_stealth_driver(self.profile_path, headless=False)

    def _teardown_driver(self) -> None:
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _run_session(
        self,
        prompts: List[SunoPrompt],
        advanced_options: Dict[str, Any],
        auto_submit: bool,
        progress_callback: Callable[[str, int, Optional[str], str, str], None],
        session_index: int,
        session_count: int,
        completed_before_session: int,
        total_songs: int,
        account_name: str | None = None,
        history_manager: SongCreationHistoryManager | None = None
    ) -> List[Dict[str, Any]]:
        if not self.driver:
            return []

        results: List[Dict[str, Any]] = []
        self.driver.get("https://suno.com/create")
        for _ in range(1, len(prompts)):
            self.driver.execute_script("window.open('https://suno.com/create', '_blank');")
            time.sleep(0.5)

        tabs = self.driver.window_handles

        for prompt_index, prompt in enumerate(prompts):
            tab_handle = tabs[prompt_index]
            progress_percent = min(
                100,
                int(((completed_before_session + prompt_index + 1) / total_songs) * 100)
            )
            message = (
                f"✍️ Session {session_index + 1}/{session_count} - "
                f"Bài {prompt_index + 1}/{len(prompts)}: {prompt.title}"
            )

            success = self._fill_song_form(prompt, tab_handle, advanced_options, prompt_index + 1)
            song_id: Optional[str] = None
            error_message: Optional[str] = None
            status_label = "success"

            if success:
                if auto_submit:
                    try:
                        delay = random.uniform(2, 5)
                        logger.info(f"⏳ Tab {prompt_index + 1}: đợi {delay:.2f}s trước khi submit")
                        time.sleep(delay)
                        song_id = self._submit_and_get_id(tab_handle)
                        logger.info(f"✅ Song created (auto) tab {prompt_index + 1}: {song_id}")
                    except TimeoutException:
                        status_label = "pending"
                        error_message = "Đã gửi yêu cầu – chờ ID"
                        logger.info(f"⏳ Song pending (tab {prompt_index + 1}) - waiting for ID")
                    except Exception as exc:
                        logger.error(f"❌ Auto-submit failed: {exc}")
                        success = False
                        status_label = "failed"
                        error_message = str(exc)
                else:
                    status_label = "pending"
                    logger.info(f"ℹ️ Tab {prompt_index + 1} ready for manual submit")
            else:
                status_label = "failed"
                error_message = "Fill form failed"

            results.append({
                'title': prompt.title,
                'success': success,
                'pending': status_label == "pending",
                'error': None if success else error_message
            })

            self._record_history_entry(
                history_manager,
                account_name,
                prompt,
                completed_before_session + prompt_index + 1,
                song_id,
                status_label,
                error_message
            )

            progress_callback(message, progress_percent, song_id, status_label, prompt.title)
            time.sleep(3)

        return results

    def _record_history_entry(
        self,
        history_manager: SongCreationHistoryManager | None,
        account_name: str | None,
        prompt: SunoPrompt,
        prompt_index: int,
        song_id: str | None,
        status_label: str,
        error_message: Optional[str]
    ) -> None:
        if not history_manager:
            return

        record = SongCreationRecord(
            song_id=song_id or "",
            title=prompt.title,
            prompt_index=prompt_index,
            account_name=account_name or self.profile_path.name,
            status=status_label,
            error_message=error_message
        )
        history_manager.add_creation_record(record)

    def _submit_and_get_id(self, tab_handle: str) -> str:
        if not self.driver:
            raise RuntimeError("WebDriver is not initialized")
        self.driver.switch_to.window(tab_handle)
        create_btn = self.driver.find_element(By.XPATH, SunoSelectors.CREATE_BUTTON)
        create_btn.click()
        WebDriverWait(self.driver, 20).until(
            EC.url_contains("/song/")
        )
        return self._extract_song_id(self.driver.current_url)

    def _extract_song_id(self, url: str) -> str:
        parsed = url.rstrip("/").split("/")
        return parsed[-1] if parsed else ""
    
    def _fill_song_form(
        self,
        prompt: SunoPrompt,
        tab_handle: str,
        advanced_options: Dict[str, Any],
        tab_index: int
    ) -> bool:
        """Fill form cho 1 bài hát"""
        try:
            add_human_delays()
            self.driver.switch_to.window(tab_handle)

            lyrics_inputs = self.driver.find_elements(By.XPATH, SunoSelectors.LYRICS_TEXTAREA)
            if not lyrics_inputs:
                custom_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, SunoSelectors.CUSTOM_BUTTON))
                )
                custom_btn.click()
                time.sleep(2)

            add_human_delays()
            lyrics_box = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, SunoSelectors.LYRICS_TEXTAREA))
            )
            lyrics_box.clear()
            lyrics_box.send_keys(prompt.lyrics)

            add_human_delays()
            styles_box = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, SunoSelectors.STYLES_TEXTAREA))
            )
            styles_box.clear()
            styles_box.send_keys(prompt.style)

            add_human_delays()
            title_filled = False
            try:
                title_box = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, SunoSelectors.TITLE_INPUT))
                )
                title_box.clear()
                title_box.send_keys(prompt.title)
                title_filled = True
            except Exception:
                try:
                    title_box = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, SunoSelectors.TITLE_INPUT_BY_LABEL)
                        )
                    )
                    title_box.click()
                    time.sleep(0.2)
                    title_box.clear()
                    title_box.send_keys(prompt.title)
                    title_filled = True
                except Exception:
                    pass

            if not title_filled:
                try:
                    js = """
                    const els = Array.from(document.querySelectorAll('input[placeholder="Song Title (Optional)"]'));
                    const el = els.find(e => e && e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden');
                    if(!el) return {ok:false, reason:'not-found-visible'};
                    el.scrollIntoView({block:'center'});
                    el.focus();
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(el, '');
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    setter.call(el, arguments[0]);
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    return {ok: el.value === arguments[0], value: el.value};
                    """
                    res = self.driver.execute_script(js, prompt.title)
                    if res and res.get('ok'):
                        title_filled = True
                        logger.info(f"TAB {tab_index}: JS fallback Title OK → '{res.get('value')}'")
                    else:
                        logger.warning(f"TAB {tab_index}: JS fallback Title fail: {res}")
                except Exception as e:
                    logger.warning(f"TAB {tab_index}: JS fallback Title exception: {e}")

            if not title_filled:
                logger.warning(f"TAB {tab_index}: Không tìm thấy ô nhập Title, bỏ qua.")

            if advanced_options.get('enabled'):
                self._apply_advanced_options(advanced_options, tab_index)

            logger.info(f"✅ TAB {tab_index}: Filled {prompt.title}")
            return True
        except Exception as e:
            logger.error(f"❌ TAB {tab_index} error: {e}")
            return False
    
            title_filled = False
            try:
                title_box = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, SunoSelectors.TITLE_INPUT))
                )
                title_box.click(); time.sleep(0.2)
                title_box.clear(); title_box.send_keys(prompt.title)
                title_filled = True
            except Exception:
                # Fallback theo label
                try:
                    title_box = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, SunoSelectors.TITLE_INPUT_BY_LABEL))
                    )
                    title_box.click(); time.sleep(0.2)
                    title_box.clear(); title_box.send_keys(prompt.title)
                    title_filled = True
                except Exception:
                    pass

            # JS fallback cho React controlled input (nếu vẫn chưa điền được Title)
            if not title_filled:
                try:
                    js = """
                    const els = Array.from(document.querySelectorAll('input[placeholder="Song Title (Optional)"]'));
                    const el = els.find(e => e && e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden');
                    if(!el) return {ok:false, reason:'not-found-visible'};
                    el.scrollIntoView({block:'center'});
                    el.focus();
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(el, '');
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    setter.call(el, arguments[0]);
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    return {ok: el.value === arguments[0], value: el.value};
                    """
                    res = self.driver.execute_script(js, prompt.title)
                    if res and res.get('ok'):
                        title_filled = True
                        logger.info(f"TAB {tab_index}: JS fallback Title OK → '{res.get('value')}'")
                    else:
                        logger.warning(f"TAB {tab_index}: JS fallback Title fail: {res}")
                except Exception as e:
                    logger.warning(f"TAB {tab_index}: JS fallback Title exception: {e}")

            if not title_filled:
                logger.warning(f"TAB {tab_index}: Không tìm thấy ô nhập Title, bỏ qua.")
            
            # Apply Advanced Options
            if advanced_options['enabled']:
                self._apply_advanced_options(advanced_options, tab_index)
            
            logger.info(f"✅ TAB {tab_index}: Filled {prompt.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ TAB {tab_index} error: {e}")
            return False
    
    def _apply_advanced_options(self, options: Dict[str, Any], tab_index: int):
        """Áp dụng Advanced Options"""
        try:
            # Click Advanced Options button
            logger.info(f"TAB {tab_index}: Opening Advanced Options...")
            self.driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(1)
            
            try:
                advanced_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, SunoSelectors.ADVANCED_OPTIONS_BUTTON))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", advanced_btn)
                time.sleep(0.5)
                advanced_btn.click()
                time.sleep(1)
            except:
                logger.warning(f"TAB {tab_index}: Could not open Advanced Options")
                return
            
            # Exclude Styles
            if options['exclude_styles']:
                try:
                    exclude_input = self.driver.find_element(By.XPATH, SunoSelectors.EXCLUDE_STYLES_INPUT)
                    exclude_input.clear()
                    exclude_input.send_keys(options['exclude_styles'])
                    logger.info(f"TAB {tab_index}: Exclude styles = {options['exclude_styles']}")
                except:
                    pass
            
            # Vocal Gender
            if options['vocal_gender'] in ["Male", "Female"]:
                try:
                    selector = SunoSelectors.MALE_BUTTON if options['vocal_gender'] == "Male" else SunoSelectors.FEMALE_BUTTON
                    gender_btn = self.driver.find_element(By.XPATH, selector)
                    gender_btn.click()
                    time.sleep(0.5)
                except:
                    pass
            
            # Lyrics Mode
            if options['lyrics_mode'] in ["Manual", "Auto"]:
                try:
                    selector = SunoSelectors.MANUAL_LYRICS_BUTTON if options['lyrics_mode'] == "Manual" else SunoSelectors.AUTO_LYRICS_BUTTON
                    mode_btn = self.driver.find_element(By.XPATH, selector)
                    mode_btn.click()
                    time.sleep(0.5)
                except:
                    pass
            
            # Weirdness
            if options['weirdness'] != 50:
                try:
                    weirdness_slider = self.driver.find_element(By.XPATH, SunoSelectors.WEIRDNESS_SLIDER)
                    self._set_slider_value(weirdness_slider, options['weirdness'])
                except:
                    pass
            
            # Style Influence
            if options['style_influence'] != 50:
                try:
                    style_slider = self.driver.find_element(By.XPATH, SunoSelectors.STYLE_INFLUENCE_SLIDER)
                    self._set_slider_value(style_slider, options['style_influence'])
                except:
                    pass
            
            # Persona
            if options['persona_name']:
                try:
                    self._select_persona(options['persona_name'], tab_index)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"TAB {tab_index}: Error applying advanced options: {e}")
    
    def _set_slider_value(self, slider_element, percentage: int):
        """Set slider value"""
        current_value = int(slider_element.get_attribute('aria-valuenow'))
        min_value = int(slider_element.get_attribute('aria-valuemin'))
        max_value = int(slider_element.get_attribute('aria-valuemax'))
        
        if current_value == percentage:
            return
        
        slider_width = slider_element.size['width']
        current_position = (current_value - min_value) / (max_value - min_value)
        target_position = (percentage - min_value) / (max_value - min_value)
        drag_offset = (target_position - current_position) * slider_width
        
        actions = ActionChains(self.driver)
        actions.click_and_hold(slider_element)
        actions.move_by_offset(drag_offset, 0)
        actions.release()
        actions.perform()
        
        time.sleep(0.3)
    
    def _select_persona(self, persona_name: str, tab_index: int):
        """Chọn persona"""
        logger.info(f"TAB {tab_index}: Selecting persona '{persona_name}'...")
        
        # Scroll lên trên
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        
        # Click Persona button
        try:
            persona_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, SunoSelectors.PERSONA_BUTTON))
            )
            persona_btn.click()
            time.sleep(1.5)
        except:
            return
        
        # Search
        try:
            time.sleep(1)
            search_input = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, SunoSelectors.PERSONA_MODAL_SEARCH))
            )
            search_input.click()
            time.sleep(0.3)
            search_input.clear()
            search_input.send_keys(persona_name.lower())
            time.sleep(1.5)
        except:
            return
        
        # Click kết quả đầu tiên
        try:
            persona_containers = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, SunoSelectors.PERSONA_CONTAINER))
            )
            
            valid_personas = [c for c in persona_containers if "Create New Persona" not in c.text]
            
            if valid_personas:
                first_result = valid_personas[0]
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_result)
                time.sleep(0.5)
                first_result.click()
                time.sleep(1)
                logger.info(f"TAB {tab_index}: Persona selected")
        except:
            pass
    
    def stop(self):
        """Dừng quá trình"""
        if self.driver:
            self.driver.quit()
            self.driver = None
