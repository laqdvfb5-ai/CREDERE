# Chạy model tại trường (on-prem) với vốn 3 tỷ đồng

Ngày 26/09/2026. Tỷ giá 26.180 đồng/USD (Vietcombank bán ra ngày 25/09/2026), nên 3 tỷ ≈ 114.600 USD. Số liệu do 9 agent tra cứu ngày 26/09/2026: 5 agent nghiên cứu, 3 agent thiết kế theo ba hướng khác nhau, 1 agent phản biện và kiểm tra lại các con số chính. Số nào không có nguồn thì ghi "ước tính". Giá GPU năm 2026 biến động mạnh: RTX PRO 6000 tăng 87% trong 18 tháng. Vì vậy cần báo giá lại trước khi đề xuất.

## Kết luận

1. **Đề tài sinh viên 3 tháng: không mua gì.**
   - Toàn bộ API của đề tài chỉ 3,8–7,2 triệu, bằng 0,1–0,3% số vốn.
   - Máy mua qua đấu thầu sớm nhất khoảng quý 2/2027 mới về.
   - Model qua API vừa rẻ hơn vừa tốt hơn.
   - Việc nên làm ngay là thay cổng trung gian bằng tài khoản API trực tiếp do trường trả tiền.
   - Nếu cần demo chạy local, thuê GPU ở FPT khoảng 2,3 triệu cho 40 giờ.
2. **Triển khai cho cả trường: mua máy không bao giờ rẻ hơn API.**
   - Với tải giả định, dùng toàn bộ API tốn khoảng **185 triệu/năm**.
   - Mua máy tốn khoảng **0,82 tỷ/năm**, gồm khấu hao 5 năm và vận hành.
   - Lý do duy nhất để mua là **tài liệu nội bộ, dữ liệu cá nhân phải xử lý trên máy của trường**.
3. **Nếu trường yêu cầu dữ liệu không rời trường:**
   - Mua một máy 3 GPU RTX PRO 6000 (96 GB mỗi card), tổng khoảng **2,2 tỷ**, giữ lại **0,77 tỷ** dự phòng.
   - Chạy theo kiểu lai: lượt chạy chỉ dùng nguồn công khai vẫn gọi `gpt-6-sol` qua API; lượt chạy có tài liệu nội bộ chạy hoàn toàn trên máy trường.
   - Trước khi mua phải qua Phase 0: thuê máy đo thử khoảng 50 triệu. Nếu model mở không đạt thì không bỏ vốn.

## So sánh các phương án

Tải giả định (ước tính):
- NAU có 315 cán bộ (4/2025). Giả định khoảng 100 người đăng ký, 30–40 người dùng mỗi ngày, 10–15 người cùng dùng giờ cao điểm.
- Mỗi ngày làm việc có 200 lượt tra cứu, 30 lượt tổng hợp và 5 lượt NCKH đầy đủ.
- Sinh viên là chủ thể dữ liệu, không phải người dùng hệ thống.

| Phương án | Vốn | Chi phí/năm | Chất lượng | Dữ liệu nội bộ | Nhận xét |
| --- | --- | --- | --- | --- | --- |
| A. Chỉ API, tài khoản trực tiếp | 0 | ~185 triệu | Tốt nhất (`gpt-6-sol`) | Không dùng được nếu chưa có phiếu đồng ý hoặc chưa lược bỏ dữ liệu cá nhân | Đúng cho đề tài 3 tháng |
| B. API cho dữ liệu công khai + thuê 2 GPU FPT trong giờ hành chính | 0 | ~0,48 tỷ | Như phương án mua | Dữ liệu ở trong Việt Nam, cần hợp đồng xử lý dữ liệu | Rẻ nhất trong các cách tuân thủ luật. Dùng cho Phase 0 và làm phương án dự phòng |
| **C. Mua 3 GPU + chạy lai (khuyến nghị nếu phải giữ dữ liệu tại trường)** | ~2,22 tỷ + 0,77 tỷ dự phòng | ~0,37 tỷ vận hành; ~0,82 tỷ nếu tính cả khấu hao | Lượt chạy công khai: `gpt-6-sol`. Lượt chạy có tài liệu nội bộ: kém hơn rõ | Không rời trường | Chỉ mua khi qua Gate G1 |
| Loại: 4 GPU, dùng một model DeepSeek-V4.1-Flash cho mọi vai trò | ~2,88 tỷ | ~0,82 tỷ | Chưa đo tiếng Việt | Không rời trường | Chưa có bản vLLM chính thức cho card RTX PRO 6000, dự phòng chỉ 4% |
| Loại: hai điểm đặt máy, Vinh + colocation Hà Nội | ~2,92 tỷ | ~0,99 tỷ | Không dùng `gpt-6-sol` | Dữ liệu nội bộ nằm ở Hà Nội | Quá lớn so với 10–15 người dùng, dự phòng 2,5% |

