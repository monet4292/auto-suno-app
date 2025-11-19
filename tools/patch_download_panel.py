#!/usr/bin/env python3
"""Patch download_panel.py to use paginated streaming"""

f = open('src/ui/download_panel.py', 'r', encoding='utf-8')
lines = f.readlines()
f.close()

# Replace lines 344-378 (the download logic block)
new_block = '''            # Use paginated streaming download to save memory
            self.update_progress("Đang chuẩn bị tải...", 10)

            # Determine start page from history if resume enabled
            start_page = 0
            if self.resume_var.get():
                history = self.download_manager.get_history(self.selected_account)
                # Start from page 0 and let history skip downloaded clips
                start_page = 0
            
            # Use batch_download_paginated for memory-efficient page-by-page processing
            stats = self.download_manager.batch_download_paginated(
                account_name=self.selected_account,
                session_token=session_token,
                output_dir=output_path,
                profile_name=profile_name,
                use_create_page=use_my_songs,
                start_page=start_page,
                max_pages=None,  # Download all pages
                with_thumbnail=self.thumbnail_var.get(),
                append_uuid=self.uuid_var.get(),
                progress_callback=self.update_progress,
                delay=2
            )

            # Show result
            message = (
                f"✅ Thành công: {stats.get('success', 0)}\\n"
                f"❌ Thất bại: {stats.get('failed', 0)}\\n"
                f"⏭️  Đã bỏ qua: {stats.get('skipped', 0)}\\n"
                f"📄 Tổng số trang: {stats.get('total_pages', 0)}\\n"
                f"📊 Tổng đã tải: {stats.get('success', 0) + stats.get('skipped', 0)} bài\\n\\n"
                f"📁 Thư mục: {output_path}"
            )
            messagebox.showinfo("Hoàn thành!", message)
'''

result = lines[:343] + [new_block + '\n'] + lines[378:]
f = open('src/ui/download_panel.py', 'w', encoding='utf-8', newline='')
f.writelines(result)
f.close()
print('Updated download_panel.py with paginated streaming')
