"""Tạo bộ slide trình bày AI Tuyển sinh cho Ban Giám hiệu và lãnh đạo các đơn vị (khoảng 15 phút).

    C:/Users/laqdv/.credere/venv/Scripts/python.exe build_deck.py

Số liệu kết quả thử nghiệm đọc từ deck_numbers.json (cùng thư mục) nếu có; thiếu thì slide ghi "đang đo".
Lời nói của người trình bày nằm trong phần ghi chú (Notes) của từng slide.
"""
import json
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).parent
OUT = HERE / "AI_Tuyen_sinh_trinh_bay.pptx"
FONT = "Arial"
BLUE, DARK, INK, MUTED = RGBColor(0x0B, 0x5C, 0xAD), RGBColor(0x08, 0x3B, 0x73), RGBColor(0x1C, 0x24, 0x30), RGBColor(0x5D, 0x6B, 0x7C)
SOFT, LINE, WHITE = RGBColor(0xE8, 0xF1, 0xFB), RGBColor(0xD5, 0xDD, 0xE6), RGBColor(0xFF, 0xFF, 0xFF)
GREEN, GREEN_SOFT, ORANGE, ORANGE_SOFT = RGBColor(0x1A, 0x7F, 0x37), RGBColor(0xE3, 0xF2, 0xE8), RGBColor(0xB7, 0x6E, 0x00), RGBColor(0xFF, 0xF4, 0xE0)
PURPLE_SOFT, PURPLE = RGBColor(0xF1, 0xEB, 0xFF), RGBColor(0x5B, 0x3E, 0xA8)
FOOTER = "Credere · AI Tuyển sinh · Trường Đại học Nghệ An"

