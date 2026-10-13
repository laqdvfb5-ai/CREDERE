"""Đo khả năng bám nguồn trên ngữ cảnh dài (điều kiện M-1 để dùng gpt-6-luna cho Worker bám nguồn).

Sinh bộ văn bản quy chế tiếng Việt có đáp án biết trước (hạt giống cố định), ở hai cỡ khoảng 20 nghìn và 50 nghìn token:
quy chế hiện hành, quy chế cũ đã bị thay thế, quyết định sửa đổi, bài diễn đàn nói sai và nhiều văn bản gây nhiễu.

Chạy:  py -3 probe_longctx.py
       py -3 probe_longctx.py --models gpt-6-luna --sizes 65000 --repeats 1   # chạy thử nhanh
Kết quả ghi vào results_longctx/.
"""
import argparse
import json
import os
import random
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import probe_v2 as V  # dùng lại chat(), has_number(), sentences(), REFUSE, KEYS, load_prices()

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_longctx")

PROGRAMS = ["chính quy", "vừa làm vừa học", "liên thông", "chất lượng cao", "văn bằng hai"]
QUALIFY = re.compile(r"cũ|trước|không còn|thay thế|sửa đổi|bãi bỏ|không chính thức|không phải|chưa được xác nhận", re.I)


# ---------- Sinh văn bản ----------

def fmt_money(n):
    return f"{n:,}".replace(",", ".")


def make_params(rng):
    """Giá trị từng chủ đề cho từng hệ; quy chế cũ khác quy chế mới ở mọi giá trị."""
    p = {}
    for i, prog in enumerate(PROGRAMS):
        p[("tc_max", prog)] = 20 + i * 2 + rng.choice([0, 1])
        p[("tc_he", prog)] = 6 + i + rng.choice([0, 1])
        p[("phi_pk", prog)] = (15 + i * 5 + rng.choice([0, 2])) * 1000
        p[("vang", prog)] = 15 + i * 3 + rng.choice([0, 1])
        p[("nam_max", prog)] = 5 + (i % 3) + rng.choice([0, 1])
    p["ngay_pk"] = 10
    return p


def old_params(new):
    return {k: (v + 3 if isinstance(v, int) and v < 100 else v + 7000) for k, v in new.items()}


TOPICS = [
    ("tc_max", "Số tín chỉ tối đa được đăng ký trong mỗi học kỳ chính", "{v} tín chỉ"),
    ("tc_he", "Số tín chỉ tối đa được đăng ký trong học kỳ phụ (học kỳ hè)", "{v} tín chỉ"),
    ("phi_pk", "Lệ phí phúc khảo bài thi kết thúc học phần", "{m} đồng mỗi học phần"),
    ("vang", "Tỷ lệ vắng mặt tối đa trên tổng số tiết của học phần để được dự thi", "{v}%"),
    ("nam_max", "Thời gian đào tạo tối đa để hoàn thành chương trình", "{v} năm"),
]
FILLER = [
    "Hồ sơ đề nghị được lập thành hai bộ, nộp trực tiếp hoặc qua hệ thống quản lý đào tạo trực tuyến của Trường.",
    "Trưởng khoa chịu trách nhiệm kiểm tra tính hợp lệ của hồ sơ trước khi chuyển về đơn vị quản lý.",
    "Trường hợp có vướng mắc phát sinh, đơn vị báo cáo Hiệu trưởng xem xét, quyết định.",
    "Kết quả xử lý được thông báo công khai trên cổng thông tin điện tử và lưu trong hồ sơ người học.",
    "Việc tổ chức thực hiện phải bảo đảm công khai, minh bạch và đúng thẩm quyền.",
    "Các đơn vị liên quan phối hợp thực hiện theo chức năng, nhiệm vụ được giao.",
]


