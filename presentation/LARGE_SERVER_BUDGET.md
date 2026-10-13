# Căn cứ sửa ngân sách máy chủ AI local

Kiểm tra trực tiếp trang nhà sản xuất/nhà bán hàng ngày 29/09/2026. Các mốc bên dưới dùng để sửa phần chi phí của bài trình bày; chưa phải báo giá trọn hệ thống hay kết quả nghiệm thu Credere.

## 1. Giá phần cứng đã kiểm tra

| Hạng mục | Giá niêm yết | Điều kiện, phạm vi |
|---|---:|---|
| Leadtek NVIDIA RTX PRO 6000 Blackwell **Max-Q** 96 GB | **499.990.000 đồng/card**, gồm VAT | Sicomp ghi 300 W, bảo hành 36 tháng và chỉ bán kèm bộ máy. Đây là giá một GPU, không gồm máy chủ. |
| Leadtek NVIDIA RTX PRO 6000 Blackwell Workstation 96 GB | **499.000.000 đồng/card**, gồm VAT | Phúc Anh; bản Workstation 600 W khác bản Max-Q 300 W, không tráo hai phiên bản trong tính điện. |
| Leadtek NVIDIA RTX PRO 6000 Blackwell **Server Edition** 96 GB | **629.990.000 đồng/card**, gồm VAT | Sicomp ghi bảo hành 36 tháng; tản nhiệt thụ động, cần khung máy chủ phù hợp. |

