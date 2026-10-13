# Căn cứ định cỡ LLM lớn chạy nội bộ

Ngày đối chiếu: 29/09/2026. Tài liệu này xác minh kích thước và điều kiện phục vụ suy luận; không phải báo giá mua sắm hoặc cam kết chất lượng trên Credere.

## Kết luận dùng để sửa slide

Không đủ căn cứ dùng 186 triệu đồng làm tổng ngân sách local cho toàn bộ Credere với yêu cầu LLM lớn. Phải chốt model, mức lượng tử hóa, độ dài ngữ cảnh, số yêu cầu đồng thời và thời gian phản hồi trước khi định giá. Máy thử model nhỏ, máy chạy model lớn và hạ tầng vận hành toàn hệ thống là các phạm vi chi phí riêng.

Số AI nghiệp vụ không phải số bản model cần nạp: nhiều AI có chỉ dẫn, quyền và công cụ riêng có thể dùng chung một dịch vụ model nội bộ. Code `backend/app/apps.py` tạo client cho từng AI con để tách lượt chạy/sổ lời gọi; điều đó không mặc nhiên tạo một bộ trọng số riêng trên GPU. Ngược lại, nhiều AI cùng chạy làm tăng tải, ngữ cảnh đang giữ và số lời gọi; cần định cỡ theo tải thực tế.

## Kích thước model tham khảo

Các số dung lượng sau là **tính toán lý thuyết cho trọng số**, theo tổng tham số × số byte/tham số, đơn vị GB thập phân. Chúng chưa gồm KV cache, activation, bộ nhớ chạy framework, tensor giữ độ chính xác cao, scale lượng tử hóa hoặc bản sao phục vụ thêm. Không dùng trực tiếp các số này như VRAM bảo đảm chạy được.

| Model | Tổng tham số / hoạt hóa mỗi token | BF16, xấp xỉ | FP8, xấp xỉ | 4 bit, lý thuyết |
|---|---:|---:|---:|---:|
| Qwen3-235B-A22B-Instruct-2507 | 235B / 22B | 470 GB | 235 GB | 117,5 GB |
| DeepSeek-V3, phần model chính | 671B / 37B | 1.342 GB | 671 GB | 335,5 GB |
| Llama-3.1-405B-Instruct | 405B, dense | 810 GB | 405 GB | 202,5 GB |

**MoE giảm lượng tính toán trên từng token; không có nghĩa chỉ lưu 22B hoặc 37B trọng số.** Muốn giữ toàn model trên GPU phải tính các expert của toàn bộ model. Offload sang RAM/CPU hoặc nén mạnh có thể thay đổi cấu hình, nhưng cần đo lại tốc độ, độ chính xác và số người dùng phục vụ được.

- Qwen công bố 235B tổng, 22B hoạt hóa và checkpoint FP8. Ví dụ triển khai chính thức dùng vLLM với `--tensor-parallel-size 4`; trang không xác nhận bốn GPU bất kỳ đều đủ. Khi thiếu bộ nhớ, tài liệu đề nghị hạ context, ví dụ xuống 32.768. [Model card chính thức Qwen](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-FP8).
- DeepSeek công bố 671B tổng, 37B hoạt hóa; checkpoint trên Hugging Face có 685B gồm thêm module MTP 14B. Vì vậy phép tính 671 GB chỉ biểu diễn trọng số model chính ở một byte/tham số. [Kho chính thức DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3).
- Meta công bố bản 405B. Đây chỉ là đối chiếu kích thước, chưa phải đề xuất chọn cho tiếng Việt; model card không liệt kê tiếng Việt trong tám ngôn ngữ được hỗ trợ. [Model card chính thức Meta](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct).

## Cấu hình có căn cứ kỹ thuật

