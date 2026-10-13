# Phương án local cho mô hình lớn — bản hiệu chỉnh

Đối chiếu ngày 29/09/2026. Đây là hồ sơ định cỡ và neo giá, chưa phải báo giá trọn bộ hoặc cấu hình đã nghiệm thu cho toàn trường.

## Định cỡ trước khi định giá

Phải định cỡ theo một model và mức phục vụ cụ thể trước khi dự toán. Qwen3-235B-A22B có 235 tỷ tham số tổng và 22 tỷ hoạt hóa mỗi token. Phép tính thô cho trọng số là khoảng 235 GB ở FP8 hoặc 470 GB BF16 (GB thập phân), chưa gồm tensor giữ precision cao, scale, KV cache, workspace, runtime và bản sao phục vụ. 22B hoạt hóa không có nghĩa chỉ lưu 22B trọng số. Ví dụ TP4 trong model card cũng không bảo đảm bốn GPU bất kỳ đều đủ. Kịch bản kiểm chứng ở đây là một node bốn RTX PRO 6000 Max-Q 96GB, tổng dung lượng GPU quảng bá 384GB; phải xác nhận topology PCIe, phần mềm và mức ngữ cảnh/đồng thời. Đây không phải cấu hình đã nghiệm thu chất lượng hay đáp ứng toàn trường. DeepSeek-V3 671B FP8 là cấp khác; recipe vLLM tham chiếu tám H200, cần báo giá máy chủ riêng. Sáu AI nghiệp vụ có thể dùng chung endpoint model; không tự nhân sáu bộ trọng số. Số người dùng/agent song song vẫn làm tăng tải và bộ nhớ. Các phương án lượng tử hóa mạnh hay offload RAM có thể thay đổi chi phí nhưng phải đo lại độ đúng và thời gian, không coi tương đương API mặc định.

## Giá phần cứng và tổng chi phí

Giá tham khảo lấy trực tiếp trang Sicomp ngày 29/9/2026 cho đúng RTX PRO 6000 Blackwell Max-Q 96GB, 300W: 499.990.000 đồng/card, đã có VAT. Nhà bán ghi chỉ bán kèm build PC. Bốn card cộng 1.999.960.000 đồng; đây là phép cộng giá niêm yết, chưa phải báo giá giao hàng trọn bộ. Phần CPU, RAM máy chủ, SSD, chassis, nguồn, kết nối, mạng, UPS, làm mát, lưu trữ sao lưu và triển khai vẫn phải xin báo giá; tổng đầu tư chưa chốt và vượt riêng chi phí GPU. Không thể lấy giá máy thử model nhỏ để đại diện hệ thống phục vụ model hàng trăm tỷ tham số. Không đưa ra tổng năm đầu khi phần vốn trọn bộ chưa có giá. Kịch bản chi vận hành tách riêng: giả định công suất IT trung bình 2kW, hệ số điện/làm mát 1,4, chạy 8.760 giờ/năm và giá điện dự toán 3.000 đ/kWh thì điện là 73.584.000 đ/năm. Phân bổ 0,5 nhân sự ở mức toàn thời gian 30 triệu/tháng là 180 triệu/năm; dự phòng bảo trì 80 triệu, backup/giám sát 20 triệu. Tổng kịch bản 353.584.000 đ/năm, khoảng 354 triệu. Đây đều là giả định ngân sách, không phải số đo điện hay báo giá vận hành; chưa khấu hao, công phát triển/tích hợp dữ liệu và node dự phòng. Nếu cần sẵn sàng cao hoặc model lớn hơn, phải lập thêm cấu hình và dự toán, không giữ tổng chi phí cố định khi tăng tải.

| Khoản | Trạng thái | Giá trị |
| --- | --- | --- |
| RTX PRO 6000 Max-Q 96GB | Giá niêm yết 29/9, kèm build PC | 499.990.000 đ/card, có VAT |
| Bốn GPU | Cộng giá niêm yết | 1.999.960.000 đ |
| Máy tương thích, RAM/SSD/nguồn/mạng | Chưa có báo giá đủ cấu hình | Chưa chốt |
| UPS, làm mát, sao lưu, triển khai | Chưa có báo giá | Chưa chốt |
| Chi vận hành một năm | Kịch bản giả định, không gồm khấu hao | 353.584.000 đ |
| Tổng vốn / dòng tiền năm đầu | Thiếu báo giá trọn bộ | Chưa chốt |

## Điều kiện quyết định

- Chốt model/precision và độ dài ngữ cảnh mục tiêu; nhiều AI có thể dùng chung endpoint.
- Đo chuỗi giao việc bằng nguồn/câu hỏi Việt thực tế: độ đúng, JSON/tool, trích dẫn, review và sửa.
- Đo thời gian hoàn tất và đồng thời; kiểm KV cache, băng thông giữa GPU, bộ nhớ đỉnh và ngừng/khởi động lại.
- Xin báo giá đúng chassis, CPU/RAM, GPU, nguồn, SSD, mạng, UPS, bảo hành và địa điểm lắp đặt.
- Không suy số người phục vụ từ VRAM cộng dồn, không khẳng định chất lượng tương đương API chưa đo, không công bố hòa vốn chưa có chi phí/Run đạt.
- Toàn bộ giá trên cho suy luận model đã có; huấn luyện nền tảng hay fine-tune cần dự toán riêng.

## Nguồn đã mở đối chiếu

- [Qwen235B FP8](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-FP8)
- [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3)
- [Recipe vLLM DeepSeek-V3](https://recipes.vllm.ai/deepseek-ai/DeepSeek-V3)
- [NVIDIA RTX PRO 6000 family](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/)
- [Sicomp Max-Q 96GB](https://sicomp.vn/card-man-hinh-leadtek-nvidia-rtx-pro-6000-blackwell-max-q-workstation-edition-96gb)

Các ước lượng máy thử nhỏ và đồ thị hòa vốn trước đây không còn được dùng trong bộ trình bày hiện hành. Nguồn/cách tính máy đọc được tại COST_MODEL.json.