- **Hòa vốn so với API:** cần khoảng 178 lượt NCKH đầy đủ mỗi ngày, gấp 35 lần tải giả định và xấp xỉ công suất tối đa của máy. Chỉ chuyển Worker về máy trường thì tiết kiệm tối đa khoảng 13% tiền API.
- **Thuê trong nước (FPT AI Factory, 2,19 USD/giờ mỗi GPU):** 2 GPU giờ hành chính khoảng 303 triệu/năm, 4 GPU chạy 24/7 khoảng 2,0 tỷ/năm. Mua máy chỉ rẻ hơn khi so với thuê 24/7.

## Cấu hình khuyến nghị (phương án C)

Giá niêm yết ngày 26/09/2026, đã gồm VAT 8%. Nếu xuất hóa đơn năm 2027 với VAT 10% thì tổng khoảng 2,225 tỷ.

| Hạng mục | SL | Thành tiền (đồng) | Nguồn giá |
| --- | --- | --- | --- |
| RTX PRO 6000 Blackwell **Max-Q** 96 GB, 300 W, bảo hành 36 tháng | 3 | 1.499.970.000 | Sicomp 499,99 triệu/card; Phúc Anh, An Phát 499 triệu; chỉ bán kèm bộ máy |
| CPU AMD Threadripper PRO 9955WX | 1 | 53.999.000 | An Phát |
| Bo mạch ASUS Pro WS WRX90E-SAGE SE | 1 | 39.999.000 | An Phát |
| RAM 64 GB DDR5-5600 ECC RDIMM (256 GB, còn 4 khe trống) | 4 | 220.000.000 | An Phát 52–55 triệu/thanh |
| NVMe 4 TB chạy RAID1 | 2 | 75.998.000 | |
| Nguồn 3.000 W, vỏ 4U, tản nhiệt | 1 | 32.000.000 | ước tính |
| Lắp ráp, chạy thử 72 giờ | 1 | 15.000.000 | ước tính |
| Máy CPU cho ứng dụng, CSDL, Docling (Ryzen 9 9950X, 64 GB) | 1 | 75.000.000 | ước tính |
| UPS online 10 kVA kèm ắc quy | 1 | 76.800.000 | |
| Phòng máy: điều hòa 24k BTU thứ hai, tủ rack/PDU, cảm biến, đường điện riêng | 1 | 60.000.000 | ước tính |
| NAS sao lưu | 1 | 24.000.000 | |
| Mạng 10GbE | 1 | 12.000.000 | |
| **Tổng** | | **2.184.766.000** | |

- **Dự phòng khoảng 775 triệu:**
  - Khoảng 509 triệu là quyền mua thêm card GPU thứ 4, ghi ngay trong cùng gói thầu. Hình thức pháp lý này cần xác nhận.
  - Khoảng 172 triệu cho biến động giá.
  - Khoảng 94 triệu để trống.
  - Phần nào không dùng thì trả lại.
- **Vì sao dùng card Max-Q mà không dùng Server Edition:** Server Edition giá 630 triệu/card. Nó được xếp vào nhóm hàng trung tâm dữ liệu nên nhiều khả năng cần giấy phép xuất khẩu của Mỹ. Max-Q nhiều khả năng được miễn theo diện ACA. Nhà cung cấp phải xác nhận bằng văn bản.
- **Không chọn H200 hay 8 GPU:** 2 card H200 NVL đã khoảng 2,5–3,1 tỷ, còn 8 GPU H200 khoảng 8,9–11,5 tỷ. Mac Studio và DGX Spark nạp văn bản dài quá chậm, mỗi lượt NCKH mất 8–30 phút, chỉ hợp làm máy thử nghiệm.

