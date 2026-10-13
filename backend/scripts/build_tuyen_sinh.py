"""Gộp các tệp nguồn đã kiểm chứng của một lĩnh vực thành kho cho AI con và ghi danh mục tài liệu (DATA_PLAN.md).

    python scripts/build_tuyen_sinh.py [--domain tuyen_sinh|dao_tao] [--root ~/credere-data]

Đọc 03_xu-ly/<lĩnh vực>/staging/*.verified.json, kiểm tra từng mục rồi ghi 03_xu-ly/<lĩnh vực>/sources.json
và cập nhật 02_danh-muc/documents.csv (mỗi mã tài liệu một dòng, ghi đè dòng cũ cùng mã).
"""
import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import DATA_ROOT  # noqa: E402

REQUIRED = ("source_id", "title", "url", "text")
CSV_FIELDS = ["ma_tai_lieu", "tieu_de", "linh_vuc", "don_vi_so_huu", "loai_van_ban", "so_hieu", "ngay_ban_hanh", "ngay_hieu_luc",
              "ngay_het_hieu_luc", "phien_ban", "thay_the_cho", "nguon", "ngay_thu_thap", "nguoi_giao", "dinh_dang", "sha256",
              "muc_truy_cap", "duoc_gui_api", "chat_luong", "trang_thai", "ghi_chu"]


def sha256(path: str) -> str:
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if path and p.is_file() else ""


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DATA_ROOT))
    ap.add_argument("--domain", default="tuyen_sinh", choices=["tuyen_sinh", "dao_tao"])
    args = ap.parse_args()
    root, domain = Path(args.root), args.domain
    stage = root / "03_xu-ly" / domain / "staging"
    items, problems = [], []
    for f in sorted(stage.glob("*.verified.json")):
        for item in json.loads(f.read_text(encoding="utf-8")):
            missing = [k for k in REQUIRED if not str(item.get(k) or "").strip()]
            if missing:
                problems.append(f"{f.name}: {item.get('source_id')} thiếu {missing}")
                continue
            if item.get("access_scope", "public") != "public":
                problems.append(f"{f.name}: {item['source_id']} không phải nguồn công khai, bỏ qua")
                continue
            items.append({**item, "access_scope": "public", "_file": f.name})
    ids = [i["source_id"] for i in items]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        print("Trùng mã nguồn:", ", ".join(dupes))
        return 1
    items.sort(key=lambda i: i["source_id"])
    versions_file = root / "03_xu-ly" / domain / "versions.json"  # văn bản nào đã được văn bản sau cập nhật
    versions = json.loads(versions_file.read_text(encoding="utf-8")) if versions_file.exists() else {}
    known = {i["source_id"] for i in items}
    replaces = {}
    for i in items:
        v = versions.get(i["source_id"])
        if v:
            missing = [u for u in v["updated_by"] if u not in known]
            if missing:
                print(f"versions.json: {i['source_id']} trỏ tới mã không có trong kho: {missing}")
                return 1
            i["updated_by"], i["version_note"] = v["updated_by"], v["note"]
            for u in v["updated_by"]:
                replaces.setdefault(u, []).append(i["source_id"])
    out = root / "03_xu-ly" / domain / "sources.json"
    out.write_text(json.dumps([{k: v for k, v in i.items() if k != "_file"} for i in items], ensure_ascii=False, indent=1), encoding="utf-8")

    catalog = root / "02_danh-muc" / "documents.csv"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    rows = {}
    if catalog.exists():
        with catalog.open(encoding="utf-8-sig", newline="") as fh:
            rows = {r["ma_tai_lieu"]: r for r in csv.DictReader(fh)}
    today = date.today().isoformat()
    for i in items:
        original = str(i.get("original_file") or "")
        rows[i["source_id"]] = {
            "ma_tai_lieu": i["source_id"], "tieu_de": i["title"], "linh_vuc": domain, "don_vi_so_huu": "Trường Đại học Nghệ An",
            "loai_van_ban": i.get("doc_type", ""), "ngay_ban_hanh": i.get("published", ""), "phien_ban": i.get("year_scope", ""),
            "nguon": i["url"], "ngay_thu_thap": today, "nguoi_giao": "thu thập công khai", "dinh_dang": Path(original).suffix.lstrip("."),
            "sha256": sha256(original), "muc_truy_cap": "P0", "duoc_gui_api": "có", "chat_luong": "văn bản",
            "thay_the_cho": ", ".join(replaces.get(i["source_id"], [])),
            "trang_thai": ("đã có bản cập nhật" if i.get("updated_by") else "đang dùng") if i.get("verified") else "chờ kiểm tra",
            "ghi_chu": i["_file"]}
    with catalog.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in sorted(rows.values(), key=lambda r: r["ma_tai_lieu"]):
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})

    chars = sum(len(i["text"]) for i in items)
    print(f"{len(items)} nguồn, {chars:,} ký tự (~{chars // 3:,} token) -> {out}")
    print(f"Danh mục: {catalog} ({len(rows)} dòng). Chưa kiểm chứng: {sum(not i.get('verified') for i in items)}")
    for p in problems:
        print("  !", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
