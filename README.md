# Credere

Trợ lý AI đa tác tử cho trường đại học. Mục tiêu toàn dự án gồm Tuyển sinh, Đào tạo, Nghiên cứu khoa học, Hợp tác quốc tế, Nhân sự và Hành chính; AI Tổng hợp phối hợp các lĩnh vực để lập báo cáo có căn cứ.

Bản code hiện tại có AI Tuyển sinh, AI Đào tạo và AI Tổng hợp, dùng FastAPI, LangGraph, Pydantic và SQLite chỉ đọc. Đây là bản thử nghiệm; chưa có phân quyền nghiệp vụ theo người dùng, checkpoint/resume bền hoặc nghiệm thu production. Hai CSDL nghiệp vụ của bản demo là dữ liệu giả lập.

## Cấu trúc

- `backend/app/`: API, giao diện, điều phối, provider, công cụ và AI lĩnh vực.
- `backend/tests/`: kiểm thử cơ chế, dữ liệu và cổng mật khẩu cài đặt.
- `backend/scripts/`: tạo dữ liệu giả lập, nhập nguồn và đánh giá.
- `evals/`: mã và kết quả thử nghiệm model đã lưu.
- `deploy/`: cấu hình triển khai tham khảo, cần đối chiếu môi trường trước khi áp dụng.
- `presentation/`: slide, lời nói, nguồn và script dựng bài trình bày.
- `production_plan/`: backlog và mẫu hợp đồng dữ liệu/ma trận quyền.

## Cài đặt

Python từ 3.12. Tạo môi trường và cài dependencies:

```bash
git clone https://github.com/laqdvfb5-ai/CREDERE.git
cd CREDERE/backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[web,dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

Linux/macOS:

```bash
.venv/bin/python -m pip install -e '.[web,dev]'
.venv/bin/python -m pytest -q
```

Các test dùng model/dữ liệu giả lập, không cần khóa API thật. Snapshot code đã được kiểm tra ngày 13/10/2026: 159 test đạt.

## Cấu hình và dữ liệu

Runtime được đặt **ngoài repository**:

| Biến | Mặc định | Nội dung |
| --- | --- | --- |
| `CREDERE_HOME` | `~/.credere` | `.env`, `providers.json`, `settings-auth.json`, `runs/` |
| `CREDERE_DATA` | `~/credere-data` | Kho tài liệu và CSDL nghiệp vụ |

Tham khảo `backend/.env.example` và `backend/providers.example.json`, chép vào `CREDERE_HOME` rồi cấu hình riêng trên máy chạy. Tệp `.env` được ứng dụng đọc tại `CREDERE_HOME`, không tự đọc ở thư mục `backend`.

Kho tài liệu để dựng đủ ba AI có cấu trúc sau:

```text
credere-data/
  03_xu-ly/
    tuyen_sinh/
      sources.json
      demo_questions.json
      gia_lap/tuyen_sinh_2026_gia_lap.sqlite
      gia_lap/demo_questions.json
    dao_tao/
      sources.json
      demo_questions.json
      gia_lap/hoc_vu_gia_lap.sqlite
      gia_lap/demo_questions.json
    tong_hop/demo_questions.json
```

`sources.json` là danh sách nguồn có `source_id`, `title`, `text`, URL và mức truy cập. Script `build_tuyen_sinh.py` gộp nguồn đã xử lý; các script `make_gia_lap*.py` tạo CSDL mẫu khi có đủ đầu vào. Dữ liệu runtime đầy đủ không được đóng kèm Git; clone repository không tự tạo kho nghiệp vụ. Xem `DATA_PLAN.md` và kế hoạch vận hành để chuẩn bị dữ liệu được phép dùng.

Chạy web sau khi có kho nguồn và cấu hình:

```bash
python -m app.web --host 127.0.0.1 --port 8000
```

`--no-data` chỉ bỏ kết nối SQLite, vẫn cần nguồn văn bản. Giao diện gửi câu hỏi mới sẽ gọi dịch vụ AI và có thể phát sinh phí.

### Mật khẩu trang cài đặt

`/cai-dat` sử dụng mật khẩu băm trong `CREDERE_HOME/settings-auth.json`. Tạo trên máy chạy, từ thư mục `backend`, bằng Python của môi trường vừa cài:

```python
from getpass import getpass
import json
from app.config import CREDERE_HOME
from app.settings_auth import hash_password

CREDERE_HOME.mkdir(parents=True, exist_ok=True)
path = CREDERE_HOME / "settings-auth.json"
with path.open("x", encoding="utf-8") as output:
    json.dump(hash_password(getpass("Mat khau cai dat: ")), output)
```

Tệp có sẵn sẽ không bị ghi đè. Chỉ cài đặt được bảo vệ bằng mật khẩu; đây chưa phải đăng nhập/phân quyền dữ liệu cho toàn ứng dụng. Quy tắc localhost ở API quản trị cũng cần được thiết kế đúng khi chạy sau reverse proxy.

## Tài liệu hiện hành

- [Kế hoạch đưa vào vận hành thật](KE_HOACH_VAN_HANH_THAT.md): mốc triển khai, đầu vào và tiêu chí nghiệm thu.
- [Phương án bảo mật](presentation/PHUONG_AN_BAO_MAT_CREDERE.md): thiết kế mục tiêu, phân biệt với code đã có.
- [Kế hoạch tối ưu tốc độ](LATENCY_OPTIMIZATION_PLAN.md): hướng thử nghiệm, chưa phải mọi tối ưu đã triển khai.
- [Nội dung bài trình bày 15 phút](presentation/NOI_DUNG_CHI_TIET_15P.md).

`PLAN.md`, sơ đồ, giá tham khảo và các bản trong `presentation/archive/` giữ để đối chiếu lịch sử; không lấy ngày của chúng làm hiện trạng triển khai. Cấu hình `deploy/` cũng là mẫu, không phải bản sao được đảm bảo khớp VPS đang chạy.

Không đưa mật khẩu VPS, khóa API, tệp cấu hình thực, hồ sơ nội bộ hoặc log người dùng vào commit. Các thư viện/asset bên thứ ba giữ thông tin giấy phép đi kèm, gồm `backend/app/static/vendor/`.