**DeepSeek-V3 FP8: một node 8 × H200 là cấu hình tham chiếu có tài liệu vLLM**, không phải số GPU tối thiểu tuyệt đối của mọi cách chạy. Recipe còn nêu lựa chọn 8 × MI300X/MI325X/MI355X; bản FP4 riêng có recipe 4 × B200. Phải giữ đúng biến thể model và precision khi so sánh giá. [Recipe DeepSeek-V3 của vLLM](https://recipes.vllm.ai/deepseek-ai/DeepSeek-V3).

NVIDIA công bố H200 SXM 141 GB/GPU và H100 SXM 80 GB/GPU; node tám H200 có khoảng 1,1 TB bộ nhớ GPU. Bảng thông số cũng bao gồm tốc độ liên kết và băng thông, những yếu tố quan trọng khi chia model. Không thể cộng số VRAM của các card rời rồi mặc định hiệu năng tương đương HGX. [Thông số nền tảng NVIDIA HGX](https://docs.nvidia.com/enterprise-reference-architectures/hgx-ai-factory-h100-h200-b200/latest/components.html).

Với Qwen235B FP8, **4 × H100 80 GB chỉ nên ghi là cấu hình ứng viên cần benchmark**, dựa trên kích thước và ví dụ TP4; không ghi là cấu hình được Qwen bảo đảm cho workload Credere. Có thể cần bộ nhớ/tài nguyên lớn hơn khi chạy nhiều yêu cầu dài. Nếu chưa có báo giá đầy đủ theo cấu hình này, dùng nhãn “chờ báo giá” thay vì con số phỏng đoán.

Khi quy đổi dung lượng, cần thống nhất GB thập phân và GiB nhị phân; đồng thời kiểm tra kích thước checkpoint thực, không chỉ so hai số tiếp thị.

## Điều kiện chốt cấu hình và tổng chi phí

vLLM hướng dẫn tăng GPU/node cho đủ model; sau đó đọc log KV cache và ước lượng concurrency để kiểm tra khả năng giữ các yêu cầu ở độ dài đã cấu hình. Những con số này vẫn cần đối chiếu thời gian đáp ứng dưới tải. Thiếu KV cache gây preemption và tính lại, làm tăng trễ. [vLLM về chia model và tăng quy mô](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/), [vLLM về tối ưu bộ nhớ và hiệu năng](https://docs.vllm.ai/en/latest/configuration/optimization/).

Bộ nghiệm thu Credere cần đo câu hỏi Việt dài, giao việc liên phòng, JSON/tool calling, trích nguồn, sửa kết quả và nhiều người dùng đồng thời. Đo độ đúng nghiệp vụ, p50/p95 thời gian trả lời hoàn chỉnh, tỷ lệ thất bại, số lời gọi/token và mức sử dụng GPU. Hiện chưa có bằng chứng rằng các model local này tương đương model API đang dùng trên các tiêu chí đó.

Dự toán mua phải có GPU, CPU/RAM, SSD, chassis/nguồn, kết nối GPU, mạng, UPS/làm mát, thiết lập và bảo hành. Tổng chi phí vận hành còn có điện, chỗ đặt máy, nhân sự, sao lưu, giám sát và dự phòng. Chi phí thuê GPU là dòng tiền thuê, không phải giá mua máy và không chứng minh dữ liệu nằm tại trường.

Không cần huấn luyện nền tảng từ đầu để chạy local: các cấu hình trên chỉ phục vụ suy luận với checkpoint đã có. Nếu đề xuất fine-tune, phải lập phần tải và chi phí bổ sung riêng.

## Câu nói ngắn trên sân khấu

“Con số 186 triệu trước đây chưa đại diện cho phương án local ở quy mô đầy đủ. Với LLM hàng trăm tỷ tham số, riêng trọng số đã cần hàng trăm GB bộ nhớ; cấu hình DeepSeek-V3 FP8 tham chiếu trong tài liệu vLLM là tám GPU H200. Chúng tôi sẽ lấy báo giá toàn bộ máy chủ và đo tải nghiệp vụ để chốt ngân sách. Các AI phòng ban có thể dùng chung dịch vụ model, còn khả năng chạy đồng thời phải được kiểm chứng.”
