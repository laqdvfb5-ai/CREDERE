"""Replace the unsupported small-machine TCO with evidenced large-model sizing.

Only the GPU line has an observed purchase price. A complete acquisition price
and equivalent-quality local cost per completed request remain unquoted.
"""
PRICE='https://developers.openai.com/api/docs/pricing'
QWEN_LARGE='https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-FP8'
DEEPSEEK='https://github.com/deepseek-ai/DeepSeek-V3'
VLLM='https://recipes.vllm.ai/deepseek-ai/DeepSeek-V3'
NVIDIA='https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/'
SELLER='https://sicomp.vn/card-man-hinh-leadtek-nvidia-rtx-pro-6000-blackwell-max-q-workstation-edition-96gb'
GPU_PRICE=499_990_000
GPU_TOTAL=4*GPU_PRICE
POWER=2*1.4*8760*3000
LABOR=.5*30_000_000*12
OPEX=POWER+LABOR+80_000_000+20_000_000
COST={
 'date':'2026-09-29','fx_vnd_per_usd':27000,'fx_is_budget_assumption':True,
 'api_standard_short_context_per_million':{'gpt-6-sol':{'input':2,'output':10},'gpt-6-luna':{'input':.1,'output':.5}},
 'hypothetical_run':{'master_input':20000,'master_output':2000,'worker_input':30000,'worker_output':2000},
 'api_cost_per_run_usd':.064,'api_cost_per_run_vnd':1728,
 'monthly_scenarios':[{'requests':n,'api_vnd':n*1728,'local_vnd':None,'local_reason':'No matched-quality throughput/cost benchmark.'} for n in (1000,5000,20000)],
 'price_source':PRICE,
 'local_large_model_candidate':{
   'model':'Qwen3-235B-A22B-Instruct-2507-FP8','model_source':QWEN_LARGE,
   'total_parameters_billion':235,'active_parameters_billion':22,
   'fp8_weight_only_decimal_gb_approx':235,'bf16_weight_only_decimal_gb_approx':470,
   'gpu':'RTX PRO 6000 Blackwell Max-Q 96GB','gpu_count':4,'aggregate_gpu_memory_advertised_gb':384,
   'gpu_unit_price_vnd_including_vat':GPU_PRICE,'gpu_subtotal_vnd_including_vat':GPU_TOTAL,
   'gpu_price_source':SELLER,'hardware_source':NVIDIA,
   'seller_condition':'Price listed with complete PC build only; no binding four-GPU system quotation obtained.',
   'qualification':'Sizing candidate only. Checkpoint overhead, KV cache, software support, PCIe topology and concurrency require a measured acceptance test. Not proved equivalent to API model quality or enough for the whole school.',
   'other_acquisition_costs':{'cpu_ram_ssd_chassis_psu_network':None,'ups_cooling_backup_setup':None,'redundant_model_node':None},
   'complete_capex_vnd':None,'complete_first_year_cost_vnd':None,
 },
 'larger_reference':{'model':'DeepSeek-V3 main671B','fp8_weight_only_decimal_gb_approx':671,'reference_topology':'8 x H200 in vLLM FP8 recipe','source':VLLM,'purchase_price_vnd':None},
 'annual_opex_scenario_not_quote':{
   'average_it_kw':2,'power_cooling_multiplier':1.4,'hours_per_year':8760,'assumed_vnd_per_kwh':3000,
   'electricity_cooling_vnd':POWER,'operations_fte':.5,'assumed_full_time_monthly_vnd':30_000_000,
   'labor_vnd':LABOR,'maintenance_reserve_vnd':80_000_000,'backup_monitoring_reserve_vnd':20_000_000,
   'total_vnd':OPEX,'includes_depreciation':False,
   'scope':'Operating-budget illustration for one candidate node; not measured power, salary quotation or complete school operating cost.'},
 'excluded_costs':['application development','data integration and validation','fine-tuning or training','additional replicas/HA node','extra API calls in hybrid mode','financing','taxes on unquoted services'],
 'comparable_local_per_request_cost':None,'proven_breakeven_requests':None,
 'decision':'Obtain a full configuration quote and run equal-quality/end-to-end latency tests before an acquisition decision.',
}