def regulation(doc_id, title, year, params, rng, extra_note=""):
    lines = [f"===== {doc_id}: {title} (ban hành năm {year}) =====", extra_note] if extra_note else [f"===== {doc_id}: {title} (ban hành năm {year}) ====="]
    art = 1
    for chapter in range(1, 5):
        lines.append(f"Chương {chapter}. Quy định về tổ chức đào tạo, phần {chapter}")
        for key, label, unit in TOPICS:
            parts = []
            for prog in PROGRAMS:
                v = params[(key, prog)] + (chapter - 1) * 0  # cùng giá trị, lặp lại ở các chương sẽ gây trùng; chỉ dùng chương 1
                parts.append(f"đối với sinh viên hệ {prog} là " + unit.format(v=v, m=fmt_money(v)))
            if chapter == 1:
                lines.append(f"[{doc_id}, Điều {art}] {label}: " + "; ".join(parts) + ". " + rng.choice(FILLER))
            else:
                lines.append(f"[{doc_id}, Điều {art}] Quy định về thủ tục liên quan đến nội dung '{label.lower()}': "
                             + " ".join(rng.sample(FILLER, 3)))
            art += 1
    lines.append(f"[{doc_id}, Điều {art}] Thời hạn nộp đơn đề nghị phúc khảo là {params['ngay_pk']} ngày làm việc kể từ ngày công bố điểm. "
                 + rng.choice(FILLER))
    return "\n".join(lines), art


def other_regulation(doc_id, title, topic, rng, n_articles, needle=None):
    """Văn bản gây nhiễu (NCKH, HTQT, hành chính). needle = (điều, câu) chèn vào đúng điều đó."""
    lines = [f"===== {doc_id}: {title} ====="]
    for a in range(1, n_articles + 1):
        if needle and a == needle[0]:
            lines.append(f"[{doc_id}, Điều {a}] {needle[1]}")
            continue
        amount = fmt_money(rng.randint(2, 90) * 500000)
        lines.append(f"[{doc_id}, Điều {a}] Quy định về {topic} (mục {a}): mức hỗ trợ tối đa {amount} đồng cho mỗi hồ sơ đủ điều kiện. "
                     + " ".join(rng.sample(FILLER, 2)))
    return "\n".join(lines)