**Model theo vai trò** (tên model và điểm số lấy theo tra cứu ngày 26/09/2026):

| Vai trò | Model | Đặt ở | Ghi chú |
| --- | --- | --- | --- |
| Điều phối cho lượt chạy có tài liệu nội bộ, tìm kiếm, phân tích | Qwen3.8-Flash-Next (FP8, chia trên 2 GPU; bảng n-gram khoảng 51 GB đặt ở RAM máy) | GPU 0–1 | Model mạnh duy nhất trong tầm vốn có công thức vLLM chính thức đã kiểm chứng trên RTX PRO 6000. Giấy phép Qwen Community 1.0 cho phép dùng nội bộ. Ứng viên thay thế: DeepSeek-V4-Flash (MIT) |
| Worker bám nguồn (NCKH, Đào tạo, HTQT) | Qwen3.8-27B (FP8, Apache-2.0) | GPU 2 | Đọc văn bản dài gần ngang API: AA-LCR 82,0, so với 83,3 của `gpt-6-luna` |
| Embedding, reranker | AITeamVN Vietnamese_Embedding_v2 + Vietnamese_Reranker (khoảng 3 GB), đọ thử với Qwen3-Embedding-4B | GPU 2 | Apache-2.0 |
| OCR tài liệu scan | Docling + DeepSeek-OCR-2 hoặc khả năng đọc ảnh của Qwen3.8-27B | GPU 2, chạy ban đêm | Cần thử trên văn bản tiếng Việt có dấu |
| Điều phối cho lượt chạy chỉ dùng nguồn công khai | `gpt-6-sol` qua API, tài khoản trực tiếp | — | Khoảng 120 triệu/năm |

- **Phần mềm:**
  - Ubuntu 24.04, Docker với image cố định phiên bản.
  - vLLM từ 0.29, dùng công thức chính thức và xgrammar để JSON luôn đúng schema.
  - Một bộ định tuyến tự quyết định lượt chạy đi API hay ở lại máy trường, dựa trên nhãn độ nhạy của nguồn. Trong backend, nhãn này là trường `access_scope`.
  - Prometheus/Grafana để giám sát, sao lưu mã hóa hằng đêm.
- **Năng lực phục vụ (ước tính):**
  - Khoảng 13–20 người cùng dùng giờ cao điểm, khi máy chạy 70% công suất.
  - Lượt tra cứu có tài liệu nội bộ mất khoảng 30–60 giây. Lượt NCKH đầy đủ mất khoảng 5–10 phút.
  - Model mở sinh ra số token gấp 2,3–3,2 lần `gpt-6-sol`, nên cần đặt trần độ dài suy luận và đo lại ở Phase 0.
- **Chi phí vận hành khoảng 370 triệu/năm:**
  - API `gpt-6-sol`: 120 triệu.
  - Điện: khoảng 40 triệu (1 kW × 8.760 giờ × hệ số phòng máy 1,8 × 2.449 đồng/kWh). Giá điện áp cho nhóm hành chính sự nghiệp là 2.226 đồng/kWh chưa VAT.
  - 0,4 người vận hành MLOps: 110 triệu.
  - Linh kiện, bảo trì: 40 triệu.
  - Duy trì phòng máy: 15 triệu.
  - Đánh giá tác động và bảo mật dữ liệu: 30 triệu.
  - Cập nhật bộ đánh giá: 15 triệu.

## Chất lượng so với API

- **Kém hơn rõ ở vai trò điều phối** (lập kế hoạch, nghiệm thu FR4, viết báo cáo cuối):
  - Điểm Artificial Analysis khoảng 40–42, so với 48 của `gpt-6-sol`.
  - Tiếng Việt: trên V-Bench, `gpt-5.6-sol` (dùng thay cho `gpt-6-sol`, vì `gpt-6-sol` chưa được chấm trên V-Bench) hơn các model mở khoảng 12 điểm, riêng văn hóa và văn chương thì hơn 26–29 điểm.
  - Chưa model nào trong tầm vốn có điểm tiếng Việt chính thức.
