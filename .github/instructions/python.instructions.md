---
applyTo: '**/*.py'
---

Mục tiêu: Python ≥ 3.10.

Dùng generic dựng sẵn: list[str], dict[str, int], set[str], tuple[int, ...].

typing chỉ dùng cho Optional, Literal, TypedDict, Protocol, Iterable, v.v.

Không tạo side-effect khi import: không I/O, không network, không khởi tạo thread/task.

Mỗi hàm có docstring ngắn gọn theo PEP 257.

Tên hàm, biến rõ nghĩa; có type hints đầy đủ.

Hàm dài tách nhỏ thành các hàm đơn nhiệm.

Dùng logging cho chẩn đoán. Không dùng print() trong thư viện.

Bắt lỗi cụ thể. Tránh except Exception: và bare except.

Ưu tiên pathlib cho đường dẫn, dataclasses cho cấu trúc dữ liệu.

Dùng from __future__ import annotations khi có forward reference.

Nếu dùng thư viện ngoài, ghi chú ngay tại chỗ import về mục đích sử dụng.

General Instructions

Ưu tiên dễ đọc. Tối ưu hiệu năng chỉ khi có số liệu.

Với thuật toán: thêm bình luận ngắn về ý tưởng, độ phức tạp, trade-off.

Ghi chú quyết định thiết kế ngay cạnh đoạn code liên quan.

Xử lý edge case: input rỗng, kiểu sai, biên, dữ liệu lớn.

API/public surface ổn định; tránh phá vỡ tương thích không cần thiết.

Code Style and Formatting

Tuân theo PEP 8.

Thụt lề 4 khoảng trắng. Dòng ≤ 79 ký tự.

Docstring đặt ngay sau def hoặc class.

Thứ tự import: stdlib → third‑party → local. Một import mỗi dòng.

Quy ước tên: snake_case (hàm/biến), PascalCase (class), UPPER_CASE (hằng).

Dùng dấu ngoặc để bọc dòng dài, không dùng \ tiếp dòng.