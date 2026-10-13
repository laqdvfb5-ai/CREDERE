"""Vẽ sơ đồ tiến độ Credere: phần nào xong, phần nào dở dang, phần nào chưa làm.

    py -3 progress_map.py        -> PROGRESS_MAP.html (mở bằng trình duyệt, rê chuột xem chi tiết)

Sửa danh sách GROUPS / MILESTONES bên dưới khi tiến độ thay đổi rồi chạy lại. Số đếm tự tính.
"""
import html
from pathlib import Path

DATE = "29/09/2026"
DONE, PART, TODO = "done", "part", "todo"
LABEL = {DONE: "Xong", PART: "Dở dang", TODO: "Chưa làm"}
ICON = {DONE: "✓", PART: "◐", TODO: "○"}

GROUPS = [
    ("Kế hoạch và hồ sơ", [
        (DONE, "Kế hoạch PLAN bản 3", "Kiến trúc, mốc M-1 đến M6, ưu tiên mã nguồn mở (PLAN.md, OSS_REVIEW.md)"),
        (DONE, "Đề xuất đề tài theo mẫu NAU", "Đã điền xong, 3 tháng (10–12/2026); bạn còn phải nộp"),
        (DONE, "Kế hoạch dữ liệu và dự toán", "DATA_PLAN.md, COST_ESTIMATE.md: 4,4–15 triệu cho đề tài"),
        (DONE, "Phân tích máy chủ tại trường", "LOCAL_HOSTING.md: chốt dùng API, không mua máy"),
        (DONE, "Bài trình bày AI Tuyển sinh", "14 slide (2 slide dự phòng), lời nói trong Notes, kịch bản 15 phút"),
        (TODO, "Gửi phiếu xin dữ liệu cho các phòng", "Phòng QLĐT, QLKH & HTQT, KH-TC theo DATA_PLAN.md"),
        (TODO, "Tài khoản API do Trường đứng tên", "Đang dùng cổng trung gian, lúc lỗi 401/502"),
    ]),
    ("Chọn model", [
        (DONE, "Đo 12 model, chốt cấu hình A", "Điều phối gpt-6-sol, thực thi gpt-6-luna (2 vòng đo)"),
        (PART, "M-1: đo ngữ cảnh dài", "Đã đo đến ~202 nghìn token, đạt 100% nhưng bài đo quá dễ nên chưa kết luận"),
        (TODO, "M-1b: bài đo phân biệt", "Văn bản thật qua Docling, mâu thuẫn không gắn nhãn, JSON có trích nguyên văn"),
    ]),
    ("Lõi điều phối (yêu cầu đề bài)", [
        (DONE, "FR1 lập kế hoạch, chạy song song", "Kế hoạch lưu trước khi giao việc; nhiệm vụ độc lập chạy cùng lúc"),
        (DONE, "FR2 hợp đồng dữ liệu", "Task, kết quả, nghiệm thu có kiểu (Pydantic); kế hoạch sai bị chặn"),
        (DONE, "FR4 nghiệm thu, sửa tối đa 2 lượt", "Kiểm nguồn bằng code, phản hồi cụ thể, dừng đúng giới hạn"),
        (DONE, "NFR2 chi phí và cấu hình model", "Ghi chi phí từng lời gọi, trần lời gọi và tiền, model theo vai trò"),
        (PART, "FR3 trạng thái, chịu lỗi", "Lỗi một nhiệm vụ không làm hỏng lượt chạy; chưa lưu checkpoint để chạy tiếp sau khi sập"),
        (PART, "NFR3 truy vết", "Nhật ký sự kiện, lịch sử từng lần thử, hồ sơ JSON; chưa lưu CSDL, chưa có màn hình xem lại"),
        (DONE, "NFR1 thêm tác tử không sửa lõi", "Mỗi AI con là một tệp domains/<lĩnh vực>.py cùng danh mục truy vấn; lõi không đổi"),
        (DONE, "Mô hình chủ – tớ (AI Tổng hợp)", "AI Tổng hợp giao việc cho AI con, AI con tự lập kế hoạch, nghiệm thu, báo cáo lại; ghép số liệu nhiều lĩnh vực"),
        (DONE, "Kiểm thử tự động", "132 kiểm thử chạy bằng model giả lập, không tốn tiền"),
    ]),
    ("Tác tử theo 6 lĩnh vực", [
        (DONE, "Tuyển sinh", "Trợ lý cho cán bộ Trung tâm Tuyển sinh: 70 văn bản công khai, có trang demo"),
        (PART, "Dữ liệu tuyển sinh (giai đoạn 2)", "Bản thử trên dữ liệu giả lập: 19 truy vấn đã duyệt, tổng do máy cộng; chưa nối dữ liệu thật"),
        (PART, "Đào tạo", "AI Đào tạo: 36 văn bản quy chế, chương trình, lịch thi đã kiểm chứng; dữ liệu học vụ giả lập, 18 truy vấn; chưa nối dữ liệu thật"),
        (PART, "Nghiên cứu khoa học", "Có khung và công cụ OpenAlex; chưa có dữ liệu thật"),
        (PART, "Hợp tác quốc tế", "Có khung dùng chung; chưa có dữ liệu thật"),
        (TODO, "Nhân sự", "Sau MVP; cần phân quyền và dữ liệu nội bộ"),
        (TODO, "Hành chính", "Sau MVP; cần phân quyền và dữ liệu nội bộ"),
        (DONE, "Phân tích (hỗ trợ)", "Model viết biểu thức, máy tính thực hiện bằng Decimal"),
        (PART, "Tìm kiếm OpenAlex (hỗ trợ)", "Code xong và có kiểm thử; chưa có key, chưa chạy thật"),
    ]),
    ("Dữ liệu và truy xuất", [
        (DONE, "Kho tuyển sinh công khai", "70 văn bản, 3.628 con số đã đối chiếu lại với bản gốc"),
        (DONE, "Bộ thử tuyển sinh", "30 câu văn bản: 30/30; 14 câu dữ liệu: 14/14; 10 tình huống cán bộ: 10/10, chấm tay (bản mã ngày 29/9)"),
        (PART, "Chọn nguồn liên quan", "BM25 bỏ dấu chạy được; chưa có embedding, reranker, pgvector"),
        (TODO, "Chuyển PDF, bản scan bằng Docling", "Hiện văn bản do agent trích và đối chiếu thủ công"),
        (DONE, "Bộ thử Đào tạo và AI Tổng hợp", "10 câu Đào tạo: 10/10; 4 câu liên lĩnh vực của Hiệu trưởng: 4/4; đáp án tính bằng SQL"),
        (TODO, "Dữ liệu thật Đào tạo, NCKH, HTQT", "Đào tạo đã có văn bản công khai; chờ phiếu xin CSDL học vụ và dữ liệu NCKH, HTQT"),
        (TODO, "Bộ nghiệm thu 60 tình huống", "Theo DATA_PLAN.md; không dùng để chỉnh prompt"),
    ]),
    ("Giao diện và nền tảng", [
        (DONE, "Trang demo web", "Tab theo vai trò (Tuyển sinh, Đào tạo, Hiệu trưởng), quy trình cả bên trong AI con, trang Cài đặt nhà cung cấp"),
        (DONE, "Nhiều nhà cung cấp AI", "Tự chuyển nhà khi lỗi, tạm ngắt nhà lỗi, chia tải; khóa chỉ trong .env"),
        (TODO, "Giao diện chính thức (React, assistant-ui)", "Mốc M0, M4"),
        (TODO, "Đăng nhập, phân quyền (Keycloak)", "Cần trước khi đưa tài liệu nội bộ vào"),
        (TODO, "API và lượt chạy bền (Aegra, PostgreSQL)", "Hủy, chạy tiếp sau khi sập, kết nối lại; mốc M0, M2"),
        (TODO, "Môi trường WSL2 và Docker", "Ổ C còn ít chỗ trống; mốc M-1"),
        (TODO, "Langfuse, DeepEval, promptfoo", "Theo dõi và nghiệm thu tự động; mốc M5"),
    ]),
]

