"""
Batch Download Suno Songs - Tích hợp với Multi Account Manager
Dựa trên bulk-suno-py-2 với cải tiến cho multi-account
"""
import os
import re
import time
import json
import random
import requests
from pathlib import Path
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

class SunoBatchDownloader:
    def __init__(self, session_token=None, proxy_list=None):
        """
        Khởi tạo downloader
        
        Args:
            session_token: JWT token từ cookies (cookie __session)
            proxy_list: List các proxy (optional)
        """
        self.session_token = session_token
        self.proxy_list = proxy_list or []
        self.base_url = "https://studio-api.prod.suno.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        if self.session_token:
            self.headers['Authorization'] = f'Bearer {self.session_token}'
        
        # File lưu lịch sử download
        self.history_file = Path("download_history.json")
    
    def load_download_history(self, account_name):
        """Load lịch sử download của account"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history.get(account_name, {
                        'downloaded_ids': [],
                        'total_downloaded': 0,
                        'current_page': 0,
                        'last_profile': ''
                    })
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Lỗi khi load history: {str(e)}")
        
        return {
            'downloaded_ids': [],
            'total_downloaded': 0,
            'current_page': 0,
            'last_profile': ''
        }
    
    def save_download_history(self, account_name, history_data):
        """Lưu lịch sử download của account"""
        try:
            # Load toàn bộ history
            all_history = {}
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    all_history = json.load(f)
            
            # Update cho account hiện tại
            all_history[account_name] = history_data
            
            # Save lại file
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(all_history, f, indent=4, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✓ Đã lưu lịch sử trang {history_data.get('current_page', 0)}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi khi save history: {str(e)}")
    
    def get_random_proxy(self):
        """Lấy proxy ngẫu nhiên từ list"""
        if not self.proxy_list:
            return None
        return {'http': random.choice(self.proxy_list), 'https': random.choice(self.proxy_list)}
    
    def sanitize_filename(self, name):
        """Làm sạch tên file, loại bỏ ký tự không hợp lệ"""
        # Loại bỏ các ký tự không hợp lệ
        invalid_chars = r'<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        
        # Loại bỏ control characters
        name = re.sub(r'[\x00-\x1f\x7f]', '', name)
        
        # Trim spaces và dots ở cuối
        name = name.strip().rstrip('.')
        
        # Nếu tên rỗng, dùng tên mặc định
        if not name:
            name = "untitled"
        
        return name
    
    def ensure_unique_filename(self, directory, base_name, extension='.mp3'):
        """Đảm bảo tên file không trùng lặp"""
        file_path = Path(directory) / f"{base_name}{extension}"
        
        if not file_path.exists():
            return str(file_path)
        
        counter = 2
        while True:
            new_name = f"{base_name} ({counter}){extension}"
            file_path = Path(directory) / new_name
            if not file_path.exists():
                return str(file_path)
            counter += 1
    
    def fetch_profile_clips(self, profile_name, start_page=0, max_pages=None):
        """
        Lấy clips từ profile theo page
        
        Args:
            profile_name: Tên profile (VD: @username)
            start_page: Trang bắt đầu (0-indexed)
            max_pages: Số trang tối đa cần fetch (None = không giới hạn)
        
        Returns:
            Tuple (clips_list, last_page, has_more)
        """
        print(f"\n{Fore.CYAN}📥 Đang lấy clips từ profile: {profile_name} (bắt đầu từ trang {start_page})")
        
        # Bỏ @ nếu có
        if profile_name.startswith('@'):
            profile_name = profile_name[1:]
        
        url = f"{self.base_url}/profiles/{profile_name}/clips"
        all_clips = []
        page = start_page
        retry_wait = 10
        pages_fetched = 0
        
        while True:
            # Kiểm tra giới hạn số trang
            if max_pages and pages_fetched >= max_pages:
                print(f"{Fore.YELLOW}⚠️  Đã đạt giới hạn {max_pages} trang")
                return all_clips, page - 1, True
            
            try:
                params = {'page': page}
                proxies = self.get_random_proxy()
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    proxies=proxies,
                    timeout=30
                )
                
                if response.status_code == 429:
                    print(f"{Fore.YELLOW}⚠️  Rate limit (429), đợi {retry_wait}s...")
                    time.sleep(retry_wait)
                    retry_wait = min(retry_wait + 5, 60)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                clips = data.get('clips', [])
                if not clips:
                    # Không còn clips nữa
                    print(f"{Fore.GREEN}✅ Đã hết clips ở trang {page}")
                    return all_clips, page - 1, False
                
                all_clips.extend(clips)
                print(f"{Fore.GREEN}✓ Page {page}: {len(clips)} clips")
                
                page += 1
                pages_fetched += 1
                time.sleep(5)  # Đợi giữa các page
                retry_wait = 10  # Reset retry wait
                
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}❌ Lỗi khi fetch page {page}: {str(e)}")
                return all_clips, page - 1, False
        
        print(f"{Fore.GREEN}✅ Tổng cộng: {len(all_clips)} clips")
        return all_clips, page - 1, False
    
    def fetch_my_clips(self):
        """
        Lấy tất cả clips của user hiện tại (từ /me)
        
        Returns:
            List các clip info
        """
        print(f"\n{Fore.CYAN}📥 Đang lấy clips của bạn từ /me...")
        
        url = f"{self.base_url}/feed/v2"
        params = {'page': 0}
        all_clips = []
        retry_wait = 10
        
        try:
            proxies = self.get_random_proxy()
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                proxies=proxies,
                timeout=30
            )
            
            if response.status_code == 429:
                print(f"{Fore.YELLOW}⚠️  Rate limit (429), đợi {retry_wait}s...")
                time.sleep(retry_wait)
                return []
            
            response.raise_for_status()
            data = response.json()
            
            # Lấy clips từ feed
            clips = data.get('clips', [])
            all_clips.extend(clips)
            
            print(f"{Fore.GREEN}✅ Tìm thấy: {len(all_clips)} clips")
            return all_clips
            
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Lỗi khi fetch clips: {str(e)}")
            return []
    
    def get_current_user_info(self):
        """
        Lấy thông tin user hiện tại
        
        Returns:
            Dict chứa user info (username, email, etc.)
        """
        try:
            url = f"{self.base_url}/billing/info"
            proxies = self.get_random_proxy()
            
            response = requests.get(
                url,
                headers=self.headers,
                proxies=proxies,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Trích xuất username từ response
            user_info = {
                'username': data.get('display_name', ''),
                'email': data.get('email', ''),
                'credits': data.get('total_credits_left', 0)
            }
            
            print(f"{Fore.GREEN}✓ User: @{user_info['username']}, Credits: {user_info['credits']}")
            return user_info
            
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Lỗi khi lấy user info: {str(e)}")
            return None
    
    def fetch_clips_by_uuids(self, uuids):
        """
        Lấy thông tin clips theo UUIDs
        
        Args:
            uuids: List hoặc set các UUID
        
        Returns:
            List các clip info
        """
        print(f"\n{Fore.CYAN}📥 Đang lấy {len(uuids)} clips theo UUID...")
        
        clips = []
        for idx, uuid in enumerate(uuids, 1):
            try:
                url = f"{self.base_url}/clips/{uuid}"
                proxies = self.get_random_proxy()
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    proxies=proxies,
                    timeout=30
                )
                
                if response.status_code == 429:
                    print(f"{Fore.YELLOW}⚠️  Rate limit, đợi 10s...")
                    time.sleep(10)
                    response = requests.get(url, headers=self.headers, proxies=proxies, timeout=30)
                
                response.raise_for_status()
                clip_data = response.json()
                clips.append(clip_data)
                
                print(f"{Fore.GREEN}✓ [{idx}/{len(uuids)}] {clip_data.get('title', 'Unknown')}")
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}❌ Lỗi khi fetch UUID {uuid}: {str(e)}")
        
        return clips

    def fetch_my_clips_paginated(self, start_page: int = 0, max_pages: int | None = None):
        """
        Fetch clips from the user's feed (/feed/v2) across multiple pages.

        Args:
            start_page: page index to start from
            max_pages: maximum number of pages to fetch (None == all available)

        Returns:
            (all_clips, last_page, has_more)
        """
        print(f"\n{Fore.CYAN}📥 Đang lấy clips từ /feed/v2 (create/me) ...")

        url = f"{self.base_url}/feed/v2"
        current_page = start_page
        all_clips = []
        pages_fetched = 0

        while True:
            params = {"page": current_page}
            try:
                proxies = self.get_random_proxy()
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    proxies=proxies,
                    timeout=30
                )

                if response.status_code == 429:
                    print(f"{Fore.YELLOW}⚠️  Rate limit (429), đợi 10s...")
                    time.sleep(10)
                    continue

                response.raise_for_status()
                data = response.json()

                clips = data.get("clips", [])
                all_clips.extend(clips)

                # Determine has_more: server may include pagination metadata
                has_more = bool(data.get("has_more", False))
                # Fallback: if clips length < page size then no more
                if not has_more and len(clips) == 0:
                    has_more = False

                pages_fetched += 1

                print(f"{Fore.GREEN}✓ Trang {current_page}: Tìm thấy {len(clips)} clips (tổng: {len(all_clips)})")

                # Check stopping conditions
                if max_pages is not None and pages_fetched >= max_pages:
                    return all_clips, current_page, True

                if not has_more:
                    return all_clips, current_page, False

                current_page += 1
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}❌ Lỗi khi fetch feed page {current_page}: {str(e)}")
                return all_clips, current_page, False
    
    def download_audio(self, clip_info, directory, append_uuid=False):
        """
        Download file audio từ clip info
        
        Args:
            clip_info: Dict chứa thông tin clip
            directory: Thư mục lưu file
            append_uuid: Có thêm UUID vào tên file không
        
        Returns:
            Path đến file đã download hoặc None nếu thất bại
        """
        title = clip_info.get('title', 'Untitled')
        clip_id = clip_info.get('id', 'unknown')
        audio_url = clip_info.get('audio_url')
        
        if not audio_url:
            print(f"{Fore.YELLOW}⚠️  Không có audio_url cho: {title}")
            return None
        
        # Tạo tên file
        safe_title = self.sanitize_filename(title)
        if append_uuid:
            base_name = f"{safe_title}__ID__{clip_id}"
        else:
            base_name = safe_title
        
        # Đảm bảo tên file unique
        file_path = self.ensure_unique_filename(directory, base_name)
        
        try:
            proxies = self.get_random_proxy()
            response = requests.get(audio_url, proxies=proxies, stream=True, timeout=60)
            response.raise_for_status()
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(file_path)
            print(f"{Fore.GREEN}✓ Downloaded: {Path(file_path).name} ({file_size/1024/1024:.2f} MB)")
            
            return file_path
            
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi khi download {title}: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    def download_thumbnail(self, clip_info, directory):
        """Download thumbnail/cover art"""
        image_url = clip_info.get('image_url')
        if not image_url:
            return None
        
        clip_id = clip_info.get('id', 'unknown')
        file_path = Path(directory) / f"{clip_id}_cover.jpg"
        
        try:
            proxies = self.get_random_proxy()
            response = requests.get(image_url, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return str(file_path)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Không download được thumbnail: {str(e)}")
            return None
    
    def embed_metadata(self, audio_path, clip_info, thumbnail_path=None):
        """Nhúng metadata vào file MP3"""
        try:
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TPUB, WOAR, APIC
            from mutagen.mp3 import MP3
            
            audio = MP3(audio_path, ID3=ID3)
            
            # Xóa ID3 tags cũ nếu có
            try:
                audio.delete()
            except:
                pass
            
            # Tạo ID3 tags mới
            audio.add_tags()
            
            # Thêm metadata cơ bản
            audio.tags.add(TIT2(encoding=3, text=clip_info.get('title', '')))
            
            if clip_info.get('display_name'):
                audio.tags.add(TPE1(encoding=3, text=clip_info['display_name']))
            
            if clip_info.get('metadata', {}).get('tags'):
                audio.tags.add(TCON(encoding=3, text=', '.join(clip_info['metadata']['tags'])))
            
            if clip_info.get('display_name'):
                audio.tags.add(TPUB(encoding=3, text=clip_info['display_name']))
            
            # Thêm URL
            song_url = f"https://suno.com/song/{clip_info.get('id', '')}"
            audio.tags.add(WOAR(url=song_url))
            
            # Thêm cover art
            if thumbnail_path and os.path.exists(thumbnail_path):
                with open(thumbnail_path, 'rb') as img:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=img.read()
                        )
                    )
            
            audio.save()
            print(f"{Fore.GREEN}✓ Đã nhúng metadata cho: {Path(audio_path).name}")
            
        except ImportError:
            print(f"{Fore.YELLOW}⚠️  mutagen chưa cài đặt, bỏ qua metadata")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Lỗi khi nhúng metadata: {str(e)}")
    
    def batch_download_with_pagination(self, profile_name, directory, account_name, 
                                      max_songs_per_page=20, resume=False, 
                                      with_thumbnail=False, append_uuid=False,
                                      use_create_page: bool = False):
        """
        Batch download với hỗ trợ pagination và resume
        
        Args:
            profile_name: Tên profile để download (VD: @username)
            directory: Thư mục lưu file
            account_name: Tên account (để lưu history)
            max_songs_per_page: Số bài tối đa mỗi trang (mặc định 20)
            resume: Tiếp tục từ trang đã lưu (True/False)
            with_thumbnail: Download và nhúng thumbnail
            append_uuid: Thêm UUID vào tên file
        
        Returns:
            Dict chứa thống kê download
        """
        # Load lịch sử
        history = self.load_download_history(account_name)
        downloaded_ids = set(history.get('downloaded_ids', []))
        
        # Xác định trang bắt đầu
        if resume and history.get('last_profile') == profile_name:
            start_page = history.get('current_page', 0)
            print(f"{Fore.CYAN}🔄 Tiếp tục từ trang {start_page} (đã tải {len(downloaded_ids)} bài)")
        else:
            start_page = 0
            if not resume:
                # Reset history nếu không resume
                downloaded_ids = set()
            print(f"{Fore.CYAN}🆕 Bắt đầu mới từ trang 0")
        
        # Tạo thư mục
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        total_success = 0
        total_fail = 0
        current_page = start_page
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎵 BATCH DOWNLOAD TỪ PROFILE: {profile_name}")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        while True:
            print(f"\n{Fore.YELLOW}📄 Đang xử lý trang {current_page}...")
            
            # Fetch clips từ trang hiện tại (chỉ lấy 1 trang)
            if use_create_page:
                # Fetch from /feed/v2 (create or /me context)
                # fetch_my_clips_paginated returns (clips_all, last_page, has_more)
                clips_all, last_page, has_more = self.fetch_my_clips_paginated(start_page=current_page, max_pages=1)
                clips = clips_all
            else:
                clips, last_page, has_more = self.fetch_profile_clips(
                    profile_name, 
                    start_page=current_page,
                    max_pages=1
                )
            
            if not clips:
                print(f"{Fore.GREEN}✅ Đã tải hết tất cả bài hát!")
                break
            
            # Lọc bỏ các bài đã download
            new_clips = [c for c in clips if c.get('id') not in downloaded_ids]
            
            if not new_clips:
                print(f"{Fore.YELLOW}⚠️  Trang {current_page}: Tất cả {len(clips)} bài đã được tải")
                current_page += 1
                
                # Update history
                history['current_page'] = current_page
                history['last_profile'] = profile_name
                self.save_download_history(account_name, history)
                
                if not has_more:
                    print(f"{Fore.GREEN}✅ Đã hết clips!")
                    break
                continue
            
            print(f"{Fore.CYAN}📥 Trang {current_page}: {len(new_clips)}/{len(clips)} bài mới")
            
            # Download từng bài
            page_success = 0
            page_fail = 0
            
            for idx, clip in enumerate(new_clips, 1):
                clip_id = clip.get('id')
                title = clip.get('title', 'Unknown')
                
                print(f"\n{Fore.CYAN}[{idx}/{len(new_clips)}] {title}")
                
                # Download audio
                audio_path = self.download_audio(clip, directory, append_uuid)
                
                if audio_path:
                    page_success += 1
                    total_success += 1
                    
                    # Thêm vào downloaded_ids
                    downloaded_ids.add(clip_id)
                    
                    # Download thumbnail và nhúng metadata
                    if with_thumbnail:
                        thumbnail_path = self.download_thumbnail(clip, directory)
                        self.embed_metadata(audio_path, clip, thumbnail_path)
                        
                        # Xóa thumbnail file sau khi nhúng
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)
                else:
                    page_fail += 1
                    total_fail += 1
                
                # Đợi giữa các downloads
                if idx < len(new_clips):
                    time.sleep(2)
                
                # Update history sau mỗi bài thành công
                if audio_path:
                    history['downloaded_ids'] = list(downloaded_ids)
                    history['total_downloaded'] = len(downloaded_ids)
                    history['current_page'] = current_page
                    history['last_profile'] = profile_name
                    history['last_download'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.save_download_history(account_name, history)
            
            print(f"\n{Fore.GREEN}✓ Trang {current_page}: Thành công {page_success}/{len(new_clips)}")
            
            # Chuyển sang trang tiếp theo
            current_page += 1
            
            # Update history trang
            history['current_page'] = current_page
            history['last_profile'] = profile_name
            self.save_download_history(account_name, history)
            
            # Kiểm tra còn trang nữa không
            if not has_more:
                print(f"{Fore.GREEN}✅ Đã hết clips!")
                break
            
            print(f"{Fore.YELLOW}➡️  Chuyển sang trang {current_page}...")
            time.sleep(3)  # Đợi trước khi fetch trang mới
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}✅ HOÀN TẤT!")
        print(f"{Fore.GREEN}   Tổng thành công: {total_success}")
        print(f"{Fore.RED}   Tổng thất bại: {total_fail}")
        print(f"{Fore.CYAN}   Trang cuối: {current_page - 1}")
        print(f"{Fore.CYAN}   Tổng đã tải: {len(downloaded_ids)} bài")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        return {
            'success': total_success,
            'failed': total_fail,
            'total_downloaded': len(downloaded_ids),
            'last_page': current_page - 1
        }
    
    def batch_download(self, clips, directory, with_thumbnail=False, append_uuid=False):
        """
        Batch download nhiều clips (phương thức cũ - giữ lại để tương thích)
        
        Args:
            clips: List các clip info
            directory: Thư mục lưu file
            with_thumbnail: Download và nhúng thumbnail
            append_uuid: Thêm UUID vào tên file
        """
        # Tạo thư mục nếu chưa có
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎵 BẮT ĐẦU DOWNLOAD {len(clips)} SONGS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        success_count = 0
        fail_count = 0
        
        for idx, clip in enumerate(clips, 1):
            title = clip.get('title', 'Unknown')
            print(f"\n{Fore.CYAN}[{idx}/{len(clips)}] {title}")
            
            # Download audio
            audio_path = self.download_audio(clip, directory, append_uuid)
            
            if audio_path:
                success_count += 1
                
                # Download thumbnail và nhúng metadata
                if with_thumbnail:
                    thumbnail_path = self.download_thumbnail(clip, directory)
                    self.embed_metadata(audio_path, clip, thumbnail_path)
                    
                    # Xóa thumbnail file sau khi nhúng
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)
            else:
                fail_count += 1
            
            # Đợi một chút giữa các downloads
            if idx < len(clips):
                time.sleep(2)
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}✅ Thành công: {success_count}")
        print(f"{Fore.RED}❌ Thất bại: {fail_count}")
        print(f"{Fore.CYAN}{'='*70}\n")


def main():
    """Test function - sẽ được tích hợp vào suno_multi_account.py"""
    print("Batch Downloader Test")
    print("Chức năng này sẽ được tích hợp vào suno_multi_account.py")

if __name__ == "__main__":
    main()
