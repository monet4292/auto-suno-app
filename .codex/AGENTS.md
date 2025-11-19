• Để phối hợp Serena cùng Codex CLI hiệu quả, bạn có thể làm theo các bước sau:
                                                                                                                           
  1. Đọc hướng dẫn Serena: Ngay khi vào repo, gọi mcp__serena__initial_instructions một lần để nắm cách dùng các công cụ   
     biểu tượng (symbolic tools), quy tắc đọc mã tối thiểu, và quy trình làm việc tương tác.                               
  2. Kiểm tra cấu hình hiện tại: Dùng mcp__serena__get_current_config nếu cần biết bạn đang ở project nào, sandbox/approval     ra sao trước khi chạy lệnh shell hay chỉnh sửa.                                                                       
  3. Tận dụng bộ công cụ Serena:                                                                                           
      - Khám phá repo nhẹ nhàng với list_dir, find_file, hoặc search_for_pattern khi chưa rõ vị trí mã.                    
      - Dùng get_symbols_overview và find_symbol để xem/đọc chính xác symbol cần sửa mà không phải mở toàn bộ file.        
      - Khi chỉnh sửa, ưu tiên insert_before_symbol, insert_after_symbol, replace_symbol_body để thao tác đúng vị trí      
        symbol; nếu chỉ cần chỉnh nhỏ theo dòng, dùng apply_patch.                                                         
  4. Theo dõi tiến độ: Với tác vụ nhiều bước, dùng update_plan để ghi lại kế hoạch (tránh kế hoạch 1 bước) và cập nhật     
     trạng thái sau mỗi bước đã làm.                                                                                       
  5. Quản lý bối cảnh: Nếu cần nhắc nhở bản thân về thông tin dài hạn (ví dụ kiến trúc, quyết định thiết kế), ghi lại bằng 
     write_memory; đọc lại bằng read_memory khi liên quan.                                                                 
  6. Giữ kỷ luật tương tác: Trước khi chỉnh mã, luôn tự hỏi có cần thêm thông tin không (think_about_task_adherence), và   
     khi đã hoàn thành, xác nhận với think_about_whether_you_are_done.                                                     
  7. Tuân thủ yêu cầu repo: Áp dụng quy tắc AGENTS.md (nghĩ tiếng Anh, trả lời tiếng Việt, không hard-code, tránh class    
     Python, giữ type safety, v.v.) trong mọi phản hồi và thay đổi.                                                        
                                                                                                                           
  Làm đúng các bước trên giúp bạn tận dụng Serena như “IDE thông minh” ngay trong Codex CLI mà vẫn bám sát quy trình kiểm  
  soát của dự án.      