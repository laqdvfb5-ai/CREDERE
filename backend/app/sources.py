"""Đọc kho nguồn từ tệp JSON (danh sách tài liệu đã trích), theo định dạng của DATA_PLAN.md và bộ thu thập tuyển sinh."""
import json
from pathlib import Path

from .contracts import Source


def load_sources(path: str | Path) -> list[Source]:
    """Mỗi mục cần source_id, title, text; url hoặc url_or_document_id; access_scope mặc định là public.
    Tiêu đề được nối thêm phạm vi năm (year_scope) nếu tiêu đề chưa ghi, để tác tử điều phối chọn đúng năm.
    Văn bản đã được văn bản sau cập nhật (updated_by, version_note) được ghi rõ ở tiêu đề và đầu nội dung."""
    items = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    sources, seen = [], set()
    for item in items:
        if item["source_id"] in seen:
            raise ValueError(f"Trùng mã nguồn: {item['source_id']}")
        seen.add(item["source_id"])
        title, scope = item["title"].strip(), str(item.get("year_scope") or "").strip()
        if scope and scope not in title:
            title = f"{title} ({scope})"
        text = item["text"]
        if item.get("updated_by"):
            title = f"{title} [đã có văn bản cập nhật: {', '.join(item['updated_by'])}]"
            text = f"LƯU Ý PHIÊN BẢN: {item.get('version_note') or 'đã có văn bản ban hành sau cập nhật.'}\n\n{text}"
        sources.append(Source(source_id=item["source_id"], title=title, text=text,
                              url_or_document_id=item.get("url_or_document_id") or item.get("url") or "",
                              access_scope=item.get("access_scope", "public")))
    return sources