MILESTONES = [
    ("M-1", "PoC khả thi", PART, "Đã chốt model, đo ngữ cảnh dài, có PoC Tuyển sinh; chưa WSL2/Docker, chưa thử Aegra, Docling"),
    ("M0", "Nền tảng", TODO, "Docker Compose, Keycloak, schema CSDL, khung giao diện"),
    ("M1", "Một luồng hoàn chỉnh", PART, "Luồng điều phối → tác tử → nghiệm thu → trả lời đã chạy với Tuyển sinh, Đào tạo và AI Tổng hợp; chưa chạy kịch bản NCKH"),
    ("M2", "Điều phối bền", TODO, "Checkpoint, hủy, chạy tiếp, kết nối lại"),
    ("M3", "Ba lĩnh vực", PART, "Đào tạo có văn bản công khai và dữ liệu giả lập; NCKH, HTQT và dữ liệu thật chưa có"),
    ("M4", "Web MVP", TODO, "Giao diện đủ vai trò, lịch sử, xuất file"),
    ("M5", "Nghiệm thu", TODO, "Bộ đánh giá cố định, kiểm tra quyền và prompt injection"),
    ("M6", "Sáu lĩnh vực", PART, "Tuyển sinh làm trước để trình diễn; Nhân sự, Hành chính chưa làm"),
]