def build_corpus(target_chars, seed=2026):
    rng = random.Random(seed)
    new = make_params(rng)
    old = old_params(new)
    amended = {("phi_pk", "chính quy"): new[("phi_pk", "chính quy")] + 5000, ("nam_max", "liên thông"): new[("nam_max", "liên thông")] + 1}
    forum_days = 30
    needle_amount = 12_345_000

    doc_new, last_new = regulation("QĐ-620", "Quy chế đào tạo trình độ đại học", 2025, new, rng,
                                   "Quy chế này áp dụng cho sinh viên tuyển sinh từ khóa 2025 và thay thế QĐ-105.")
    doc_old, _ = regulation("QĐ-105", "Quy chế đào tạo trình độ đại học (đã được thay thế bởi QĐ-620 từ khóa 2025)", 2021, old, rng)
    art_fee = 1 + PROGRAMS.index("chính quy") * 0 + 2  # Điều 3 = phi_pk (chủ đề thứ 3 trong chương 1)
    art_years = 5                                      # Điều 5 = nam_max
    doc_amend = ("===== QĐ-712: Quyết định sửa đổi, bổ sung một số điều của QĐ-620 (ban hành năm 2026, hiệu lực từ 01/01/2026) =====\n"
                 f"[QĐ-712, Điều 1] Sửa đổi QĐ-620, Điều {art_fee}: lệ phí phúc khảo bài thi kết thúc học phần đối với sinh viên hệ chính quy là "
                 f"{fmt_money(amended[('phi_pk', 'chính quy')])} đồng mỗi học phần; các hệ khác giữ nguyên.\n"
                 f"[QĐ-712, Điều 2] Sửa đổi QĐ-620, Điều {art_years}: thời gian đào tạo tối đa đối với sinh viên hệ liên thông là "
                 f"{amended[('nam_max', 'liên thông')]} năm; các hệ khác giữ nguyên.\n"
                 "[QĐ-712, Điều 3] Các nội dung khác của QĐ-620 giữ nguyên hiệu lực.")
    doc_forum = ("===== Diễn đàn sinh viên, bài viết số 1823 (nguồn không chính thức, do sinh viên đăng) =====\n"
                 f"[Diễn đàn SV, bài 1823] Mình hỏi phòng rồi, giờ thời hạn nộp đơn phúc khảo là {forum_days} ngày, "
                 "và hệ vừa làm vừa học được đăng ký tới 40 tín chỉ mỗi kỳ nhé mọi người.")

    fillers, i = [], 0
    topics = [("QĐ-NCKH", "Quy định quản lý hoạt động khoa học và công nghệ", "hỗ trợ đề tài và công bố khoa học"),
              ("QĐ-HTQT", "Quy định quản lý hoạt động hợp tác quốc tế", "đoàn ra, đoàn vào và trao đổi học thuật"),
              ("QĐ-HC", "Quy định công tác hành chính, văn thư", "văn thư, lưu trữ và cơ sở vật chất"),
              ("QĐ-TC", "Quy chế chi tiêu nội bộ", "chi hội nghị, công tác phí và văn phòng phẩm")]
    fixed = len(doc_new) + len(doc_old) + len(doc_amend) + len(doc_forum)
    while fixed + sum(len(f) for f in fillers) < target_chars:
        doc_id, title, topic = topics[i % len(topics)]
        fillers.append(other_regulation(f"{doc_id}-{i // len(topics) + 1}", title, topic, rng, 40))
        i += 1
    # Câu cần tìm ở cuối tài liệu: chèn vào văn bản gây nhiễu cuối cùng
    last_id = f"{topics[(i - 1) % len(topics)][0]}-{(i - 1) // len(topics) + 1}"
    fillers[-1] = other_regulation(last_id, topics[(i - 1) % len(topics)][1], topics[(i - 1) % len(topics)][2], random.Random(seed + i), 40,
                                   needle=(33, f"Mức thưởng cho mỗi bài báo khoa học đăng trên tạp chí thuộc danh mục Q1 là {fmt_money(needle_amount)} đồng."))
    # Thứ tự: quy chế cũ ở đầu, quy chế mới ở ~1/3, diễn đàn ở giữa, sửa đổi ở ~2/3, câu cần tìm ở cuối
    n = len(fillers)
    order = [doc_old] + fillers[: n // 3] + [doc_new] + fillers[n // 3: n // 2] + [doc_forum] + fillers[n // 2: 2 * n // 3] + [doc_amend] + fillers[2 * n // 3:]
    corpus = "\n\n".join(order)

    Q = [
        ("dau_tai_lieu", "Theo quy chế hiện hành, sinh viên hệ vừa làm vừa học được đăng ký tối đa bao nhiêu tín chỉ trong mỗi học kỳ chính?",
         [str(new[("tc_max", "vừa làm vừa học")])], ["QĐ-620"], [str(old[("tc_max", "vừa làm vừa học")]), "40"]),
        ("cuoi_tai_lieu", "Mức thưởng cho mỗi bài báo khoa học đăng trên tạp chí thuộc danh mục Q1 là bao nhiêu?",
         [str(needle_amount)], [last_id], []),
        ("sua_doi_phi", "Lệ phí phúc khảo bài thi kết thúc học phần đối với sinh viên hệ chính quy hiện nay là bao nhiêu?",
         [str(amended[("phi_pk", "chính quy")])], ["QĐ-712"], [str(new[("phi_pk", "chính quy")]), str(old[("phi_pk", "chính quy")])]),
        ("sua_doi_nam", "Thời gian đào tạo tối đa đối với sinh viên hệ liên thông hiện nay là bao nhiêu năm?",
         [str(amended[("nam_max", "liên thông")])], ["QĐ-712"], [str(new[("nam_max", "liên thông")]), str(old[("nam_max", "liên thông")])]),
        ("quy_che_cu", "Sinh viên khóa 2025 hệ chất lượng cao được vắng tối đa bao nhiêu phần trăm số tiết của học phần để được dự thi?",
         [str(new[("vang", "chất lượng cao")])], ["QĐ-620"], [str(old[("vang", "chất lượng cao")])]),
        ("dien_dan", "Thời hạn nộp đơn đề nghị phúc khảo là bao nhiêu ngày làm việc kể từ ngày công bố điểm?",
         [str(new["ngay_pk"])], ["QĐ-620"], [str(forum_days), str(old["ngay_pk"])]),
        ("thieu_nguon", "Sinh viên hệ đào tạo từ xa được đăng ký tối đa bao nhiêu tín chỉ mỗi học kỳ chính?", [], [], []),
        ("tong_hop", "Trong một năm học gồm 2 học kỳ chính và 1 học kỳ phụ, sinh viên hệ văn bằng hai theo quy chế hiện hành được đăng ký tối đa "
                     "tổng cộng bao nhiêu tín chỉ?",
         [str(2 * new[("tc_max", "văn bằng hai")] + new[("tc_he", "văn bằng hai")])], ["QĐ-620"], []),
        # Bẫy khó hơn: sửa đổi chỉ áp dụng cho hệ khác, nhân với giá trị đã sửa, giá trị không bị sửa nằm cạnh giá trị đã sửa
        ("sua_doi_bay", "Lệ phí phúc khảo bài thi kết thúc học phần đối với sinh viên hệ liên thông hiện nay là bao nhiêu?",
         [str(new[("phi_pk", "liên thông")])], ["QĐ-620"], [str(amended[("phi_pk", "chính quy")]), str(old[("phi_pk", "liên thông")])]),
        ("nhan_phi", "Một sinh viên hệ chính quy nộp đơn phúc khảo 3 học phần. Tổng lệ phí phải nộp theo quy định hiện hành là bao nhiêu?",
         [str(3 * amended[("phi_pk", "chính quy")])], ["QĐ-712"], [str(3 * new[("phi_pk", "chính quy")]), str(3 * old[("phi_pk", "chính quy")])]),
        ("nam_khac", "Thời gian đào tạo tối đa đối với sinh viên hệ chất lượng cao hiện nay là bao nhiêu năm?",
         [str(new[("nam_max", "chất lượng cao")])], ["QĐ-620"],
         [str(amended[("nam_max", "liên thông")]), str(old[("nam_max", "chất lượng cao")])]),
    ]
    for code, _, gold, _, forbidden in Q:  # đáp án đúng không được trùng số bị cấm, nếu không bài chấm vô nghĩa
        assert not set(gold) & set(forbidden), code
    return corpus, Q


# ---------- Chấm ----------

def grade(q, r):
    code, _, gold, cites, forbidden = q
    t = r.get("text", "") if r["ok"] else ""
    c = {}
    if code == "thieu_nguon":
        c["tu_choi"] = bool(V.REFUSE.search(t))
        c["khong_bia_so"] = not [s for s in V.sentences(t) if re.search(r"\d+\s*tín chỉ", s) and "từ xa" in s and not re.search(r"không|chưa", s)]
        return c
    c["dung_dap_an"] = all(V.has_number(t, g) for g in gold)
    c["trich_dung_nguon"] = all(ci in t for ci in cites)
    bad = [s for s in V.sentences(t) for f in forbidden if V.has_number(s, f) and not QUALIFY.search(s)]
    c["khong_dung_so_sai"] = not bad
    return c


SYS = ("Bạn là trợ lý của trường đại học. Chỉ trả lời dựa trên tài liệu được cấp. Mỗi nhận định ghi mã nguồn trong ngoặc vuông, "
       "ví dụ [QĐ-620, Điều 1]. Khi có văn bản sửa đổi hoặc văn bản thay thế, dùng quy định đang có hiệu lực. Nguồn không chính thức "
       "không được dùng làm căn cứ. Nếu tài liệu không đủ, nói rõ là chưa đủ căn cứ và không suy đoán. Trả lời ngắn gọn.")


GATEWAY_FLAKY = re.compile(r"^HTTP (401|403|429|5\d\d|None)\b")  # cổng từng trả 401/502 ngắt quãng với key đúng


def run_one(model, size, corpus, q, rep):
    msgs = [{"role": "system", "content": SYS},
            {"role": "user", "content": f"TÀI LIỆU:\n{corpus}\n\nCÂU HỎI: {q[1]}"}]
    for tries in range(1, 6):
        r = V.chat(V.KEYS["openai-key"], model, msgs, 1500)
        if r["ok"] or not GATEWAY_FLAKY.match(r.get("error", "")):
            break
        time.sleep(15 * tries)
    # Lỗi cổng không phải lỗi model: không chấm, báo riêng
    checks = grade(q, r) if r["ok"] else {}
    return {"model": model, "size": size, "q": q[0], "rep": rep, "checks": checks, "tries": tries,
            "score": round(sum(checks.values()) / len(checks), 3) if checks else None,
            **{k: r.get(k) for k in ("ok", "text", "error", "in_tokens", "out_tokens", "latency", "reported_model")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gpt-6-luna,gpt-6-sol,gpt-5.6-sol")
    ap.add_argument("--sizes", default="65000,165000", help="số ký tự mục tiêu (~20k và ~50k token)")
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default="results_longctx", help="thư mục kết quả (trong model_probe)")
    ap.add_argument("--questions", default=".*", help="biểu thức chọn mã câu hỏi, ví dụ 'sua_doi_bay|nhan_phi|nam_khac'")
    args = ap.parse_args()
    global RES
    RES = os.path.join(HERE, args.out)
    os.makedirs(RES, exist_ok=True)
    models = args.models.split(",")
    sizes = [int(s) for s in args.sizes.split(",")]
    corpora = {s: build_corpus(s) for s in sizes}
    for s, (c, _) in corpora.items():
        open(os.path.join(RES, f"corpus_{s}.txt"), "w", encoding="utf-8").write(c)
    pick = re.compile(args.questions)
    jobs = [(m, s, q, rep) for m in models for s in sizes for q in corpora[s][1] if pick.fullmatch(q[0]) for rep in range(args.repeats)]
    n_q = len(jobs) // max(1, len(models) * len(sizes) * args.repeats)
    print(f"[1] {len(jobs)} lời gọi: {len(models)} model × {len(sizes)} cỡ × {n_q} câu × {args.repeats} lần", flush=True)
    with ThreadPoolExecutor(args.workers) as ex:
        rows = list(ex.map(lambda j: run_one(j[0], j[1], corpora[j[1]][0], j[2], j[3]), jobs))
    json.dump(rows, open(os.path.join(RES, "raw.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    prices = V.load_prices()
    L = ["# Bám nguồn trên ngữ cảnh dài", "",
         "| Model | Cỡ (token vào trung vị) | Điểm (lượt chấm được) | Câu trượt | Lỗi cổng | Trễ trung vị (s) | Chi phí vòng đo ($) |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for m in models:
        for s in sizes:
            rs = [r for r in rows if r["model"] == m and r["size"] == s]
            ok = [r for r in rs if r["ok"]]
            p, _, _ = V.price_for(m, prices)
            cost = sum((r["in_tokens"] or 0) * p[0] + (r["out_tokens"] or 0) * p[1] for r in ok) / 1e6 if p else 0
            failed = sorted({f"{r['q']}#{r['rep']}" for r in ok if r["score"] < 1})
            L.append(f"| {m} | {int(statistics.median([r['in_tokens'] for r in ok])) if ok else '—'} | "
                     f"{statistics.mean(r['score'] for r in ok):.2f} ({len(ok)}/{len(rs)}) | {', '.join(failed) or '—'} | "
                     f"{len(rs) - len(ok)} | {statistics.median([r['latency'] for r in ok]) if ok else '—'} | {cost:.3f} |"
                     if ok else f"| {m} | — | — | — | {len(rs)} | — | 0 |")
    open(os.path.join(RES, "SUMMARY.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L), flush=True)


if __name__ == "__main__":
    sys.exit(main())
