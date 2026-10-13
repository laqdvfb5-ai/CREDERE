# Phương án model tại trường — dữ liệu để soạn slide

Kiểm tra nguồn chính thức ngày **29/09/2026**. Đây là ứng viên cần thử nghiệm, chưa phải cấu hình đã chạy Credere hay báo giá mua máy.

## Các lựa chọn có căn cứ

Qwen công bố Qwen3-8B, 14B và 32B theo Apache 2.0; tài liệu hãng có hướng dẫn triển khai bằng vLLM hoặc Ollama. Chọn chúng làm mốc thử, không tuyên bố đây là model mới nhất hay tốt nhất. [Qwen](https://qwenlm.github.io/blog/qwen3/)

| Ứng viên Ollama | File Q4_K_M | GPU để bắt đầu thử* | Mục đích |
|---|---:|---:|---|
| Qwen3-8B | 5,2 GB | 16–24 GB VRAM | Tra cứu, chọn truy vấn |
| Qwen3-14B | 9,3 GB | 24 GB VRAM | Thử cả Worker và điều phối |
| Qwen3-32B | 20 GB | 48 GB VRAM | Đối chứng chất lượng với model nhỏ |

Nguồn kích thước: [8B](https://ollama.com/library/qwen3:8b), [14B](https://ollama.com/library/qwen3:14b), [32B](https://ollama.com/library/qwen3:32b).

*VRAM là ước lượng khởi đầu của nhóm, cần benchmark; kích thước file không phải toàn bộ bộ nhớ chạy. Cần thêm KV cache, runtime, ngữ cảnh và phiên đồng thời. Thử đầu với ngữ cảnh 8K và một phiên; tăng dần. Không hứa 24GB đủ chạy 32B ở ngữ cảnh dài. Qwen3-8B có ngữ cảnh gốc 32.768 token, mở rộng bằng YaRN cần cấu hình riêng. [Model card](https://huggingface.co/Qwen/Qwen3-8B)

Ollama phù hợp thử nhanh; vLLM là lựa chọn cần đánh giá cho phục vụ đồng thời. Giao thức tương thích OpenAI giúp nối backend, nhưng vẫn phải thử JSON/schema, streaming, timeout và toàn bộ chuỗi giao việc. API tương thích không bảo đảm cùng chất lượng. [Ollama](https://docs.ollama.com/api/openai-compatibility), [hướng dẫn vLLM của Qwen](https://huggingface.co/Qwen/Qwen3-8B)

## Giá thuê đã kiểm tra

Runpod niêm yết A40 48GB **0,49 USD/giờ**, RTX 4090 24GB **0,74 USD/giờ**. Đây là giá GPU cloud tham khảo, không phải máy đặt tại trường. [Bảng giá chính thức](https://www.runpod.io/pricing)

Với A40, giả định tỷ giá **26.000 đồng/USD**:

- 176 giờ/tháng: 86,24 USD ≈ **2,24 triệu đồng/tháng**.
- 730 giờ/tháng: 357,70 USD ≈ **9,30 triệu đồng/tháng**.

Chưa gồm lưu trữ, thuế, công vận hành và các phí khác; kiểm tra vùng đặt máy, tồn kho và hợp đồng trước khi thuê. Cloud GPU vẫn là xử lý ngoài trường.

## Mô hình chi phí sở hữu minh họa

Giả định máy trọn bộ **150 triệu**, dùng 36 tháng; vận hành **3 triệu/tháng** gồm nhân sự phân bổ 2 triệu, điện/làm mát 0,5 triệu, bảo trì 0,5 triệu. Đây là giả định lập ngân sách, chưa gắn với báo giá/cấu hình cụ thể.

- Khấu hao: 150/36 = **4,17 triệu/tháng**.
- Tổng chi phí quy đổi: **7,17 triệu/tháng**, khoảng **86 triệu/năm**.
- Dòng tiền năm đầu: **186 triệu**; tổng ba năm: **258 triệu**.
- Chưa gồm phát triển ứng dụng, nhập dữ liệu, bảo mật, dự phòng sự cố, thuế hay chi phí vốn.

So API theo **chi phí một câu hỏi hoàn tất**, cộng token của mọi AI con, nghiệm thu và lần sửa. Nếu giả định API 5.000 đồng/câu thì mức chi tương đương khoảng **1.434 câu/tháng**. Đây không phải điểm hòa vốn đã chứng minh: phải đối chiếu cùng chất lượng, số phiên và độ trễ. Dùng giá API chính thức ở slide giá riêng; không lấy giá cổng trung gian làm giá OpenAI.

## Quyết định và những điều không kế thừa

Đề xuất pilot bằng API trực tiếp với nguồn được phép gửi; thử local bằng bộ câu hỏi giống nhau trước khi mua. Local giúp kiểm soát nơi xử lý, nhưng vẫn cần quyền truy cập, sao lưu và quản trị. Phương án lai chỉ gửi dữ liệu đã được phép; báo cáo AI con cũng có thể chứa thông tin nhạy cảm.

Không kế thừa kết luận trong LOCAL_HOSTING.md rằng máy trường “không bao giờ rẻ hơn API”, JSON “luôn đúng”, model local chắc chắn kém hơn, số người đồng thời, giá máy 2,2 tỷ, hay tiến độ mua sắm chưa xác nhận. Các khẳng định đó cần chứng cứ riêng; điểm benchmark công khai không thay bài nghiệm thu nghiệp vụ của trường.
