# Đánh giá mã nguồn mở cho Credere

Ngày kiểm tra: 25/09/2026. Phương pháp: đọc trang GitHub, file LICENSE, README, metadata PyPI/Hugging Face, release/commit feed và tài liệu chính thức; gọi thử OpenAlex một lần. Một số trang không truy cập trực tiếp được và GitHub API bị giới hạn lượt gọi, nên không ghi số sao. Mục nào chưa đối chiếu tại nguồn gốc được ghi "chưa kiểm chứng". Giấy phép và tình trạng repo thay đổi theo thời gian, cần kiểm lại trước mỗi mốc. Kế hoạch sử dụng tại [PLAN.md](./PLAN.md).

**Kết luận.** Có thể dùng lại phần lớn hạ tầng: API và quản lý Run (Aegra), đăng nhập (Keycloak), nhập tài liệu (Docling), truy xuất (pgvector + underthesea), nguồn học thuật (OpenAlex, Crossref, arXiv), tìm web (SearXNG + trafilatura), trace cho đội phát triển (Langfuse), đánh giá (DeepEval, promptfoo) và giao diện chat (assistant-ui). Phần lõi của đề bài vẫn phải tự viết: graph Master với kế hoạch DAG có validator, vòng review hữu hạn, hợp đồng dữ liệu FR2, bằng chứng và quyền của báo cáo phát sinh. Không có nền tảng trọn gói nào đáp ứng đồng thời kế hoạch DAG có kiểm tra, giao thức có schema, vòng sửa hữu hạn và quyền theo nguồn mà không vướng giấy phép hoặc phải sửa sâu.

**Điều phối và API.**