N = json.loads((HERE / "deck_numbers.json").read_text(encoding="utf-8")) if (HERE / "deck_numbers.json").exists() else {}

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, paras, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.1, after=0):
    """paras: chuỗi, hoặc danh sách đoạn; mỗi đoạn là chuỗi hoặc danh sách (chữ, {size, bold, color})."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap, tf.vertical_anchor = True, anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    for i, para in enumerate([paras] if isinstance(paras, str) else paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing, p.space_after = align, spacing, Pt(after)
        for run_text, style in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = run_text
            f = r.font
            f.name, f.size = FONT, Pt(style.get("size", size))
            f.bold = style.get("bold", bold)
            f.color.rgb = style.get("color", color)
    return box


def box(slide, x, y, w, h, fill=SOFT, line=None, radius=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line:
        s.line.color.rgb, s.line.width = line, Pt(1.25)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if radius:
        s.adjustments[0] = 0.08
    return s


def arrow(slide, x1, y1, x2, y2, color=MUTED):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb, c.line.width = color, Pt(2.5)
    tail = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"))
    tail.set("type", "triangle")
    return c


def slide(title, notes, number=True):
    s = prs.slides.add_slide(BLANK)
    if title:
        box(s, 0, 0, 13.333, 0.12, BLUE, radius=False)
        text(s, 0.6, 0.35, 12.1, 0.9, title, size=30, bold=True, color=DARK)
    if number:
        text(s, 0.6, 7.0, 9, 0.35, FOOTER, size=11, color=MUTED)
        text(s, 11.9, 7.0, 0.85, 0.35, str(len(prs.slides)), size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = notes
    return s


def card(s, x, y, w, h, heading, body, fill=SOFT, head_color=DARK, size=17):
    box(s, x, y, w, h, fill)
    text(s, x + 0.25, y + 0.2, w - 0.5, 0.6, heading, size=22, bold=True, color=head_color)
    text(s, x + 0.25, y + 0.95, w - 0.5, h - 1.1, body, size=size, color=INK, spacing=1.15, after=10)


def stat(s, x, y, w, h, value, label, fill=SOFT, color=DARK):
    box(s, x, y, w, h, fill)
    text(s, x + 0.2, y + 0.15, w - 0.4, 0.95, value, size=36, bold=True, color=color)
    text(s, x + 0.2, y + 1.05, w - 0.4, h - 1.15, label, size=15, color=INK, spacing=1.1)


# ---------- 1. Tiêu đề ----------
s = slide(None, number=False, notes=(
    "Kính thưa thầy Hiệu trưởng, quý thầy cô lãnh đạo các khoa, phòng. Em xin trình bày đề tài AI Tuyển sinh: một trợ lý trí tuệ nhân tạo "
    "cho cán bộ Trung tâm Tuyển sinh và Truyền thông. Mục tiêu là trợ lý nắm được văn bản và số liệu tuyển sinh mà cán bộ Trung tâm làm việc hằng ngày, "
    "trả lời có dẫn nguồn. Đây là phần đầu tiên của hệ thống Credere mà nhóm em đang xây dựng "
    "cho Nhà trường. Bài trình bày khoảng 15 phút, trong đó có phần chạy thử trực tiếp."))
box(s, 0, 0, 13.333, 7.5, DARK, radius=False)
box(s, 0.9, 1.55, 0.14, 2.35, WHITE, radius=False)
text(s, 1.3, 1.35, 11, 1.2, "AI Tuyển sinh", size=54, bold=True, color=WHITE)
text(s, 1.3, 2.5, 11, 1.4, ["Trợ lý AI cho cán bộ Trung tâm Tuyển sinh và Truyền thông:", "nắm văn bản và số liệu tuyển sinh, trả lời có dẫn nguồn"],
     size=26, color=RGBColor(0xDC, 0xE8, 0xF7))
text(s, 1.3, 4.35, 11, 0.6, "Bước đầu của hệ thống AI đa tác tử Credere cho Trường Đại học Nghệ An", size=20, color=WHITE)
text(s, 1.3, 5.45, 11, 1.2, ["Đề tài nghiên cứu khoa học sinh viên năm học 2026–2027",
                             "Sinh viên thực hiện: ……………………   ·   Giáo viên hướng dẫn: ……………………   ·   …/…/2026"],
     size=16, color=RGBColor(0xB8, 0xCC, 0xE4))

# ---------- 2. Vấn đề ----------
s = slide("Tuyển sinh: nhiều văn bản, nhiều số liệu, dồn vào vài tuần", notes=(
    "Khi thu thập dữ liệu, nhóm em đếm được 70 tài liệu công khai liên quan tới tuyển sinh: đề án, thông báo, điểm chuẩn ba năm, "
    "học phí, học bổng, thủ tục, cùng quy chế và lịch tuyển sinh của Bộ. Chúng nằm ở nhiều trang, nhiều định dạng, và cập nhật lẫn nhau: "
    "chỉ tiêu công bố tháng 2 được cập nhật bằng thông báo tháng 6 và tháng 7, nên rất dễ dùng nhầm số cũ. "
    "Nhưng văn bản chỉ là một nửa. Nửa còn lại là số liệu của chính Trung tâm, dồn vào tháng 7 đến tháng 9: tải dữ liệu nguyện vọng, "
    "lọc ảo sáu vòng trong năm ngày, công bố điểm chuẩn, theo dõi xác nhận nhập học, rồi tính chỉ tiêu còn lại cho các đợt bổ sung. "
    "Cả nước năm 2025 có khoảng 19% thí sinh trúng tuyển không xác nhận nhập học, và 16 trường sai sót khi công bố kết quả vì dữ liệu đầu vào "
    "hoặc hiểu sai quy chế. Đó là những việc mà một trợ lý nắm được cả văn bản lẫn số liệu có thể đỡ cho cán bộ."))
stat(s, 0.6, 1.5, 3.85, 1.65, "70", "văn bản tuyển sinh công khai, cập nhật lẫn nhau trong năm")
stat(s, 0.6, 3.3, 3.85, 1.65, "6 vòng", "lọc ảo trong 5 ngày (4–9/8/2026), mỗi vòng tính lại điểm chuẩn")
stat(s, 0.6, 5.1, 3.85, 1.65, "19%", "trúng tuyển nhưng không xác nhận nhập học (cả nước 2025)")
text(s, 4.95, 1.55, 7.8, 0.5, "Hai loại việc của cán bộ Trung tâm", size=21, bold=True, color=DARK)
text(s, 4.95, 2.2, 7.8, 4.6, [
    [("Văn bản: ", {"bold": True}), ("tra cứu, soạn tin trả lời phụ huynh, bài đăng, thông báo; đối chiếu văn bản cập nhật (chỉ tiêu tháng 2 được sửa bằng thông báo tháng 6, tháng 7).", {})],
    [("Số liệu: ", {"bold": True}), ("bao nhiêu nguyện vọng vào từng ngành; điểm chuẩn bao nhiêu thì đủ chỉ tiêu; ai chưa xác nhận nhập học; ngành nào còn thiếu chỉ tiêu cho đợt bổ sung.", {})],
    [("Báo cáo: ", {"bold": True}), ("tổng hợp cho Hội đồng tuyển sinh, Ban Giám hiệu, Bộ; số liệu phải khớp giữa nhiều hệ thống.", {})],
    [("Rủi ro sai sót: ", {"bold": True}), ("năm 2025, 16 trường sai sót khi công bố kết quả, ảnh hưởng gần 1.000 thí sinh.", {})],
], size=18, spacing=1.12, after=12)

# ---------- 3. Giải pháp ----------
s = slide("Giải pháp: trợ lý AI cho cán bộ tuyển sinh", notes=(
    "Người dùng của AI Tuyển sinh là cán bộ Trung tâm Tuyển sinh và Truyền thông; thí sinh không hỏi AI trực tiếp. Ba cam kết: "
    "một, làm nhanh các việc lặp lại: tra cứu, soạn tin trả lời phụ huynh, câu hỏi thường gặp, bản nháp thông báo, bảng số liệu, tóm tắt cho "
    "Ban Giám hiệu. Hai, mọi con số đều kèm nguồn: văn bản thì bấm vào mở văn bản gốc, số liệu thì do máy tính từ dữ liệu và ghi thời điểm dữ liệu. "
    "Ba, cán bộ là người quyết định: không có căn cứ thì AI nói rõ, không đoán; cán bộ đọc, sửa rồi mới gửi đi; dữ liệu cá nhân của thí sinh "
    "không ra khỏi Trường. Khác với tự hỏi ChatGPT: ChatGPT không có tài liệu, số liệu của Trường và có thể bịa số."))
card(s, 0.6, 1.6, 3.9, 4.4, "Làm nhanh việc lặp lại",
     ["Tra cứu số liệu, lịch, thủ tục.", "Soạn tin trả lời phụ huynh, câu hỏi thường gặp, bản nháp thông báo.", "Lập bảng, tóm tắt cho Ban Giám hiệu."], size=18)
card(s, 4.72, 1.6, 3.9, 4.4, "Mọi con số có nguồn",
     ["Văn bản: mã nguồn bấm vào mở văn bản gốc; ưu tiên văn bản mới nhất.", "Số liệu: máy tính từ dữ liệu, ghi thời điểm dữ liệu.",
      "AI không tự nhẩm số."],
     fill=GREEN_SOFT, head_color=GREEN, size=18)
card(s, 8.84, 1.6, 3.9, 4.4, "Cán bộ quyết định",
     ["Không có căn cứ thì nói rõ, không đoán.", "Cán bộ đọc, sửa rồi mới gửi cho thí sinh.", "Dữ liệu cá nhân của thí sinh không ra khỏi Trường."],
     fill=ORANGE_SOFT, head_color=ORANGE, size=18)
text(s, 0.6, 6.25, 12.1, 0.5, "Thí sinh không hỏi AI trực tiếp: AI giúp cán bộ trả lời nhanh hơn và đúng văn bản hơn.", size=17, color=MUTED)

# ---------- 4. Cách hoạt động ----------
s = slide("Bên trong: các “nhân viên AI” làm việc như một phòng ban", notes=(
    "Bên trong không phải một chatbot mà là một nhóm tác tử AI, mỗi tác tử như một nhân viên có việc riêng. Tác tử điều phối nhận yêu cầu của cán bộ, "
    "lập kế hoạch và giao việc. Tác tử Tuyển sinh tìm trong 70 tài liệu, trích đúng số liệu và ghi nguồn. Tác tử Dữ liệu là phần của giai đoạn 2: "
    "nó không tự viết câu lệnh mà chỉ chọn trong danh mục truy vấn đã duyệt, cơ sở dữ liệu đếm và trả số tổng hợp; danh sách thí sinh đi thẳng "
    "tới màn hình cán bộ, không qua AI. Khi cần tính, tác tử Phân tích viết phép tính và máy tính thực hiện, không để AI tính nhẩm. "
    "Sau đó tác tử điều phối nghiệm thu: kiểm tra số liệu có đúng nguồn không; chưa đạt thì trả lại, yêu cầu làm lại, tối đa hai lần. "
    "Cuối cùng mới tổng hợp câu trả lời. Phần mềm còn kiểm tra tự động: mã nguồn nào không có thật thì bị loại ngay."))
Y = 2.35
box(s, 0.45, Y, 2.0, 1.5, RGBColor(0xEE, 0xF1, 0xF5))
text(s, 0.55, Y + 0.2, 1.8, 1.1, ["Yêu cầu của", "cán bộ"], size=18, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
box(s, 2.95, Y - 0.35, 2.6, 2.2, SOFT, BLUE)
text(s, 3.05, Y - 0.25, 2.4, 2.0, [[("Tác tử điều phối", {"bold": True, "color": DARK, "size": 19})], "", "Hiểu câu hỏi,", "lập kế hoạch,", "giao việc"],
     size=16, align=PP_ALIGN.CENTER)
TEAL, TEAL_SOFT = RGBColor(0x0F, 0x76, 0x6E), RGBColor(0xE0, 0xF2, 0xF0)
workers_ = [("Tác tử Tuyển sinh", "đọc 70 văn bản,", "trích số liệu, ghi nguồn", GREEN, GREEN_SOFT),
            ("Tác tử Dữ liệu", "truy vấn đã duyệt trên", "dữ liệu Trung tâm · giai đoạn 2", TEAL, TEAL_SOFT),
            ("Tác tử Phân tích", "viết phép tính,", "máy tính thực hiện", PURPLE, PURPLE_SOFT)]
for i, (name, l1, l2, color, fill) in enumerate(workers_):
    y = 1.2 + i * 1.5
    box(s, 6.1, y, 2.9, 1.3, fill, color)
    text(s, 6.15, y + 0.08, 2.8, 1.15, [[(name, {"bold": True, "color": color, "size": 18})], l1, l2], size=14, align=PP_ALIGN.CENTER)
    arrow(s, 5.55, Y + 0.25 + i * 0.5, 6.1, y + 0.65)
    arrow(s, 9.0, y + 0.65, 9.55, Y + 0.25 + i * 0.5)
box(s, 9.55, Y - 0.35, 2.3, 2.2, SOFT, BLUE)
text(s, 9.65, Y - 0.25, 2.1, 2.0, [[("Nghiệm thu", {"bold": True, "color": DARK, "size": 19})], "", "Kiểm nguồn,", "kiểm số liệu;", "chưa đạt: làm lại"],
     size=16, align=PP_ALIGN.CENTER)
box(s, 12.0, Y, 1.1, 1.5, GREEN)
text(s, 12.02, Y + 0.1, 1.06, 1.3, ["Trả lời", "có", "nguồn"], size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
arrow(s, 2.45, Y + 0.75, 2.95, Y + 0.75)
arrow(s, 11.85, Y + 0.75, 12.0, Y + 0.75)
c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(10.7), Inches(Y + 1.85), Inches(10.7), Inches(5.95))
c.line.color.rgb, c.line.width, c.line.dash_style = ORANGE, Pt(2), 4
text(s, 6.1, 5.75, 4.55, 0.45, "Chưa đạt → trả lại, sửa tối đa 2 lần", size=15, color=ORANGE, bold=True, align=PP_ALIGN.RIGHT)
text(s, 0.6, 6.3, 12.1, 0.6, [[("Có kế hoạch, có phân công, có kiểm tra chéo. ", {"bold": True, "color": DARK}),
                              ("Mã nguồn không có thật bị loại ngay; danh sách thí sinh đi thẳng tới màn hình cán bộ, không qua AI.", {"color": MUTED})]], size=16)

# ---------- 5. Trình diễn ----------
s = slide("Trình diễn trực tiếp", notes=(
    "Bây giờ em xin chạy thử trực tiếp, em đóng vai cán bộ Trung tâm Tuyển sinh. [Chuyển sang trình duyệt.] Quý thầy cô chú ý khung bên phải: đó là các tác tử "
    "đang làm việc, kế hoạch hiện ra trước, sau đó từng bước giao việc và nghiệm thu. Mỗi câu mất khoảng một đến hai phút vì các tác tử làm "
    "nhiều bước và kiểm tra chéo. Trong lúc chờ, em giải thích từng bước. Nếu mạng hoặc dịch vụ AI gặp sự cố, trang sẽ phát lại bản chạy "
    "thật đã ghi trước của đúng câu đó và ghi rõ là bản ghi. Nếu còn thời gian, em xin mời thầy cô đặt một yêu cầu như cán bộ tuyển sinh sẽ hỏi."))
DEMO = N.get("demo", [
    ("Tra cứu", "Điểm chuẩn ngành Logistics và Quản lý chuỗi cung ứng năm 2026 là bao nhiêu, xét những tổ hợp nào?"),
    ("Tính toán", "Học phí toàn khóa ngành Kế toán hệ chính quy khoảng bao nhiêu nếu tính theo mức học phí năm 2026?"),
    ("Tư vấn", "Em thi tốt nghiệp THPT được 17 điểm khối D01. Em có thể cân nhắc những ngành nào?"),
    ("Không có trong tài liệu", "Điểm chuẩn năm 2027 của ngành Thú y là bao nhiêu?"),
])
for i, (kind, q) in enumerate(DEMO):
    y = 1.55 + i * 1.18
    box(s, 0.6, y, 12.1, 1.0, SOFT if i % 2 == 0 else RGBColor(0xF4, 0xF7, 0xFB))
    text(s, 0.85, y + 0.12, 2.6, 0.75, kind, size=18, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 3.45, y + 0.12, 9.0, 0.75, f"“{q}”", size=18, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 6.3, 12.1, 0.5, "Mời quý thầy cô đặt thêm một yêu cầu, như cán bộ tuyển sinh sẽ hỏi.", size=18, bold=True, color=GREEN)

# ---------- 5b. Dự phòng: ảnh chụp kết quả chạy thật (chỉ chiếu khi không chạy được trình diễn) ----------
SHOTS = [HERE / "shots" / f for f in ("soan_tin.png", "bao_cao_bgh.png")]
if all(p.exists() for p in SHOTS):
    s = slide("Dự phòng: kết quả chạy thật", notes=(
        "Chỉ dùng slide này nếu không chạy được trình diễn. Đây là ảnh chụp hai lượt chạy thật: bên trái là tin nhắn trả lời phụ huynh do AI soạn, "
        "bên phải là bản tóm tắt điểm chuẩn gửi Ban Giám hiệu. Khung bên phải mỗi ảnh là các bước tác tử đã làm."))
    for i, p in enumerate(SHOTS):
        s.shapes.add_picture(str(p), Inches(0.6 + i * 6.15), Inches(1.45), width=Inches(5.95))

# ---------- 6. Kết quả thử nghiệm ----------
ev = N.get("eval", {})
s = slide("Kết quả thử nghiệm", notes=ev.get("notes", (
    "Nhóm em đã soạn bộ câu hỏi thử có đáp án, gồm cả câu bẫy lấy số của năm cũ và câu hỏi không có trong tài liệu, rồi cho hệ thống trả lời "
    "và chấm. Kết quả và chi phí đo thực tế như trên slide.")))
stat(s, 0.6, 1.55, 2.85, 2.1, ev.get("accuracy", "đang đo"), ev.get("accuracy_label", "câu trả lời đúng trên bộ câu hỏi thử có đáp án"),
     fill=GREEN_SOFT, color=GREEN)
stat(s, 3.65, 1.55, 2.85, 2.1, ev.get("cost", "~800 đ"), "chi phí dịch vụ AI trung bình mỗi yêu cầu (đo thực tế)")
stat(s, 6.7, 1.55, 2.85, 2.1, ev.get("time", "1–2 phút"), "một nửa số yêu cầu xong trong khoảng này")
stat(s, 9.75, 1.55, 2.95, 2.1, ev.get("staff", "đang đo"), ev.get("staff_label", "tình huống cán bộ tuyển sinh đạt (chấm tay)"),
     fill=GREEN_SOFT, color=GREEN)
text(s, 0.6, 3.95, 12.1, 0.5, ev.get("detail_title", "Bộ câu hỏi thử gồm"), size=20, bold=True, color=DARK)
text(s, 0.6, 4.5, 12.1, 2.3, ev.get("detail", [
    "Tra cứu điểm chuẩn, học phí, tổ hợp, hồ sơ, lịch; so sánh giữa các năm; tính học phí toàn khóa, điểm ưu tiên;",
    "tư vấn chọn ngành theo điểm; câu bẫy lấy số của năm cũ; câu hỏi không có trong tài liệu (phải từ chối).",
]), size=17, spacing=1.15, after=10)

# ---------- 6b. Cán bộ sẽ hỏi gì (từ NGHIEN_CUU_NGUOI_DUNG_TUYEN_SINH.md) ----------
ask = N.get("asks", {})
s = slide("Cán bộ Trung tâm sẽ hỏi gì: phần lớn là số liệu", notes=ask.get("notes", (
    "Phần vừa trình diễn mới là giai đoạn 1: AI đọc văn bản công khai. Nhóm em đã nghiên cứu quy trình tuyển sinh năm 2026 và công việc "
    "của Trung tâm, rồi liệt kê 50 câu hỏi một cán bộ tuyển sinh sẽ hỏi nếu có một trợ lý nắm hết dữ liệu của Trung tâm. Chỉ 8 câu cần văn bản, "
    "là phần AI làm được hôm nay. Khoảng 30 câu cần số liệu tổng hợp: bao nhiêu nguyện vọng vào từng ngành, điểm chuẩn bao nhiêu thì đủ chỉ tiêu, "
    "bao nhiêu thí sinh đã xác nhận nhập học. Khoảng 12 câu cần tra tới từng hồ sơ, ví dụ ai trúng tuyển mà chưa xác nhận để gọi nhắc. "
    "Đó là giai đoạn 2: nối bản sao chỉ đọc dữ liệu tuyển sinh của Trung tâm. Danh sách này rút từ nghiên cứu tài liệu; nhóm em cần phỏng vấn "
    "cán bộ Trung tâm để xác nhận.")))
cols = [
    ("Văn bản", ask.get("docs_status", "8 câu · làm được hôm nay"), GREEN, GREEN_SOFT,
     ["Soạn tin trả lời phụ huynh về điểm chuẩn, học phí.", "Tổ hợp ngành Ngôn ngữ Trung giữa các văn bản có khớp không?",
      "Soạn thông báo xét tuyển bổ sung."]),
    ("Số liệu tổng hợp", ask.get("agg_status", "~30 câu · giai đoạn 2"), BLUE, SOFT,
     ["Đến giờ bao nhiêu thí sinh đã xác nhận nhập học, ngành nào còn thiếu nhiều chỉ tiêu nhất?",
      "Điểm chuẩn Kế toán là 15 thay vì 16 thì trúng tuyển thêm bao nhiêu?", "Nguyện vọng 1 vào từng ngành so với 2025?"]),
    ("Tra tới từng hồ sơ", ask.get("person_status", "~12 câu · giai đoạn 2"), ORANGE, ORANGE_SOFT,
     ["Ai trúng tuyển Kế toán mà chưa xác nhận, chia theo cán bộ tư vấn để gọi nhắc?", "Danh sách trúng tuyển có ai sai điều kiện không?",
      "Hồ sơ gửi bưu điện nào còn thiếu giấy tờ?"]),
]
for i, (head, status, color, fill, qs) in enumerate(cols):
    x = 0.6 + i * 4.12
    box(s, x, 1.5, 3.9, 4.55, fill)
    text(s, x + 0.25, 1.65, 3.4, 0.55, head, size=22, bold=True, color=color)
    text(s, x + 0.25, 2.2, 3.4, 0.45, status, size=15, bold=True, color=MUTED)
    text(s, x + 0.25, 2.8, 3.4, 3.2, [f"“{q}”" for q in qs], size=16, spacing=1.12, after=12)
text(s, 0.6, 6.25, 12.1, 0.6, [[(ask.get("footer_bold", "Dữ liệu cá nhân không ra khỏi Trường: "), {"bold": True, "color": DARK}),
                               (ask.get("footer", "dịch vụ AI chỉ nhận số tổng hợp; danh sách chỉ hiện cho người có quyền."), {"color": MUTED})]], size=16)

# ---------- 6c. Dự phòng cho phần số liệu (chỉ chiếu khi không chạy được) ----------
DATA_SHOTS = [HERE / "shots" / f for f in ("du_lieu_xn.png", "du_lieu_ds.png")]
if ask.get("backup_slide") and all(p.exists() for p in DATA_SHOTS):
    s = slide("Dự phòng: số liệu trên dữ liệu giả lập", notes=(
        "Chỉ dùng slide này nếu không chạy được phần số liệu. Bên trái: số thí sinh đã xác nhận nhập học theo ngành và chỉ tiêu chưa có người "
        "xác nhận. Bên phải: danh sách thí sinh Kế toán chưa xác nhận, chia theo cán bộ tư vấn. AI chỉ thấy số lượng theo mã cán bộ; bảng "
        "danh sách bên dưới lấy thẳng từ cơ sở dữ liệu. Toàn bộ là dữ liệu giả lập, không phải số liệu thật của Trường."))
    for i, p in enumerate(DATA_SHOTS):
        s.shapes.add_picture(str(p), Inches(0.6 + i * 6.15), Inches(1.45), width=Inches(5.95))

# ---------- 7. An toàn ----------
s = slide("Nguyên tắc an toàn", notes=(
    "Về an toàn, nhóm em đặt năm nguyên tắc. Một, phần số liệu vừa trình diễn chạy trên dữ liệu giả lập; dữ liệu tuyển sinh thật của Trung tâm chỉ được nối khi Nhà trường "
    "cho phép bằng văn bản, làm đúng Luật Bảo vệ dữ liệu cá nhân năm 2025. Hai, khi nối rồi, dữ liệu cá nhân vẫn không ra khỏi Trường: dịch vụ AI "
    "bên ngoài chỉ nhận số tổng hợp như số thí sinh theo ngành; danh sách tên, số điện thoại lấy thẳng từ cơ sở dữ liệu của Trường và chỉ hiện "
    "cho cán bộ có quyền. Ba, AI chỉ đọc: không ghi vào hệ thống của Bộ hay phần mềm xét tuyển; số liệu do máy tính, ghi thời điểm dữ liệu. "
    "Bốn, cán bộ duyệt trước khi gửi, AI không hứa đỗ hay trượt. Năm, AI không chấm điểm, xếp hạng thí sinh hay quyết định điểm chuẩn thay "
    "Hội đồng tuyển sinh; nó chỉ tính kịch bản tham khảo và rà soát sai sót."))
rules = [
    ("Bản thử dùng dữ liệu giả lập", "dữ liệu thật của Trung tâm chỉ nối khi Nhà trường cho phép, đúng Luật Bảo vệ dữ liệu cá nhân."),
    ("Dữ liệu cá nhân không ra khỏi Trường", "dịch vụ AI chỉ nhận số tổng hợp; danh sách thí sinh chỉ hiện cho cán bộ có quyền."),
    ("Chỉ đọc, luôn có nguồn", "không ghi vào hệ thống của Bộ; văn bản có mã nguồn, số liệu ghi thời điểm dữ liệu."),
    ("Cán bộ duyệt trước khi gửi", "thí sinh không nhận trực tiếp câu trả lời của AI; AI không hứa đỗ, trượt."),
    ("Không quyết định thay con người", "không chấm điểm, xếp hạng thí sinh; điểm chuẩn do Hội đồng tuyển sinh quyết định."),
]
for i, (head, body) in enumerate(rules):
    y = 1.5 + i * 1.02
    box(s, 0.6, y, 0.75, 0.75, GREEN)
    text(s, 0.6, y + 0.05, 0.75, 0.65, str(i + 1), size=24, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 1.6, y + 0.05, 11.1, 0.75, [[(head + ": ", {"bold": True, "color": DARK}), (body, {})]], size=20, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 8. Chi phí ----------
cost = N.get("cost", {})
s = slide("Chi phí: không cần máy chủ AI riêng", notes=(
    "Về chi phí: mỗi yêu cầu tốn khoảng " + cost.get("per_q_text", "800 đồng") + " tiền dịch vụ AI, đo thực tế. Giả sử một mùa tuyển sinh cán bộ hỏi 10 nghìn lượt thì "
    "khoảng " + cost.get("season_text", "8 triệu đồng") + ". Nhóm em cũng đã tính phương án mua máy chủ chạy AI tại trường: khoảng 2,2 đến 3 tỷ đồng đầu tư và "
    "khoảng 0,8 tỷ mỗi năm, và chất lượng tiếng Việt kém hơn. Phương án đó chỉ cần nếu muốn AI đọc trực tiếp dữ liệu cá nhân. Thiết kế của nhóm "
    "tránh việc đó: dữ liệu tuyển sinh nằm trên máy chủ dữ liệu của Trường, dịch vụ AI chỉ nhận số tổng hợp, nên không cần máy chủ AI riêng."))
rows = [
    ("Mỗi yêu cầu của cán bộ", cost.get("per_q", "~800 đồng"), "đo thực tế, gồm các bước kiểm tra chéo"),
    ("Một mùa tuyển sinh (giả định 10.000 lượt)", cost.get("season", "~8 triệu đồng"), "trả theo mức dùng, có thể đặt trần chi tiêu"),
    ("Máy chủ AI riêng (2,2–3 tỷ đồng)", "không cần", "dữ liệu ở máy chủ dữ liệu của Trường; dịch vụ AI chỉ nhận số tổng hợp"),
]
for i, (item, value, note) in enumerate(rows):
    y = 1.6 + i * 1.45
    box(s, 0.6, y, 12.1, 1.25, SOFT if i < 2 else GREEN_SOFT)
    text(s, 0.9, y + 0.1, 5.2, 1.05, item, size=20, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 6.1, y + 0.1, 2.9, 1.05, value, size=26, bold=True, color=GREEN if i == 2 else DARK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 9.0, y + 0.1, 3.55, 1.05, note, size=15, color=MUTED, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 6.15, 12.1, 0.6, "Tỷ giá 26.180 đồng/USD. Chưa gồm công vận hành của cán bộ đầu mối.", size=14, color=MUTED)

# ---------- 9. Lộ trình ----------
s = slide("Từ Tuyển sinh đến sáu lĩnh vực của Nhà trường", notes=(
    "Tuyển sinh là bước đầu. Cùng một lõi điều phối, nhóm em sẽ thêm các tác tử theo mô hình sáu lĩnh vực: Đào tạo, Nghiên cứu khoa học, "
    "Hợp tác quốc tế là phạm vi của đề tài năm nay; Nhân sự, Hành chính làm sau vì cần phân quyền và dữ liệu nội bộ. Với Tuyển sinh có hai giai đoạn. "
    "Tháng 10: Trung tâm dùng thử phần văn bản, nhóm phỏng vấn cán bộ để chốt danh sách câu hỏi thật. Tháng 11, 12: nếu Nhà trường cho phép, "
    "nối bản sao chỉ đọc dữ liệu tuyển sinh năm 2026, làm đăng nhập và phân quyền, thử các câu hỏi số liệu trên dữ liệu mùa vừa qua; song song "
    "mở rộng ba lĩnh vực của đề tài. Nửa đầu năm 2027 cập nhật văn bản mới và chạy thử lại. Tháng 7 đến tháng 9 năm 2027 là mùa cao điểm: "
    "nếu đạt ngưỡng chất lượng, cán bộ dùng chính thức."))
box(s, 0.6, 1.5, 5.6, 0.85, DARK)
text(s, 0.7, 1.55, 5.4, 0.75, "Tác tử điều phối (Ban Giám hiệu)", size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
domains = [("Tuyển sinh", "đang làm", GREEN, GREEN_SOFT), ("Đào tạo", "đề tài 2026", BLUE, SOFT), ("NCKH", "đề tài 2026", BLUE, SOFT),
           ("HTQT", "đề tài 2026", BLUE, SOFT), ("Nhân sự", "sau", MUTED, RGBColor(0xF1, 0xF3, 0xF6)), ("Hành chính", "sau", MUTED, RGBColor(0xF1, 0xF3, 0xF6))]
for i, (name, when, color, fill) in enumerate(domains):
    x, y = 0.6 + (i % 3) * 1.9, 2.8 + (i // 3) * 1.55
    box(s, x, y, 1.75, 1.3, fill, color)
    text(s, x + 0.05, y + 0.15, 1.65, 1.0, [[(name, {"bold": True, "color": color, "size": 17})], [(when, {"size": 13, "color": MUTED})]],
         align=PP_ALIGN.CENTER)
arrow(s, 3.4, 2.35, 3.4, 2.8, MUTED)
text(s, 0.6, 5.95, 5.6, 0.8, "Cùng một lõi: thêm lĩnh vực là thêm tác tử và tài liệu, không làm lại hệ thống.", size=15, color=MUTED)
steps = [("10/2026 · giai đoạn 1", "Trung tâm dùng thử phần văn bản; phỏng vấn cán bộ, chốt câu hỏi thật."),
         ("11–12/2026 · giai đoạn 2", "Nối dữ liệu thật nếu được phép (đã có bản thử giả lập); mở rộng Đào tạo, NCKH, HTQT."),
         ("01–06/2027", "Cập nhật văn bản tuyển sinh 2027; chạy thử lại trên số liệu mùa trước."),
         ("07–09/2027", "Mùa cao điểm: nếu đạt ngưỡng chất lượng, cán bộ dùng chính thức.")]
for i, (when, what) in enumerate(steps):
    y = 1.5 + i * 1.3
    box(s, 6.7, y, 0.28, 0.28, BLUE if i else GREEN)
    if i < len(steps) - 1:
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(6.84), Inches(y + 0.28), Inches(6.84), Inches(y + 1.3))
        c.line.color.rgb, c.line.width = LINE, Pt(2)
    text(s, 7.2, y - 0.1, 5.5, 0.45, when, size=18, bold=True, color=DARK)
    text(s, 7.2, y + 0.35, 5.5, 0.85, what, size=16)

# ---------- 10. Đề nghị ----------
s = slide("Đề nghị Nhà trường", notes=(
    "Để triển khai, nhóm em xin đề nghị bốn việc. Một, Trung tâm Tuyển sinh và Truyền thông cử một cán bộ đầu mối, và cho nhóm phỏng vấn "
    "ba đến năm cán bộ, mỗi người 30 đến 45 phút, để chốt những câu hỏi cán bộ thật sự cần. Hai, cho phép giai đoạn 2: nối bản sao chỉ đọc "
    "dữ liệu tuyển sinh năm 2026, có văn bản đồng ý, phân quyền và nhật ký truy cập; dữ liệu cá nhân không ra khỏi Trường. Ba, Nhà trường đứng tên "
    "tài khoản dịch vụ AI chính thức, trả theo mức dùng, thay cho dịch vụ trung gian nhóm đang dùng thử. Bốn, cho cán bộ Trung tâm dùng thử "
    "từ tháng 10 và góp ý; khi đăng điểm chuẩn, chỉ tiêu thì đăng thêm bản Excel bên cạnh ảnh."))
asks = [("Cử đầu mối, cho phỏng vấn cán bộ", "3–5 cán bộ Trung tâm, mỗi người 30–45 phút, để chốt những câu hỏi thật sự cần."),
        ("Cho phép giai đoạn 2", "bản thử đã chạy trên dữ liệu giả lập; xin nối bản sao chỉ đọc dữ liệu thật, có văn bản đồng ý, phân quyền, nhật ký."),
        ("Tài khoản dịch vụ AI do Trường đứng tên", "trả theo mức dùng, có trần chi tiêu; thay dịch vụ trung gian đang dùng thử."),
        ("Cho cán bộ dùng thử từ 10/2026", "góp ý để hoàn thiện; đăng thêm bản Excel cho bảng điểm chuẩn, chỉ tiêu.")]
for i, (head, body) in enumerate(asks):
    x, y = 0.6 + (i % 2) * 6.15, 1.55 + (i // 2) * 2.55
    box(s, x, y, 5.95, 2.3, SOFT)
    text(s, x + 0.3, y + 0.2, 0.8, 0.8, str(i + 1), size=34, bold=True, color=BLUE)
    text(s, x + 1.1, y + 0.25, 4.6, 0.9, head, size=21, bold=True, color=DARK)
    text(s, x + 1.1, y + 1.1, 4.6, 1.1, body, size=16, spacing=1.15)

# ---------- 11. Cảm ơn ----------
s = slide(None, number=False, notes="Em xin cảm ơn quý thầy cô đã lắng nghe. Em rất mong nhận được ý kiến góp ý của quý thầy cô.")
box(s, 0, 0, 13.333, 7.5, DARK, radius=False)
text(s, 1.3, 2.4, 10.7, 1.2, "Xin trân trọng cảm ơn quý thầy cô", size=44, bold=True, color=WHITE)
text(s, 1.3, 3.7, 10.7, 0.8, "Kính mong nhận được ý kiến góp ý", size=26, color=RGBColor(0xDC, 0xE8, 0xF7))
text(s, 1.3, 5.3, 10.7, 0.6, "Credere · AI Tuyển sinh · Trường Đại học Nghệ An", size=16, color=RGBColor(0xB8, 0xCC, 0xE4))

prs.save(OUT)
print(f"Đã ghi {OUT} ({len(prs.slides)} slide)")