NEXT = [
    "Trình bày mô hình chủ – tớ (AI Tuyển sinh, AI Đào tạo, AI Tổng hợp) với Ban Giám hiệu",
    "Gửi phiếu xin dữ liệu, đề nghị Trường đứng tên tài khoản API",
    "M-1 còn lại: WSL2 + Docker, thử Aegra và Docling, bài đo M-1b",
]


def main() -> None:
    items = [s for _, rows in GROUPS for s, *_ in rows]
    count = {k: items.count(k) for k in (DONE, PART, TODO)}
    total = len(items)
    e = html.escape

    def chip(status, name, note):
        return (f'<li class="chip {status}" title="{e(LABEL[status])}: {e(note)}"><span class="ic {status}" aria-hidden="true">{ICON[status]}</span>'
                f'<div><div class="nm">{e(name)} <span class="st">{LABEL[status]}</span></div><div class="nt">{e(note)}</div></div></li>')

    groups = "".join(
        f'<section class="grp"><h2>{e(title)}<span class="mini">{sum(s == DONE for s, *_ in rows)}/{len(rows)} xong</span></h2>'
        f'<ul>{"".join(chip(*r) for r in rows)}</ul></section>' for title, rows in GROUPS)
    miles = "".join(
        f'<div class="ms {st}" title="{e(LABEL[st])}: {e(note)}"><div class="mhead"><span class="ic {st}">{ICON[st]}</span><b>{e(code)}</b></div>'
        f'<div class="mname">{e(name)}</div><div class="mst">{LABEL[st]}</div></div>' for code, name, st, note in MILESTONES)
    bar = "".join(f'<div class="{k}" style="flex:{count[k]}" title="{LABEL[k]}: {count[k]}"></div>' for k in (DONE, PART, TODO) if count[k])
    nxt = "".join(f"<li>{e(x)}</li>" for x in NEXT)

    page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Credere — tiến độ {DATE}</title>
