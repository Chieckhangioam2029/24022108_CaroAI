# Caro AI — Minimax & Alpha-Beta Pruning

Chương trình chơi cờ Caro trên bàn **15×15**, luật thắng **4 ô liên tiếp**.
AI sử dụng thuật toán **Minimax** và AI sử dụng thuật toán Minimax và Alpha-Beta Pruning kết hợp hàm đánh giá trạng thái để lựa chọn nước đi.
Giao diện đồ hoạ Pygame, hỗ trợ 3 chế độ: Người vs Người, Người vs AI, AI vs AI.

---

## Thông tin sinh viên

| Trường | Trường đại học Công Nghệ - ĐHQGHN |
| Họ tên | Lê Minh Dương |
| MSSV | 24022108 |
| Môn học | INT3401_1 |

---

## Yêu cầu môi trường

- **Python** 3.8 trở lên
- **Hệ điều hành**: Windows / macOS / Linux
- Thư viện cần cài: `numpy`, `pygame`

---

## Cài đặt

```bash
# 1. Clone hoặc giải nén project
# 2. Mở terminal tại thư mục gốc của project

# 3. Cài thư viện
pip install -r requirements.txt
```

Nội dung `requirements.txt`:

```
numpy
pygame
```

---

## Cách chạy

### Chạy giao diện Pygame (khuyên dùng)

```bash
python run_game.py
```

hoặc:

```bash
python -m source_code.ui.pygame_ui
```

Sau khi chạy, cửa sổ menu sẽ hiện ra cho phép chọn:

| Tuỳ chọn | Mô tả |
|---|---|
| **Game Mode** | `Human vs Human` · `Human vs AI` · `AI vs AI` |
| **Algorithm** | `Minimax` hoặc `Alpha-Beta` (chọn riêng cho từng AI trong chế độ AI vs AI) |
| **Depth** | Độ sâu tìm kiếm từ 1 đến 4 (mặc định: 3) |
| **First Player** | Chọn X hoặc O đi trước |

Nhấn **START** để bắt đầu ván cờ.

### Chạy chế độ console (terminal)

```bash
python -m source_code.main
```

Chương trình sẽ hỏi lần lượt:
1. Chọn thuật toán (1 = Minimax, 2 = Alpha-Beta)
2. Nhập độ sâu (1–4, mặc định 3)

Chế độ này chỉ hỗ trợ **Người (X) vs AI (O)**, bàn cờ hiển thị dạng text trong terminal.

### Chạy benchmark

```bash
python -m source_code.benchmark.benchmark
```

So sánh hiệu năng Minimax vs Alpha-Beta trên 5 trạng thái bàn cờ mẫu ở độ sâu 1–3.
Kết quả in ra terminal và xuất file CSV tại `source_code/logs/results.csv`.

### Chạy file .exe (không cần Python)

Nếu đã build sẵn, chạy trực tiếp:

```
dist\CaroAI.exe
```

---

## Cấu trúc thư mục

```
MSSV_HoTen_CaroAI_DeSo/
├── run_game.py              # Entry point chính (mở giao diện Pygame)
├── requirements.txt         # Danh sách thư viện
├── CaroAI.spec              # Cấu hình build .exe (PyInstaller)
├── test_perf.py             # Script test hiệu năng nhanh
│
├── source_code/
│   ├── config.py            # Hằng số cấu hình (BOARD_SIZE, WIN_LENGTH, MAX_DEPTH)
│   ├── main.py              # Entry point console (Người vs AI qua terminal)
│   │
│   ├── ai/                  # Thuật toán AI
│   │   ├── ai_player.py     # Wrapper gọi minimax / alphabeta
│   │   ├── minimax.py       # Thuật toán Minimax
│   │   ├── alphabeta.py     # Thuật toán Alpha-Beta Pruning
│   │   ├── evaluation.py    # Hàm đánh giá heuristic
│   │   └── move_generator.py# Sinh nước đi ứng viên (lọc ô gần quân cờ)
│   │
│   ├── game/                # Logic trò chơi
│   │   ├── board.py         # Cấu trúc bàn cờ
│   │   ├── rules.py         # Kiểm tra thắng/thua/hoà
│   │   └── game_manager.py  # Điều phối luồng game
│   │
│   ├── benchmark/           # Hệ thống benchmark
│   │   ├── benchmark.py     # Script chạy benchmark
│   │   └── test_states.py   # Các trạng thái bàn cờ mẫu
│   │
│   ├── ui/                  # Giao diện
│   │   ├── pygame_ui.py     # Giao diện đồ hoạ Pygame
│   │   └── console_ui.py    # (Chưa triển khai)
│   │
│   └── logs/                # Kết quả benchmark (CSV)
│
├── screenshots/             # Ảnh chụp màn hình
└── dist/
    └── CaroAI.exe           # File thực thi đã build
```

---

## Cấu hình mặc định

Các hằng số trong `source_code/config.py`:

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `BOARD_SIZE` | 15 | Kích thước bàn cờ 15×15 |
| `WIN_LENGTH` | 4 | Số ô liên tiếp để thắng |
| `MAX_DEPTH` | 3 | Độ sâu tìm kiếm mặc định |
| `TIMEOUT` | 5.0 | Thời gian giới hạn (giây) |

---

## Build file .exe

```bash
pip install pyinstaller
pyinstaller CaroAI.spec
```

File đầu ra: `dist/CaroAI.exe`

---

## Lưu ý

- **Độ sâu 4** có thể chạy chậm ở giai đoạn giữa ván (midgame) do số trạng thái lớn. Khuyên dùng độ sâu 2–3 cho trải nghiệm mượt mà.
- Nếu gặp lỗi `ModuleNotFoundError`, đảm bảo đang chạy lệnh từ **thư mục gốc** của project (thư mục chứa `run_game.py`).
- Nếu gặp lỗi `No module named 'pygame'`, chạy `pip install pygame` để cài thư viện.
## Tính năng chính

- Chơi Người vs Người
- Chơi Người vs AI
- Chơi AI vs AI
- Thuật toán Minimax
- Thuật toán Alpha-Beta Pruning
- Giới hạn độ sâu tìm kiếm
- Hàm đánh giá trạng thái heuristic
- Benchmark số trạng thái và thời gian chạy
- Giao diện Pygame
Trong quá trình chơi, chương trình hiển thị:
- nước đi AI chọn
- giá trị đánh giá
- số trạng thái đã xét
- thời gian chạy