- **Gần ngang API ở Worker đọc văn bản dài.** Thêm vào đó, JSON luôn đúng schema và không còn lỗi 502/401 của cổng.
- **Hệ quả:** báo cáo từ tài liệu nội bộ sẽ kém hơn, nên cần cán bộ duyệt trước khi dùng. Lãnh đạo trường phải chấp nhận điều này.

## Lộ trình

1. **Phase 0 (10–12/2026, khoảng 50 triệu từ kinh phí vận hành):**
   - Gắn nhãn độ nhạy cho từng nguồn dữ liệu.
   - Soạn bộ đánh giá 150–200 việc thật của NAU; bộ này cũng chính là bài đo M-1b.
   - Thuê máy FPT 2 và 4 GPU để đọ Qwen3.8-Flash-Next, DeepSeek-V4-Flash và `gpt-6-sol`.
   - Đo token thật của mỗi lượt chạy.
   - Chốt nguồn vốn và hình thức đấu thầu.
2. **Gate G1 (12/2026–01/2027):** chỉ mua nếu model mở đạt ngưỡng chất lượng đã thống nhất, và lãnh đạo chấp nhận chi thêm khoảng 0,6 tỷ/năm so với API để giữ dữ liệu tại trường. Không đạt thì dùng phương án B.
3. **Đấu thầu quý 1/2027, đưa vào dùng khoảng quý 2–3/2027.** Nộp đánh giá tác động xử lý dữ liệu trong 60 ngày kể từ lần xử lý đầu tiên.
4. **Gate G2 (khoảng 6 tháng sau khi đưa vào dùng):** chỉ mua card thứ 4 nếu có một trong ba điều sau; nếu không thì trả lại tiền dự phòng.
   - Tải đỉnh vượt 70% ít nhất 10 ngày mỗi tháng, liên tục 2 tháng.
   - Lượt tra cứu có tài liệu nội bộ mất quá 60 giây (p95).
   - Có model 4 GPU được hỗ trợ chính thức và hơn model hiện dùng từ 5 điểm trở lên trên bộ đánh giá NAU.

## Pháp lý (chưa được luật sư kiểm tra lại)

- **Đấu thầu:**
  - Theo NĐ 349/2026 (hiệu lực 09/09/2026), chỉ định thầu chỉ áp dụng tới 1 tỷ cho mua sắm thường xuyên.
  - Gói khoảng 3 tỷ thường phải đấu thầu rộng rãi qua mạng, mất khoảng 4–8 tháng.
  - Chia nhỏ gói để né đấu thầu là hành vi bị cấm (Luật Đấu thầu, Điều 16.6.l).
  - NAU trực thuộc UBND tỉnh Nghệ An, nên việc duyệt đi theo Sở Tài chính.
- **Dữ liệu cá nhân (Luật 91/2025, hiệu lực 01/01/2026):**
  - Gửi dữ liệu cá nhân ra nền tảng nước ngoài là chuyển dữ liệu xuyên biên giới. Việc này cần hồ sơ đánh giá tác động nộp Bộ Công an trong 60 ngày, cùng hợp đồng với bên nhận. Điều khoản của cổng trung gian gần như chắc chắn không đáp ứng.
  - Phạt tới 5% doanh thu năm trước hoặc 3 tỷ.
  - Chạy tại trường chỉ bỏ được hồ sơ chuyển xuyên biên giới. Trường vẫn cần đánh giá tác động xử lý dữ liệu, bộ phận bảo vệ dữ liệu và các biện pháp theo Điều 30.
- **Bí mật nhà nước,** kể cả đề thi quốc gia, không bao giờ được đưa vào bất kỳ hệ thống AI nào.
- **Luật Trí tuệ nhân tạo 134/2025:** Credere là công cụ hỗ trợ cán bộ nên nhiều khả năng thuộc rủi ro thấp. Nó sẽ thành rủi ro cao nếu chấm điểm hoặc xếp hạng sinh viên.

## Cần xác nhận trước khi mua