Nguồn giá: [Sicomp Max-Q](https://sicomp.vn/card-man-hinh-leadtek-nvidia-rtx-pro-6000-blackwell-max-q-workstation-edition-96gb), [Phúc Anh Workstation](https://www.phucanh.vn/card-do-hoa-nvidia-rtx-pro-6000-96gb-blackwell-workstation-edition-600w.html), [Sicomp Server Edition](https://sicomp.vn/card-man-hinh-leadtek-nvidia-rtx-pro-6000-blackwell-server-edition-96gb).

Nguồn thông số: [NVIDIA RTX PRO 6000 family](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/) xác nhận Max-Q có 96 GB GDDR7 ECC, 300 W, PCIe Gen5 x16 và hướng tới cấu hình tối đa bốn GPU. Server Edition dùng tản nhiệt thụ động và dải công suất 400–600 W. Không kế thừa những lời quảng cáo về NVLink, ROI, bảo mật tuyệt đối hay chất lượng model trong bài viết của cửa hàng.

## 2. Hai mốc cấu hình để trình bày, không biến thành báo giá trọn gói

**Ứng viên A — 4 × RTX PRO 6000 Max-Q 96 GB:**

- Bộ nhớ GPU cộng gộp: **384 GB**; cần phần mềm phân chia model, không phải một vùng VRAM tự ghép lại cho mọi chương trình.
- Tiền GPU: 4 × 499.990.000 = **1.999.960.000 đồng**, khoảng **2 tỷ đồng chỉ riêng GPU**.
- Đây là ứng viên để thử model mở cỡ 235B ở FP8. Phải xác nhận model/checkpoint cụ thể, hỗ trợ của runtime, KV cache, độ dài ngữ cảnh và số tác vụ đồng thời trước khi kết luận đủ tải.
- Phần còn lại phải lấy báo giá: CPU/bo mạch đủ lane PCIe, RAM ECC, SSD, khung máy/nguồn/tản nhiệt, máy ứng dụng và CSDL, mạng, sao lưu, UPS, điện/làm mát và lắp đặt.
- **Chưa có tổng vốn mua máy được xác nhận.** Không đặt lại một con số 3 tỷ hoặc số khác như thể đã có báo giá hoàn chỉnh.

**Mốc B — 8 × RTX PRO 6000 Server Edition 96 GB:**

- Bộ nhớ GPU cộng gộp **768 GB**; tiền GPU là 8 × 629.990.000 = **5.039.920.000 đồng**, khoảng **5,04 tỷ đồng chỉ riêng GPU**.
- Cần nền tảng máy chủ được nhà tích hợp xác nhận tương thích với đủ tám GPU. Đây là mốc chi phí của lựa chọn nhiều GPU hơn, chưa phải cấu hình đã chốt cho Credere.
- Cũng chưa gồm toàn bộ phần máy chủ, phòng máy, sao lưu, vận hành hay dự phòng. Không khẳng định mức VRAM đó tự bảo đảm chạy model 671B, ngữ cảnh dài và nhiều người dùng cùng lúc.

Nếu cần chuyển sang HGX H200 để tăng bộ nhớ/băng thông kết nối, [NVIDIA H200](https://www.nvidia.com/en-us/data-center/h200/) xác nhận 141 GB mỗi GPU và nền tảng HGX 4 hoặc 8 GPU. Cần báo giá trọn cấu hình. Không lấy giá “starting at” của trang cấu hình có nhiều tùy chọn rồi gọi đó là giá máy 8 H200 đã đủ CPU/RAM/SSD.

## 3. Chi phí vận hành: công thức minh họa tách khỏi tiền mua

Ví dụ cho ứng viên A, giả định chạy 24/7; **đây là đầu vào lập ngân sách, không phải số đo hoặc báo giá**:

| Khoản | Công thức/giả định | Đồng/năm |
|---|---|---:|
| Điện và làm mát | Công suất IT trung bình 2 kW × hệ số 1,4 × 8.760 giờ × 3.000 đồng/kWh | 73.584.000 |
| Nhân sự vận hành | 0,5 người quy đổi toàn thời gian × 30 triệu đồng/tháng × 12 tháng | 180.000.000 |
| Bảo trì/dự phòng sửa chữa | Khoản phân bổ giả định | 80.000.000 |
| Giám sát và sao lưu | Khoản phân bổ giả định | 20.000.000 |
| **Tổng vận hành minh họa** | | **353.584.000** |

Hai kW là công suất toàn hệ thống giả định, không phải bốn GPU × 300 W. Hệ số 1,4 biểu thị điện phụ trợ gồm làm mát; cần đo tại nơi đặt máy. Đơn giá 3.000 đồng/kWh và nhân sự 30 triệu/tháng là giả định phân tích, không tự nhận là biểu giá điện hiện hành hoặc lương thị trường đã khảo sát. Bảo trì/giám sát cần kiểm tra để không tính trùng phần đã có trong hợp đồng mua máy.

Nếu áp dụng đúng ví dụ này, chỉ riêng **GPU + một năm vận hành** đã là **2.353.544.000 đồng**; số đó vẫn **chưa phải tổng dòng tiền năm đầu**, vì còn toàn bộ phần máy chủ ngoài GPU và hạ tầng. Khấu hao là phân bổ vốn; không cộng đồng thời cả tiền mua và khấu hao vào cùng dòng tiền năm đầu.

Ngân sách triển khai toàn dự án còn phải tách công phát triển, tích hợp hệ thống nghiệp vụ, xử lý dữ liệu, phân quyền/bảo mật, đánh giá chất lượng và đào tạo người dùng. Không đưa các khoản đó về 0 chỉ vì đang nói về chi phí model.

## 4. Mốc thuê để thử trước khi mua

[FPT AI Factory GPU VM](https://factory.fpt.ai/gpu-virtual-machine) công khai giá **RTX PRO 6000** 96 GB: 1 GPU 2,19 USD/giờ, 4 GPU 8,76 USD/giờ, 8 GPU 17,51 USD/giờ. **Giá 2,19 USD không phải giá H100/H200** trên trang này. Bảng thông số của FPT có dòng ghi loại bộ nhớ HBM3 không khớp GPU RTX; chỉ dùng giá/số GPU, lấy đặc tính phần cứng từ NVIDIA.

Giả định tỷ giá 26.000 đồng/USD: thuê 4 GPU trong 40 giờ là 350,40 USD ≈ **9.110.400 đồng**; thuê 730 giờ là 6.394,80 USD ≈ **166.264.800 đồng/tháng**. Đây là tính toán từ giá công khai, cần xác nhận thuế, vùng đặt máy, thời gian tính tiền, lưu trữ và phụ phí. Thuê GPU ngoài trường không phải mua máy đặt tại trường; cũng chưa chứng minh chất lượng hay công suất phục vụ.

## Câu có thể dùng trực tiếp trên slide

“Với ứng viên bốn GPU 96 GB để thử mô hình lớn, riêng GPU đã khoảng 2 tỷ đồng theo giá niêm yết. CPU, RAM, lưu trữ, UPS, phòng máy và vận hành cần tính thêm. Tổng vốn chỉ chốt sau benchmark và báo giá trọn hệ thống; con số 186 triệu trước đây không đại diện cho triển khai này.”