<style>
  :root {{ --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#6f6e69; --line:#e1e0d9;
          --good:#0ca30c; --warn:#fab219; --todo:#a3a29b; --good-ink:#006300; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--page); font-family:system-ui, -apple-system, "Segoe UI", sans-serif; color:var(--ink); }}
  .root {{ width:1440px; margin:0 auto; padding:28px 32px 30px; }}
  h1 {{ font-size:26px; margin:0 0 4px; }}
  .sub {{ color:var(--ink2); font-size:14px; margin:0 0 18px; }}
  .top {{ display:grid; grid-template-columns:repeat(3, 150px) 1fr 1.1fr; gap:12px; margin-bottom:14px; }}
  .tile {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:12px 14px; }}
  .tile .num {{ font-size:34px; font-weight:700; line-height:1.1; }}
  .tile .lbl {{ font-size:14px; color:var(--ink2); display:flex; align-items:center; gap:7px; margin-top:2px; }}
  .bar {{ display:flex; gap:2px; height:26px; margin:8px 0 6px; }}
  .bar div {{ border-radius:4px; }}
  .bar .done {{ background:var(--good); }} .bar .part {{ background:var(--warn); }} .bar .todo {{ background:#d9d8d2; }}
  .barnote {{ font-size:12.5px; color:var(--ink2); }}
  .next ol {{ margin:4px 0 0 18px; padding:0; font-size:13.5px; color:var(--ink2); line-height:1.5; }}
  .tile h3 {{ margin:0; font-size:14px; color:var(--ink2); font-weight:600; }}
  .ic {{ width:20px; height:20px; border-radius:50%; display:inline-grid; place-items:center; font-size:12px; font-weight:800; flex:none; line-height:1; }}
  .ic.done {{ background:var(--good); color:#fff; }}
  .ic.part {{ background:var(--warn); color:#3d2e00; }}
  .ic.todo {{ background:transparent; border:2px solid var(--todo); color:var(--todo); font-size:0; }}
  .legend {{ display:flex; gap:22px; font-size:13px; color:var(--ink2); background:var(--surface); border:1px solid var(--line); border-radius:10px;
            padding:9px 14px; margin-bottom:14px; align-items:center; }}
  .legend span {{ display:flex; align-items:center; gap:7px; }}
  .miles {{ display:grid; grid-template-columns:repeat(8, 1fr); gap:8px; margin-bottom:16px; }}
  .ms {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:9px 11px; border-top:4px solid #d9d8d2; }}
  .ms.done {{ border-top-color:var(--good); }} .ms.part {{ border-top-color:var(--warn); }}
  .mhead {{ display:flex; align-items:center; gap:7px; font-size:15px; }}
  .mname {{ font-size:13px; margin-top:3px; }}
  .mst {{ font-size:12px; color:var(--muted); }}
  .grid {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; }}
  .grp {{ background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:12px 14px 6px; }}
  .grp h2 {{ font-size:16px; margin:0 0 10px; display:flex; justify-content:space-between; align-items:baseline; }}
  .mini {{ font-size:12px; color:var(--muted); font-weight:500; }}
  .grp ul {{ list-style:none; margin:0; padding:0; }}
  .chip {{ display:flex; gap:10px; align-items:flex-start; padding:8px 10px; margin-bottom:8px; border:1px solid var(--line);
          border-left:5px solid #d9d8d2; border-radius:8px; background:#fff; }}
  .chip.done {{ border-left-color:var(--good); }} .chip.part {{ border-left-color:var(--warn); }}
  .chip.todo {{ background:transparent; border-style:dashed; border-left-style:solid; }}
  .chip .ic {{ margin-top:1px; }}
  .nm {{ font-size:14px; font-weight:600; line-height:1.3; }}
  .chip.todo .nm {{ color:var(--ink2); }}
  .st {{ font-size:11px; font-weight:600; color:var(--muted); margin-left:4px; white-space:nowrap; }}
  .chip.done .st {{ color:var(--good-ink); }}
  .nt {{ font-size:12.5px; color:var(--ink2); line-height:1.35; margin-top:2px; }}
  .foot {{ font-size:12px; color:var(--muted); margin-top:12px; }}
</style></head>
<body><div class="root">
<h1>Credere: chỗ nào đã làm, chỗ nào chưa</h1>
<p class="sub">Cập nhật {DATE}. Đối chiếu với PLAN.md bản 3 và yêu cầu FR1–FR4, NFR1–NFR3 của đề bài. Rê chuột lên từng ô để xem chi tiết.</p>
<div class="top">
  <div class="tile"><div class="num">{count[DONE]}</div><div class="lbl"><span class="ic done">✓</span>Xong</div></div>
  <div class="tile"><div class="num">{count[PART]}</div><div class="lbl"><span class="ic part">◐</span>Dở dang</div></div>
  <div class="tile"><div class="num">{count[TODO]}</div><div class="lbl"><span class="ic todo">○</span>Chưa làm</div></div>
  <div class="tile"><h3>Tỷ lệ trên {total} hạng mục</h3><div class="bar">{bar}</div>
    <div class="barnote">Xong {count[DONE]} · Dở dang {count[PART]} · Chưa làm {count[TODO]}. Phần đã xong tập trung ở kế hoạch, lõi điều phối, mô hình chủ – tớ và AI Tuyển sinh; phần nền tảng (đăng nhập, CSDL, Docker) chưa bắt đầu.</div></div>
  <div class="tile next"><h3>Việc tiếp theo</h3><ol>{nxt}</ol></div>
</div>
<div class="legend"><b>Chú giải</b><span><i class="ic done">✓</i>Xong: chạy được, có kiểm chứng</span>
  <span><i class="ic part">◐</i>Dở dang: có một phần, còn thiếu phần ghi trong ô</span><span><i class="ic todo">○</i>Chưa làm</span></div>
<div class="miles">{miles}</div>
<div class="grid">{groups}</div>
<div class="foot">Tạo bằng progress_map.py. Số đếm tính tự động từ danh sách hạng mục.</div>
</div></body></html>"""
    out = Path(__file__).with_name("PROGRESS_MAP.html")
    out.write_text(page, encoding="utf-8")
    print(f"{out} — xong {count[DONE]}, dở dang {count[PART]}, chưa làm {count[TODO]} / {total}")


if __name__ == "__main__":
    main()