| Repo | Giấy phép | Hoạt động | Đáp ứng | Thiếu, rủi ro | Chọn |
| --- | --- | --- | --- | --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | MIT | langgraph 1.2.12 (21/09/2026); langgraph-checkpoint-postgres 3.1.2 (07/08/2026) | Graph, nhánh song song, interrupt, checkpoint Postgres bền | Không có server, quản lý Run hay auth; kế hoạch DAG phải tự viết | Dùng |
| [Aegra](https://github.com/aegra/aegra) | Apache-2.0 | v0.10.6 (25/09/2026); repo chuyển từ ibbybuilds/aegra | Server tương thích Agent Protocol/LangGraph SDK trên FastAPI: checkpoint Postgres, threads, Run nền, SSE, kết nối lại bằng Last-Event-ID, runs.join, hủy, resume, route FastAPI thêm, OTel; auth handler trả bộ lọc theo người dùng; Redis tùy chọn | Bản 0.x; [issue #539](https://github.com/aegra/aegra/issues/539) (08/2026): hủy có thể báo thành công khi chưa đến worker; rollback chưa có; quickstart cần Docker | Dùng, qua spike M-1 |
| langgraph-api (Agent Server chính thức) | Elastic-2.0 | 0.14.4 (23/09/2026) | Đủ API Run/thread/SSE | Tự host production cần license key Enterprise | Không dùng |
| [langgraph-supervisor-py](https://github.com/langchain-ai/langgraph-supervisor-py) | MIT | Đã archive (07/2026) | Handoff kiểu supervisor | README khuyên tự làm supervisor bằng tool | Không dùng |
| [langgraph-swarm-py](https://github.com/langchain-ai/langgraph-swarm-py) | MIT | 0.1.0 (12/2025) | Handoff ngang hàng | Không có planner trung tâm, không có DAG | Không dùng |
| Ví dụ LLMCompiler, plan-and-execute trong repo LangGraph | MIT | Chỉ còn lưu trữ | Planner sinh DAG Task, bộ chạy Task theo phụ thuộc, joiner: gần nhất với Master | API cũ | Tham khảo thiết kế, không chép mã |
| [open_deep_research](https://github.com/langchain-ai/open_deep_research); [deepagents](https://github.com/langchain-ai/deepagents) | MIT | open_deep_research đã archive (08/2026); deepagents 0.7.19 (24/09/2026) | Supervisor, nhà nghiên cứu chạy song song, báo cáo có trích dẫn | deepagents là khung có quy ước riêng, không phải DAG có kiểu | Tham khảo prompt |

**Frontend và khung dự án.**

| Repo | Giấy phép | Hoạt động | Đáp ứng | Thiếu, rủi ro | Chọn |
| --- | --- | --- | --- | --- | --- |
| [assistant-ui](https://github.com/assistant-ui/assistant-ui) | MIT; Assistant Cloud trả phí, tùy chọn | Cập nhật 25/09/2026 | Thành phần React theo shadcn, runtime @assistant-ui/react-langgraph, danh sách thread | Màn hình kế hoạch, tiến độ, bằng chứng phải tự làm | Dùng |
| [agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) | MIT | Cập nhật 22/09/2026 | Chat Next.js cho server LangGraph; Aegra ghi là tương thích | Chỉ có chat, không có màn hình Run/DAG | Thử nhanh API |
| CopilotKit | MIT, có sản phẩm enterprise riêng | v1.73.3 (22/09/2026) | Giao thức AG-UI, tích hợp LangGraph | Lớp trừu tượng nặng hơn | Không chọn |
| vercel/chatbot | Apache-2.0 | Release cuối 07/2025 | Next.js + AI SDK | Backend TypeScript gắn dịch vụ Vercel, không phải LangGraph | Không dùng |
| [agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit) | MIT | Cập nhật 23/09/2026 | FastAPI + LangGraph, checkpointer Postgres | UI Streamlit; không thấy Run nền, hủy, kết nối lại; dùng thư viện supervisor đã archive | Tham khảo |
| [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) | MIT | 0.12.0 (12/08/2026) | FastAPI + SQLModel + Postgres + React/Vite + JWT + Compose | Không có tầng agent; trùng phần với Aegra | Tham khảo mẫu |
| [Alembic](https://github.com/sqlalchemy/alembic) | MIT | 1.20.0 (11/09/2026), Python từ 3.10 | Migration có phiên bản cho schema nghiệp vụ | Chỉ quản lý schema của ứng dụng, không đụng bảng của Aegra | Dùng |

**Nền tảng trọn gói.** Không dùng làm lõi vì đều có engine hoặc mô hình dữ liệu riêng, không có kế hoạch DAG có kiểu và vòng review hữu hạn theo đề.

| Nền tảng | Giấy phép | Hoạt động | Lý do không chọn |
| --- | --- | --- | --- |
| Dify | Apache 2.0 sửa đổi | v1.17.1 (10/09/2026) | Không được dùng đa người thuê nếu không có giấy phép thương mại; không được bỏ logo frontend; engine workflow riêng |
| Open WebUI | Open WebUI License | v0.11.4 (21/09/2026) | Không được bỏ thương hiệu khi quá 50 người dùng/30 ngày nếu không có giấy phép enterprise; một trường đại học sẽ vượt mức này |
| Onyx | MIT, thư mục ee/ theo giấy phép Enterprise | Bản nightly 25/09/2026 | Connector có quyền nhưng SSO, SCIM, RBAC thuộc Enterprise; stack nặng |
| RAGFlow | Apache-2.0 | Nightly 24/09/2026 | Chỉ đáng xét như dịch vụ phân tích tài liệu tách riêng |
| LibreChat | MIT | v0.8.8-rc4 (23/09/2026) | Ứng dụng chat, không phải hệ thống Run theo DAG |
| AnythingLLM | MIT | v1.16.2 (22/09/2026) | Ứng dụng chat/RAG |
| Kotaemon | Apache-2.0 | Commit cuối 30/05/2026 | Hoạt động chậm lại |

**Nhập tài liệu và truy xuất.**

| Repo | Giấy phép | Hoạt động | Đáp ứng | Thiếu, rủi ro | Chọn |
| --- | --- | --- | --- | --- | --- |
| [Docling](https://github.com/docling-project/docling) | MIT | v2.130.0 (22/09/2026) | PDF, DOCX, HTML, ảnh; OCR; HybridChunker; tích hợp LangChain; README ghi chạy trên Windows | Phụ thuộc ML nặng; DOCX không có số trang; metadata trang/bbox của PDF chưa kiểm chứng | Dùng |
| [markitdown](https://github.com/microsoft/markitdown) | MIT | 0.1.8 (21/09/2026) | Chuyển nhanh sang Markdown | Mất vị trí trang/mục | Không làm parser chính |
| [Unstructured](https://github.com/Unstructured-IO/unstructured) | Apache-2.0 | 0.27.8 (22/09/2026) | Nhiều định dạng | Cần libmagic, poppler, tesseract, libreoffice; Python từ 3.11 đến dưới 3.14 | Không chọn |
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) | AGPL-3.0 hoặc thương mại | 1.28.2 (08/2026) | Nhanh, có wheel Windows | AGPL | Không dùng |
| [pypdf](https://github.com/py-pdf/pypdf) | BSD-3 | 6.19.0 (16/09/2026) | Văn bản theo trang, thuần Python | Không khôi phục bố cục/bảng | Dự phòng |
| [python-docx](https://github.com/python-openxml/python-docx) | MIT | 1.2.0 (06/2025) | Đọc đoạn và style DOCX | Ít cập nhật | Dự phòng |
| [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL License | 0.8.6 (29/07/2026) | HNSW; lọc áp dụng sau quét chỉ mục, từ 0.8.0 có iterative scan để lấy đủ kết quả sau lọc | Không có bản Windows chính thức | Dùng qua Docker |
| [ParadeDB pg_search](https://github.com/paradedb/paradedb) | AGPL-3.0; Enterprise thương mại | v0.25.10 (23/09/2026) | BM25, tokenizer ICU/Ngram | Không hỗ trợ Windows (nguồn thứ cấp) | Hoãn |
| [VectorChord](https://github.com/tensorchord/VectorChord), VectorChord-bm25 | AGPL-3.0 hoặc ELv2 | Commit cuối 04/2026 | BM25 trong Postgres | Giấy phép hạn chế, hoạt động chậm lại | Hoãn |
| Full-text PostgreSQL | PostgreSQL | — | unaccent có sẵn | Không có stemmer tiếng Việt; không có điểm BM25 | Dùng cấu hình simple + unaccent trên văn bản đã tách từ |
| [underthesea](https://github.com/undertheseanlp/underthesea) | Apache-2.0 | v9.5.0 (05/2026), commit 09/2026 | word_tokenize; underthesea_core có wheel Windows cho Python 3.10–3.13 | — | Dùng |
| [pyvi](https://github.com/trungtv/pyvi) | MIT | Release cuối 2021 | Tách từ | Không cập nhật | Chỉ khi dùng model bkai |
| [VnCoreNLP](https://github.com/vncorenlp/VnCoreNLP) | GPL-3.0 | Release cuối 2023 | Tách từ | Cần Java; GPL | Không dùng |

LangChain text splitters (MIT), [Chonkie](https://github.com/chonkie-inc/chonkie) (MIT) và llama-index-core (MIT) đều đang hoạt động. LlamaIndex trùng vai trò với LangGraph nên không thêm. Tự viết lớp chia đoạn mỏng trên HybridChunker của Docling để giữ vị trí nguồn theo schema của ứng dụng.

**Embedding và reranker.**

| Model | Giấy phép | Ghi chú |
| --- | --- | --- |
| [AITeamVN/Vietnamese_Embedding](https://huggingface.co/AITeamVN/Vietnamese_Embedding) | Apache-2.0 | Tinh chỉnh từ bge-m3; 1024 chiều; tối đa 2048 token; Zalo Legal 2021 Acc@1 0,727 do tác giả báo (bge-m3 0,568; bkai 0,711) |
| [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | MIT | Dense, sparse, multi-vector; tối đa 8192 token |
| [intfloat/multilingual-e5-large-instruct](https://huggingface.co/intfloat/multilingual-e5-large-instruct) | MIT | Điểm VN-MTEB cao nhất, 67,99 |
| [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | Apache-2.0 | Tối đa 1024 chiều; ngữ cảnh 32k |
| [bkai-foundation-models/vietnamese-bi-encoder](https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder) | Apache-2.0 | Đầu vào phải tách từ trước; tối đa 256 token; VN-MTEB 54,89 |
| [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) | Apache-2.0 | Reranker đa ngôn ngữ |
| [AITeamVN/Vietnamese_Reranker](https://huggingface.co/AITeamVN/Vietnamese_Reranker) | Apache-2.0 | Tinh chỉnh từ bge-reranker-v2-m3; Zalo Acc@1 0,794 do tác giả báo |

VN-MTEB (EACL 2026 Findings, 41 tập dữ liệu dịch máy) xếp Vietnamese_Embedding ở 63,34, thấp hơn multilingual-e5-large-instruct, trong khi số liệu Zalo do tác giả model tự báo. Hai nguồn không thống nhất nên phải đo trên 50–100 câu có nhãn của trường trước khi chọn.

**Nguồn ngoài cho Search Worker.**

| Nguồn | Điều kiện dùng (kiểm tra 09/2026) | Chọn |
| --- | --- | --- |
| OpenAlex + [pyalex](https://github.com/J535D165/pyalex) (MIT, v0.21, 23/02/2026) | Từ 13/02/2026 cần API key; key miễn phí kèm 1 USD/ngày; tra một bản ghi miễn phí, lọc/liệt kê 0,10 USD/1.000, tìm kiếm 1 USD/1.000; snapshot dữ liệu CC0 miễn phí. pyalex có hỗ trợ truyền key hay không: chưa kiểm chứng | Nguồn chính cho kịch bản NCKH |
| Crossref | Không cần key; thêm mailto để vào polite pool; giới hạn đổi ngày 01/12/2025 và 21/07/2026, nên đọc header X-Rate-Limit thay vì cố định | Xác minh DOI |
| arXiv | Không quá một request mỗi 3 giây, một kết nối, tính trên mọi máy | Bản tiền ấn phẩm |
| Semantic Scholar | Có key được 1 request/giây; không key dùng chung pool, hay gặp lỗi 429 | Tùy chọn |
| [SearXNG](https://github.com/searxng/searxng) | AGPL-3.0; cài qua container hoặc script Linux; LangChain có SearxSearchWrapper | Tìm web, chạy nguyên bản trong container riêng |
| [trafilatura](https://github.com/adbar/trafilatura) | Apache-2.0; 2.2.0 (07/2026) | Trích nội dung chính và metadata |
| [crawl4ai](https://github.com/unclecode/crawl4ai) | Apache-2.0; v0.9.4 (23/09/2026) | Trang cần JS |
| [Firecrawl](https://github.com/firecrawl/firecrawl) | Server AGPL-3.0, SDK MIT; tự host nặng | Không chọn |

**Model, trace và đánh giá.**

| Repo | Giấy phép | Hoạt động | Đáp ứng | Thiếu, rủi ro | Chọn |
| --- | --- | --- | --- | --- | --- |
| LangChain init_chat_model | MIT | langchain 1.4.2 | Cấu hình model theo Worker; retry 429/5xx mặc định; InMemoryRateLimiter | Không có bảng giá, ngân sách | Dùng |
| [LiteLLM](https://github.com/BerriAI/litellm) | MIT, trừ enterprise/ | v1.102.1 (25/09/2026) | completion_cost, register_model, Router có retry/fallback/giới hạn rpm/tpm | 1.82.7 và 1.82.8 trên PyPI bị chèn mã độc ngày 24/03/2026; SSO trên 5 người, audit log, hide_secrets thuộc Enterprise | Chỉ lấy dữ liệu giá, SDK khi cần fallback; không chạy proxy |
| [Portkey gateway](https://github.com/Portkey-AI/gateway) | MIT | Bản 2.0 còn pre-release | Retry, fallback, guardrails | Viết bằng Node | Không chọn |
| [Langfuse](https://github.com/langfuse/langfuse) | MIT, trừ các thư mục ee | Commit 25/09/2026; ClickHouse mua lại 01/2026, cam kết giữ MIT | Callback LangGraph, quản lý prompt, dataset, LLM-as-judge, hàng đợi chú thích; che dữ liệu trước khi gửi | Cần Postgres + ClickHouse + Redis/Valkey + S3, khoảng 5 container; RBAC theo project, audit log, retention thuộc Enterprise | Dùng cho đội phát triển |
| [Arize Phoenix](https://github.com/Arize-ai/phoenix) | Elastic License 2.0 | 20.16.0 (23/09/2026) | Chạy bằng pip, không cần Docker | Không phải giấy phép OSI | Không chọn |
| LangSmith | SDK MIT; tự host là add-on Enterprise trả phí | — | — | Không phải mã nguồn mở | Không dùng |
| OpenLLMetry | Apache-2.0 | 0.62.3 (08/2026) | Theo chuẩn OpenTelemetry | Quy ước GenAI của OpenTelemetry còn ở trạng thái Development | Để sau |
| [DeepEval](https://github.com/confident-ai/deepeval) | Apache-2.0 | 4.2.6 (24/09/2026) | G-Eval theo tiêu chí riêng, Faithfulness, chạy như pytest | Dashboard so sánh nằm ở dịch vụ trả phí | Dùng |
| [promptfoo](https://github.com/promptfoo/promptfoo) | MIT | OpenAI mua lại 09/03/2026, cam kết giữ mã nguồn mở | Plugin red-team rbac, bola, bfla, rag-document-exfiltration, indirect-prompt-injection, cross-session-leak, rag-source-attribution | CLI Node; lộ trình do OpenAI kiểm soát | Dùng |
| [Ragas](https://github.com/vibrantlabsai/ragas) | Apache-2.0 | Release cuối 01/2026 | Faithfulness | Phát triển chậm lại | Không chọn |
| [inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) | MIT | 0.3.268 (22/09/2026) | Khung đánh giá | Hướng nghiên cứu | Không chọn |

**Đăng nhập, phân quyền và chạy nền.**

| Repo | Giấy phép | Hoạt động | Đáp ứng | Thiếu, rủi ro | Chọn |
| --- | --- | --- | --- | --- | --- |
| [Keycloak](https://github.com/keycloak/keycloak) | Apache-2.0 | Commit 25/09/2026 | OIDC, cầu nối SSO; bản zip chạy trên Windows với OpenJDK 25 | Nặng | Dùng |
| [Authentik](https://github.com/goauthentik/authentik) | MIT, trừ thư mục enterprise | Đang hoạt động | OIDC | Cần Docker, tối thiểu 2 CPU/2 GB RAM | Không chọn |
| [fastapi-users](https://github.com/fastapi-users/fastapi-users) | MIT | 15.0.5 | Tài khoản cục bộ | Chế độ bảo trì, chỉ sửa lỗi bảo mật | Không dùng |
| [OpenFGA](https://github.com/openfga/openfga) | Apache-2.0 | Commit 24/09/2026 | ReBAC kiểu Zanzibar, mô tả tự nhiên việc báo cáo kế thừa quyền của nguồn | Thêm một dịch vụ | Hoãn |
| [SpiceDB](https://github.com/authzed/spicedb) | Apache-2.0 | Commit 24/09/2026 | ReBAC, có bản Windows | Thêm một dịch vụ | Hoãn |
| [Cerbos](https://github.com/cerbos/cerbos) | Apache-2.0 | Commit 25/09/2026 | Chính sách vai trò/thuộc tính, chuyển thành bộ lọc truy vấn | Không mô tả quan hệ | Không chọn |
| [pycasbin](https://github.com/casbin/pycasbin) | Apache-2.0 | Commit 24/09/2026 | Kiểm tra vai trò/hành động trong tiến trình | Yếu khi cần liệt kê tài liệu được xem | Không chọn |
| [Oso](https://github.com/osohq/oso) | — | Release PyPI cuối 01/2024 | — | Thư viện mã nguồn mở đã ngừng | Không dùng |
| [Procrastinate](https://github.com/procrastinate-org/procrastinate) | MIT | 3.10.0 (23/09/2026) | Chỉ cần Postgres; heartbeat 10 giây; get_stalled_jobs tìm job có worker đã dừng | Chạy được trên Windows nhưng không có test tự động và không tắt êm | Dự phòng nếu Aegra không đạt |
| [DBOS](https://github.com/dbos-inc/dbos-transact-py) | MIT | 3.1.0 (25/09/2026) | Workflow bền trên Postgres | Trùng vai trò checkpoint LangGraph, dễ thành DAG thứ hai | Không dùng |
| [pgqueuer](https://github.com/janbjorge/pgqueuer) | MIT | 1.4.0 | LISTEN/NOTIFY, heartbeat | Windows chưa kiểm chứng | Không chọn |
| Hatchet, Temporal | MIT | Đang hoạt động | Nền tảng workflow đầy đủ | Quá nặng cho MVP | Không dùng |
| Celery | BSD-3 | 5.6.3 | Hàng đợi phổ biến | Không hỗ trợ Windows từ 4.x; cần Redis/RabbitMQ | Không dùng mặc định |
| Dramatiq, arq, Taskiq | Dramatiq LGPL-3.0+ | Đang hoạt động | — | Thêm broker | Không chọn |

Quyền trong MVP dùng bảng ACL + RLS của PostgreSQL; quyền của báo cáo là giao quyền của các nguồn đã dùng, lưu bằng bảng lineage. Chuyển sang OpenFGA khi mô hình quan hệ vượt khả năng biểu diễn gọn bằng SQL.

**Xuất file và guardrails.** pandoc (GPL-2.0+) gọi qua tiến trình ngoài; --reference-doc áp mẫu DOCX. python-docx (MIT) và docxtpl (LGPL-2.1) là lựa chọn điền mẫu DOCX. WeasyPrint (BSD) trên Windows cần cài Pango qua MSYS2, nên hoãn PDF. llm-guard 0.3.16 (05/2025) yêu cầu Python dưới 3.13 nên không cài được trên môi trường hiện tại. NeMo Guardrails (Apache-2.0) hỗ trợ Python 3.10–3.13 nhưng thêm lời gọi LLM và ngôn ngữ cấu hình Colang; không dùng trong MVP. Phòng prompt injection bằng thiết kế và kiểm thử bằng promptfoo.

**Spike Aegra ở M-1.** Chạy Aegra ở phiên bản đã khóa với một graph thử gồm hai nhánh song song và một Task phụ thuộc, dùng provider giả lập.

| Kiểm tra | Đạt khi |
| --- | --- |
| Hủy | Run đang chạy dừng trước bước kế tiếp, trạng thái cuối đúng, không có Task mới sau khi hủy; lặp đủ lần để phát hiện trường hợp của issue #539 |
| Crash | Dừng tiến trình giữa Run rồi khởi động lại: Run được resume từ checkpoint hoặc bị đánh dấu kẹt rõ ràng; không mất kết quả đã lưu, không chạy lại Task đã xong |
| SSE | Ngắt kết nối rồi nối lại bằng Last-Event-ID nhận đủ sự kiện, không trùng, không lẫn Run |
| Quyền | Auth handler đọc JWT Keycloak; người dùng A không đọc, nối stream, hủy hoặc liệt kê thread/Run của người dùng B |
| Tương thích | LangGraph 1.x, checkpoint Postgres, route FastAPI thêm vào, phiên bản Python trong container |
| Đồng thời | 3 Run chạy cùng lúc độc lập |

Không đạt một trong các mục hủy, crash, SSE, quyền mà không có cách vá nhỏ, hoặc muốn vá phải fork Aegra: chuyển sang FastAPI tự viết + Procrastinate giao cả Run + checkpoint LangGraph + SSE tự viết có event_id. Graph Master, Worker và schema giữ nguyên ở cả hai phương án, nên thay đổi chỉ nằm ở tầng API.

**Nguồn.**

- Aegra: [repo](https://github.com/aegra/aegra), [bảng tính năng](https://docs.aegra.dev/feature-support), [streaming](https://docs.aegra.dev/guides/streaming), [authentication](https://docs.aegra.dev/guides/authentication), [issue #539](https://github.com/aegra/aegra/issues/539)
- LangGraph: [tự host Agent Server](https://docs.langchain.com/langsmith/deploy-standalone-server), [LangSmith self-hosted](https://docs.langchain.com/langsmith/self-hosted), [ví dụ LLMCompiler](https://github.com/langchain-ai/langgraph/blob/main/examples/llm-compiler/LLMCompiler.ipynb), [bài về planning agents](https://www.langchain.com/blog/planning-agents)
- pgvector: [filtering và iterative scan](https://github.com/pgvector/pgvector#filtering); ParadeDB: [cài extension](https://docs.paradedb.com/deploy/self-hosted/extension)
- VN-MTEB: [ACL Anthology](https://aclanthology.org/2026.findings-eacl.86/), [arXiv](https://arxiv.org/abs/2507.21500)
- Nguồn học thuật: [giá OpenAlex](https://help.openalex.org/access/pricing/), [thông báo OpenAlex](https://blog.openalex.org/openalex-api-new-features-and-usage-based-pricing/), [giới hạn Crossref](https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/), [cập nhật Crossref 2026](https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137), [Semantic Scholar API](https://www.semanticscholar.org/product/api/tutorial), [điều khoản arXiv API](https://info.arxiv.org/help/api/tou.html), [LangChain SearxNG](https://python.langchain.com/docs/integrations/tools/searx_search/)
- LiteLLM: [sự cố bảo mật 03/2026](https://docs.litellm.ai/blog/security-update-march-2026), [tính năng enterprise](https://docs.litellm.ai/docs/enterprise)
- Langfuse: [self-hosting](https://langfuse.com/self-hosting), [OSS và EE](https://langfuse.com/pricing-self-host), [ClickHouse mua lại Langfuse](https://clickhouse.com/blog/clickhouse-acquires-langfuse-open-source-llm-observability)
- promptfoo: [gia nhập OpenAI](https://www.promptfoo.dev/blog/promptfoo-joining-openai/), [plugin red-team](https://www.promptfoo.dev/docs/red-team/plugins/)
- Chạy nền: [Procrastinate trên Windows](https://procrastinate.readthedocs.io/en/stable/howto/basics/windows.html), [job bị kẹt](https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html), [Celery FAQ](https://docs.celeryq.dev/en/stable/faq.html)
- Khác: [cài WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html), [quy ước GenAI của OpenTelemetry](https://github.com/open-telemetry/semantic-conventions-genai)