SIZING_NOTES=(
 'Phải định cỡ theo một model và mức phục vụ cụ thể trước khi dự toán. Qwen3-235B-A22B có 235 tỷ tham số tổng và 22 tỷ hoạt hóa mỗi token. '
 'Phép tính thô cho trọng số là khoảng 235 GB ở FP8 hoặc 470 GB BF16 (GB thập phân), chưa gồm tensor giữ precision cao, scale, KV cache, workspace, runtime và bản sao phục vụ. '
 '22B hoạt hóa không có nghĩa chỉ lưu 22B trọng số. Ví dụ TP4 trong model card cũng không bảo đảm bốn GPU bất kỳ đều đủ. '
 'Kịch bản kiểm chứng ở đây là một node bốn RTX PRO 6000 Max-Q 96GB, tổng dung lượng GPU quảng bá 384GB; phải xác nhận topology PCIe, phần mềm và mức ngữ cảnh/đồng thời. '
 'Đây không phải cấu hình đã nghiệm thu chất lượng hay đáp ứng toàn trường. DeepSeek-V3 671B FP8 là cấp khác; recipe vLLM tham chiếu tám H200, cần báo giá máy chủ riêng. '
 'Sáu AI nghiệp vụ có thể dùng chung endpoint model; không tự nhân sáu bộ trọng số. Số người dùng/agent song song vẫn làm tăng tải và bộ nhớ. '
 'Các phương án lượng tử hóa mạnh hay offload RAM có thể thay đổi chi phí nhưng phải đo lại độ đúng và thời gian, không coi tương đương API mặc định.'
)
BUDGET_NOTES=(
 'Giá tham khảo lấy trực tiếp trang Sicomp ngày 29/9/2026 cho đúng RTX PRO 6000 Blackwell Max-Q 96GB, 300W: 499.990.000 đồng/card, đã có VAT. '
 'Nhà bán ghi chỉ bán kèm build PC. Bốn card cộng 1.999.960.000 đồng; đây là phép cộng giá niêm yết, chưa phải báo giá giao hàng trọn bộ. '
 'Phần CPU, RAM máy chủ, SSD, chassis, nguồn, kết nối, mạng, UPS, làm mát, lưu trữ sao lưu và triển khai vẫn phải xin báo giá; tổng đầu tư chưa chốt và vượt riêng chi phí GPU. '
 'Không thể lấy giá máy thử model nhỏ để đại diện hệ thống phục vụ model hàng trăm tỷ tham số. Không đưa ra tổng năm đầu khi phần vốn trọn bộ chưa có giá. '
 'Kịch bản chi vận hành tách riêng: giả định công suất IT trung bình 2kW, hệ số điện/làm mát 1,4, chạy 8.760 giờ/năm và giá điện dự toán 3.000 đ/kWh thì điện là 73.584.000 đ/năm. '
 'Phân bổ 0,5 nhân sự ở mức toàn thời gian 30 triệu/tháng là 180 triệu/năm; dự phòng bảo trì 80 triệu, backup/giám sát 20 triệu. Tổng kịch bản 353.584.000 đ/năm, khoảng 354 triệu. '
 'Đây đều là giả định ngân sách, không phải số đo điện hay báo giá vận hành; chưa khấu hao, công phát triển/tích hợp dữ liệu và node dự phòng. '
 'Nếu cần sẵn sàng cao hoặc model lớn hơn, phải lập thêm cấu hình và dự toán, không giữ tổng chi phí cố định khi tăng tải.'
)
MAIN_SPEECH=(
 'Local phải tính theo model đủ lớn và tải phục vụ, không theo một máy thử nhỏ. Ví dụ Qwen 235B ở FP8 cần khoảng 235 GB chỉ cho trọng số, còn phải cộng ngữ cảnh và bộ nhớ chạy. '
 'Một cấu hình ứng viên là bốn RTX PRO 6000 Max-Q 96 GB. Giá niêm yết gần 500 triệu mỗi card, nên riêng GPU đã gần 2 tỷ đồng. '
 'Chưa gồm máy chủ, RAM, SSD, nguồn, UPS, làm mát và người vận hành. Tổng vốn và chi năm đầu phải chờ báo giá cấu hình, không chốt một số thiếu căn cứ. '
 'Đây vẫn chưa chứng minh chất lượng ngang model API. Nếu chọn cấp DeepSeek 671B, tài liệu vLLM tham chiếu tám H200: đó là quy mô máy chủ khác, cần định giá riêng.'
)
CHOICE_SPEECH=(
 'Đề xuất là dùng API cho dữ liệu được phép và thuê cấu hình tương ứng để kiểm chứng model local trước khi mua. '
 'Phí API giả định 1.728 đồng mỗi yêu cầu không thể so thẳng với một chi phí local mỗi tháng khi chưa biết local hoàn thành được bao nhiêu việc cùng chất lượng. '
 'Phải đo độ đúng, thời gian và tải đồng thời, rồi mới so tổng chi phí. Nếu dữ liệu bắt buộc nội bộ, cả Master, AI con, review và dự phòng đều phải ở tuyến đó; model local lỗi thì dừng hoặc đổi model nội bộ, không tự gửi cloud.'
)