- Kết quả đọ model trên bộ đánh giá NAU, có số token thật của mỗi lượt.
- Báo giá của ít nhất 3 nhà cung cấp cho trọn bộ máy, ghi rõ: còn hàng Max-Q, bảo hành 36 tháng có dịch vụ tới Vinh, ngày giao và thời hạn báo giá.
- Văn bản của nhà cung cấp xác nhận mã ECCN và diện miễn trừ ACA cho card Max-Q.
- Nguồn vốn, dòng ngân sách, và việc gói này là mua thiết bị riêng hay dự án chuyển đổi số (NĐ 224/2026).
- Phòng máy: ít nhất 3 kW trên đường điện riêng, làm mát đủ cho mùa hè ở Vinh, UPS, phòng cháy, kiểm soát ra vào.
- Người vận hành sau khi đề tài kết thúc, khoảng 0,4 người.
- Rà soát giấy phép: Qwen Community 1.0, NVIDIA Open Model License nếu dùng bản NVFP4, MIT/Apache cho các model còn lại.

## Câu hỏi cho nhà trường

1. 3 tỷ là vốn thật của trường không? Lấy từ ngân sách, nguồn thu của trường, kinh phí khoa học công nghệ hay tài trợ?
2. Dữ liệu bắt buộc phải nằm trong trường, hay chỉ cần nằm trong Việt Nam, có hợp đồng xử lý dữ liệu (thuê FPT)? **Câu trả lời này quyết định mua hay thuê.**
3. Credere sẽ đọc những tài liệu nội bộ nào: quy chế, nhân sự, hồ sơ sinh viên hay tài chính?
4. Bao nhiêu cán bộ sẽ thật sự dùng, mỗi ngày bao nhiêu lượt?
5. Lãnh đạo có chấp nhận báo cáo tiếng Việt kém hơn ở các lượt chạy có tài liệu nội bộ, đổi lại dữ liệu không rời trường không?
6. Trường có sẵn phòng máy không, và ai vận hành hệ thống?
7. Trường có trả khoảng 85–120 triệu/năm cho API `gpt-6-sol` qua tài khoản trực tiếp không?

## Nguồn chính

- Giá card: [Sicomp](https://sicomp.vn/card-man-hinh-leadtek-nvidia-rtx-pro-6000-blackwell-workstation-edition-96gb), [Phúc Anh](https://www.phucanh.vn/card-do-hoa-nvidia-rtx-pro-6000-96gb-blackwell-workstation-edition-600w.html), [Phong Vũ](https://phongvu.vn/vga-leadtek-nvidia-rtx-pro-6000-96g-max-q--s251102058) (hết hàng ngày 26/09/2026), [TechPowerUp: giá 16.000 USD](https://www.techpowerup.com/351549/nvidia-rtx-pro-6000-blackwell-96-gb-gpu-now-costs-usd-16-000).
- Linh kiện: [An Phát (RAM, CPU, bo mạch)](https://www.anphatpc.com.vn/tim?q=WRX90).
- Thuê GPU: [FPT AI Factory](https://factory.fpt.ai/gpu-virtual-machine).
- Model: [công thức vLLM cho Qwen3.8-Flash-Next](https://recipes.vllm.ai/Qwen/Qwen3.8-Flash-Next), [Artificial Analysis](https://artificialanalysis.ai/models/open-source), [V-Bench](https://vbench.ai).
- Giá điện: [QĐ 1279/QĐ-BCT](https://luatvietnam.vn/dien-luc/quyet-dinh-1279-qd-bct-cua-bo-cong-thuong-quy-dinh-ve-gia-ban-dien-399752-d1.html).
- Đấu thầu: [NĐ 349/2026](https://xaydungchinhsach.chinhphu.vn/nghi-dinh-so-349-2026-nd-cp-sua-doi-quy-dinh-ve-lua-chon-nha-thau-giao-nhiem-vu-dat-hang-dau-thau-119260910215132272.htm).
- Xuất khẩu: [EAR §740.8 (ACA)](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-740/section-740.8).
- Chi tiết từng agent (tra cứu, ba thiết kế, bản phản biện) nằm trong nhật ký workflow `wf_fdc0e560-107`.