def revise_local_deck(main, appendix, speech):
    main[8].update(title='Local model lớn: riêng bốn GPU đã gần 2 tỷ',kind='table',
      takeaway='Kịch bản kiểm chứng Qwen235B FP8 · 4 × RTX PRO 6000 Max-Q 96GB; chưa chốt công suất/chất lượng.',
      headers=['Hạng mục','Căn cứ','Chi phí tham khảo'],
      rows=[['Bốn GPU 96GB','4 × 499.990.000 đ, giá có VAT','1.999.960.000 đ'],
            ['CPU / RAM / SSD / nguồn','Máy tương thích bốn GPU, đủ băng thông','Chờ báo giá cấu hình'],
            ['UPS / làm mát / backup','Hạ tầng và vận hành tại trường','Chờ báo giá'],
            ['Tổng vốn và năm đầu','Phải cộng máy, hạ tầng và vận hành','Chưa đủ căn cứ chốt']],
      notes=SIZING_NOTES+' '+BUDGET_NOTES,
      foot='GPU là giá niêm yết kèm build PC, chưa báo giá trọn bộ. Điện/nhân sự/bảo trì tính riêng ở phụ lục A3.',
      sources=[QWEN_LARGE,NVIDIA,SELLER,VLLM,'COST_MODEL.json'])
    main[9].update(foot='Chưa có chi phí/Run local cùng chất lượng và tải; chưa kết luận hòa vốn hoặc rẻ hơn API.',
      notes='Phương án lai phải được chọn theo dữ liệu, chất lượng và ngân sách. '+SIZING_NOTES+' Không giữ đường chi phí local phẳng cho mọi mức tải. Cần báo giá trọn máy và nghiệm thu số Run hoàn tất trước khi tính giá/Run hoặc hòa vốn. Kịch bản API đã nêu chỉ là giả định token, không phải cấu hình đối chứng model local đã đạt. Tác vụ bắt buộc nội bộ không được chuyển qua cloud khi lỗi.',
      sources=[QWEN_LARGE,VLLM,'COST_MODEL.json','backend/app/llm.py'])
    speech[8]=MAIN_SPEECH
    speech[9]=CHOICE_SPEECH
    appendix[0].update(title='A1 · So chi phí khi chưa có benchmark local',kind='table',
      takeaway='API có phép tính token; local chưa có số Run/giờ và chất lượng được nghiệm thu để tính giá/Run.',
      headers=['Mức tải / tháng','API giả định','Local tương đương'],
      rows=[['1.000 Run','1,728 triệu đ','Chưa đo; chưa tính giá/Run'],['5.000 Run','8,640 triệu đ','Chưa đo; chưa tính giá/Run'],['20.000 Run','34,560 triệu đ','Phải định cỡ/nhân node nếu cần']],
      notes='Phí API trong bảng giữ giả định 0,064 USD/Run và 27.000 đ/USD, chưa thuế, tool và retry. Với local, chưa có phép đo cùng chất lượng/độ trễ nên không điền một chi phí cố định giả định cho mọi mức tải và không công bố điểm hòa vốn. '+BUDGET_NOTES,
      foot='Bỏ phép so chi phí cố định cho model nhỏ; lấy báo giá và đo tải local trước khi quyết định.',sources=[PRICE,SELLER,'COST_MODEL.json'])
    appendix[1].update(title='A2 · Model lớn cần bao nhiêu bộ nhớ?',kind='table',
      takeaway='Bộ nhớ trọng số ≈ tổng tham số × byte/tham số; sau đó còn KV cache, runtime và nhiều phiên.',
      headers=['Model / precision','Chỉ trọng số, xấp xỉ','Cấu hình cần kiểm chứng'],
      rows=[['Qwen235B · FP8','235 GB thập phân','Bốn GPU96GB là ứng viên thử'],['Qwen235B · BF16','470 GB thập phân','Cần cấu hình lớn hơn'],['DeepSeek-V3 · FP8','671 GB model chính','Recipe vLLM: 8 × H200'],['Sáu AI nghiệp vụ','Có thể dùng chung trọng số','Tải/ngữ cảnh vẫn tăng khi song song']],
      notes=SIZING_NOTES,foot='Không lấy số tham số hoạt hóa MoE làm dung lượng phải lưu. Đây chưa phải cam kết tương đương API.',sources=[QWEN_LARGE,DEEPSEEK,VLLM,NVIDIA,'LARGE_MODEL_SIZING.md'])
    appendix[2].update(title='A3 · Điện, nhân sự và bảo trì phải tính riêng',kind='table',
      takeaway='Kịch bản chi vận hành một node khoảng 354 triệu/năm, ngoài vốn máy; mọi đầu vào dưới đây là giả định.',
      headers=['Hạng mục','Giả định tính toán','Chi phí năm'],
      rows=[['Điện + làm mát','2kW × 1,4 × 8.760h × 3.000đ','73,584 triệu'],['Nhân sự vận hành','0,5 người × 30 triệu × 12 tháng','180 triệu'],['Bảo trì + backup/giám sát','Dự phòng 80 + 20 triệu','100 triệu'],['Tổng kịch bản','Chưa khấu hao / phát triển / node dự phòng','353,584 triệu']],
      notes=BUDGET_NOTES,foot='Đầu tư GPU/máy tính tách biệt. Các mức điện, nhân sự và dự phòng cần xác nhận theo hợp đồng/vận hành.',sources=[SELLER,NVIDIA,'COST_MODEL.json'])


def write_research(root):
    text=f'''# Phương án local cho mô hình lớn — bản hiệu chỉnh

Đối chiếu ngày 29/09/2026. Đây là hồ sơ định cỡ và neo giá, chưa phải báo giá trọn bộ hoặc cấu hình đã nghiệm thu cho toàn trường.

## Định cỡ trước khi định giá

{SIZING_NOTES}

## Giá phần cứng và tổng chi phí

{BUDGET_NOTES}

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

- [Qwen235B FP8]({QWEN_LARGE})
- [DeepSeek-V3]({DEEPSEEK})
- [Recipe vLLM DeepSeek-V3]({VLLM})
- [NVIDIA RTX PRO 6000 family]({NVIDIA})
- [Sicomp Max-Q 96GB]({SELLER})

Các ước lượng máy thử nhỏ và đồ thị hòa vốn trước đây không còn được dùng trong bộ trình bày hiện hành. Nguồn/cách tính máy đọc được tại COST_MODEL.json.
'''
    (root/'LOCAL_OPTIONS_RESEARCH.md').write_text(text,encoding='utf-8')
