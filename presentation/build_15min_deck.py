"""15-minute deck + detailed notes + traceable requirements and cost model.

Source content in detailed_content.py is a research bank; only MAIN below is the
15-minute talk. Extra detail goes into 8 optional appendix slides and the handout.
"""
from copy import deepcopy
import html
import json
from pathlib import Path
import shutil

from lxml import etree
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

import deck_design as d
from detailed_content import SLIDES, REQS, PRICE, MODELS, DATA, QWEN, OLLAMA, GPU
from project_scope_15min import revised_main, SPEECH
from large_local_budget import COST, revise_local_deck, write_research
from security_strategy import revise_security_deck, write_security_method

HERE=Path(__file__).resolve().parent
NAME='Credere_15_phut_day_du'
def src(n, **changes):
    s=deepcopy(SLIDES[n-1]); s.update(changes); return s

MAIN=[
 src(1,seconds=40,title='Credere: một nền tảng, nhiều trợ lý AI',takeaway='Tổng thể dự án · cách hoạt động · triển khai · API/local · bảo mật',
     notes=SLIDES[0]['notes']+' Mục tiêu toàn dự án hướng tới sáu lĩnh vực: Tuyển sinh, Đào tạo, NCKH, HTQT, Nhân sự và Hành chính. Hiện có hai AI lĩnh vực cùng AI Tổng hợp; phần mở rộng có điều kiện về dữ liệu và quyền.'),
 src(4,seconds=55),
 src(6,seconds=50),
 src(7,seconds=65,foot='Bản ghi 29/9: hai AI con có kế hoạch riêng; T3 đợi T1 + T2; 18 lượt gọi, 4 phút 47 giây.',
     notes=SLIDES[6]['notes']+' '+SLIDES[9]['notes']),
 src(11,seconds=150,foot='Giới hạn demo 2 phút 30 giây; nếu chưa xong, tiếp tục bài và dùng ảnh dự phòng khi cần.',
     notes='Mở https://proxyllm.store, chọn AI Tổng hợp, giới thiệu một yêu cầu liên lĩnh vực. Thời gian phần demo là 2 phút 30 giây, không phải cam kết hệ thống trả lời trong mốc này. Câu liên lĩnh vực trong hồ sơ mất 4 phút 47 giây, nên chỉ cần cho thấy kế hoạch và AI con nhận việc trong phần live. Nếu chưa xong, chuyển sang slide tiếp; dùng phụ lục ảnh kết quả đã lưu khi cần và nói rõ nguồn gốc. Không chạy nhiều câu cùng lúc trong phần trình diễn. Khi có kết quả, mở Nguồn đã dẫn, chỉ mốc dữ liệu và giới hạn. Giao diện nhập tay/gợi ý chạy mới, không có nút Bản ghi; không hướng dẫn Shift+bấm. Domain đã được xác nhận tải web và SSE bản ghi, chưa nghiệm thu tải live lớn. Số liệu nghiệp vụ vẫn giả lập dù toàn bộ dữ liệu đã được chuyển lên VPS.'),
 src(13,seconds=60),
 src(15,seconds=70,title='API OpenAI: giá và cách tính một yêu cầu',
     rows=[['GPT-6 Sol · Master/review','$2,00','$10,00','Standard · short context'],['GPT-6 Luna · Worker','$0,10','$0,50','Standard · short context']],
     foot='Ví dụ tổng Master 20k/2k + Worker 30k/2k → $0,064 ≈ 1.728 đ/Run; tỷ giá giả định 27.000 đ/USD.',
     takeaway='Cộng mọi lời gọi trong một Run; API trực tiếp và giá gateway hiện tại là hai kênh khác nhau.',
     notes='Bảng dùng đơn vị USD trên một triệu token, Standard short context, kiểm tra tài liệu OpenAI ngày 29/9/2026. Sol định hướng làm Master/review, Luna làm Worker. Một yêu cầu người dùng gồm nhiều lời gọi nên phải cộng cả AI con và lần sửa. Minh họa Master tổng 20 nghìn token vào, 2 nghìn ra là 0,06 USD; Worker 30 nghìn vào, 2 nghìn ra là 0,004 USD. Tổng 0,064 USD, với tỷ giá dự toán 27.000 là 1.728 đồng. Đây là giả định, không phải trung bình đã đo hay giá cố định mỗi câu. Ngữ cảnh dài, cache, công cụ, thuế và retry phải tính riêng. Demo hiện gọi gateway; triển khai API OpenAI trực tiếp cần tài khoản trường, ánh xạ model và chạy lại kiểm chứng trên đúng kênh.',
     sources=[PRICE,MODELS,'https://developers.openai.com/api/docs/models/gpt-6-sol','COST_MODEL.json']),
 src(18,seconds=70,title='Model local: chủ động dữ liệu, thêm công vận hành',
     takeaway='Ứng viên Qwen3 + Ollama/vLLM; cần benchmark trên máy thực trước khi mua.',
     notes=SLIDES[16]['notes']+' '+SLIDES[17]['notes'],sources=[QWEN,OLLAMA,GPU,'LOCAL_OPTIONS_RESEARCH.md','COST_MODEL.json']),
 src(19,seconds=45),
 src(20,seconds=45),
 src(21,seconds=45),
 src(25,seconds=60,title='Bảo mật: từ cài đặt đến dữ liệu nghiệp vụ',
     takeaway='Mật khẩu cài đặt đã có; quyền đọc/xuất dữ liệu theo người dùng vẫn phải bổ sung.',
     rows=[['Danh tính / quyền','SSO, vai trò; kiểm API, nguồn, CSV','Thử cho phép/từ chối/thu hồi'],['Dữ liệu gửi model','Lọc câu hỏi, log, nhóm nhỏ; local-only','Không lộ PII hoặc đi sai tuyến'],['Hạ tầng / bí mật','TLS, CSDL riêng, key, hạn mức','Kiểm cổng, quyền và thu hồi key'],['Vận hành','Log có hạn lưu; backup mã hóa; restore','Diễn tập sự cố và khôi phục']],
     notes='Bản demo có HTTPS và mật khẩu bảo vệ API cấu hình, nhưng không có đăng nhập nghiệp vụ cho từng phòng ban. Tab Hiệu trưởng không xác minh chức danh. Pilot cần SSO, vai trò và kiểm quyền ngay tại backend cho hỏi đáp, nguồn, lịch sử, SSE và tải CSV. Code đã tách hàng cá nhân trong truy vấn, nhưng câu hỏi, văn bản, báo cáo và log vẫn cần kiểm; tổng hợp nhóm nhỏ vẫn có thể làm lộ người. Với API OpenAI, không dùng dữ liệu huấn luyện mặc định không đồng nghĩa không giữ log: điều kiện lưu giữ và ZDR phải kiểm theo hợp đồng/endpoint. Với local-only, mọi bước kể cả review và dự phòng phải ở tuyến nội bộ. Vận hành cần quản key, hạn mức, log có hạn lưu và backup phục hồi được; giao phòng CNTT chịu trách nhiệm.',
     sources=['backend/app/settings_auth.py','backend/app/web.py','SECURITY_BENEFITS_DRAFT.md',DATA],
     foot='Đề xuất pilot; hiện chưa có phân quyền hỏi đáp theo người dùng. Chi tiết chính sách API ở phụ lục A5.'),
 src(27,seconds=65),
 src(29,seconds=45,title='Nghiệm thu bằng công việc thật và người phụ trách',
     takeaway='Đầu mối nghiệp vụ duyệt nguồn; CNTT vận hành; nhóm phát triển sửa; lãnh đạo nghiệm thu.',
     notes=SLIDES[28]['notes']+' Đo thêm năng suất bằng 30 tác vụ mới, hai cách tự làm/có AI với cùng nguồn; tính cả thời gian cán bộ sửa. Đơn vị dữ liệu xác nhận chỉ số; CNTT quản hệ thống và backup; nhóm phát triển chịu trách nhiệm release và test; người nghiệm thu chốt kết quả. Các con số 159 test, 30/30 hay 14/14 trước đó chỉ là bằng chứng nội bộ, không thay nghiệm thu độc lập.',
     foot='Mỗi báo cáo đạt cần đúng nguồn, số và phạm vi; thử sai quyền không có rò rỉ. Mục tiêu chất lượng phải chốt trước.'),
 src(30,seconds=35),
]
MAIN = revised_main(MAIN)
APPENDIX=[
 src(19,backup=True,seconds=0,title='A1 · So chi phí ở ba mức tải giả định'),
 src(17,backup=True,seconds=0,title='A2 · Ứng viên và cấu hình thử model local'),
 src(31,title='A3 · Giả định và phép tính chi phí'),
 src(12,backup=True,seconds=0,title='A4 · Kết quả nội bộ và giới hạn bộ chấm'),
 src(24,backup=True,seconds=0,title='A5 · Chính sách dữ liệu của OpenAI API'),
 src(23,backup=True,seconds=0,title='A6 · Kiểm soát toàn bộ luồng dữ liệu'),
 src(32,title='A7 · Ảnh kết quả Tổng hợp để dự phòng'),
 src(34,title='A8 · Đối chiếu yêu cầu và nguồn tham khảo'),
]
revise_local_deck(MAIN, APPENDIX, SPEECH)
revise_security_deck(MAIN, APPENDIX, SPEECH)
DECK=MAIN+APPENDIX
assert len(MAIN)==15 and sum(s['seconds'] for s in MAIN)==900
for spec, speech in zip(MAIN, SPEECH):
    spec['explanation'] = spec['notes']
    spec['notes'] = speech

(HERE/'COST_MODEL.json').write_text(json.dumps(COST,ensure_ascii=False,indent=2),encoding='utf-8')
write_research(HERE)
write_security_method(HERE)

def make_table(s, spec):
    heads,rows=spec['headers'],spec['rows']; cols=len(heads)
    widths={2:[3.1,8.83],3:[3.0,4.12,4.81],4:[3.0,2.91,2.91,3.11]}[cols]
    top=2.63; available=3.67
    rh=min(.89,(available-.52)/max(1,len(rows)))
    xs=[.7]
    for w in widths: xs.append(xs[-1]+w)
    d.rect(s,.7,top,11.93,.50,d.NAVY,radius=.03)
    for i,h in enumerate(heads):d.text(s,xs[i]+.13,top+.1,widths[i]-.26,.31,h,13,d.WHITE,True)
    for j,row in enumerate(rows):
        y=top+.54+j*rh
        d.rect(s,.7,y,11.93,rh-.04,d.WHITE,d.LINE,radius=.025)
        for i,cell in enumerate(row):
            size=16 if cols<4 else 14
            d.text(s,xs[i]+.13,y+.13,widths[i]-.26,rh-.19,cell,size,d.BLUE if i==0 else d.INK,bold=i==0)
    if len(rows)==2:
        d.rect(s,.78,5.30,11.75,.88,d.SOFT)
        d.text(s,1.04,5.5,11.18,.51,'Một câu hỏi người dùng = nhiều lời gọi AI.\nTính tổng Master + Worker + sửa + tổng hợp.',18,d.BLUE,True)

def make_cards(s,spec):
    items=spec['items']; n=len(items)
    for j,(head,body) in enumerate(items):
        x=.73+(j%2)*6.05; y=2.65+(j//2)*1.72
        d.rect(s,x,y,5.86,1.55,d.WHITE,d.LINE,radius=.04)
        d.circle(s,x+.19,y+.22,.40,f'{j+1:02}',d.BLUE,d.SOFT,12)
        d.text(s,x+.78,y+.20,4.78,.38,head,19,d.INK,True)
        d.text(s,x+.78,y+.74,4.72,.65,body,16,d.MUTED)

def make_six_domains(s,spec):
    colors=[d.TEAL,d.BLUE,d.PURPLE,d.AMBER,d.BLUE,d.TEAL]
    for j,(head,body) in enumerate(spec['items']):
        x=.73+(j%3)*4.07; y=2.68+(j//3)*1.86
        d.rect(s,x,y,3.79,1.71,d.WHITE,d.LINE,radius=.05)
        d.text(s,x+.2,y+.16,3.39,.40,head,19,colors[j],True)
        d.line(s,x+.2,y+.67,x+3.59,y+.67)
        d.text(s,x+.2,y+.85,3.38,.73,body,15,d.INK)

def make_project_orchestration(s,spec):
    d.rect(s,1.10,2.72,11.13,.64,d.NAVY)
    d.text(s,1.3,2.86,10.73,.32,'Master: hiểu yêu cầu → lập kế hoạch → chọn AI trong quyền được cấp',19,d.WHITE,True,PP_ALIGN.CENTER)
    d.line(s,6.66,3.37,6.66,3.62,d.BLUE,1.6,True)
    domains=['Tuyển sinh','Đào tạo','Nghiên cứu khoa học','Hợp tác quốc tế','Nhân sự','Hành chính']
    for j,title in enumerate(domains):
        x=1.1+(j%3)*3.82;y=3.71+(j//3)*.82
        d.rect(s,x,y,3.48,.62,d.WHITE,d.LINE)
        d.text(s,x+.1,y+.13,3.28,.36,title,19,[d.TEAL,d.BLUE,d.PURPLE][j%3],True,PP_ALIGN.CENTER)
    d.text(s,1.11,5.44,11.13,.38,'Dùng công cụ tìm kiếm, truy vấn và tính toán; làm tuần tự hoặc song song theo phụ thuộc.',15,d.MUTED,align=PP_ALIGN.CENTER)
    d.rect(s,1.1,5.96,11.13,.61,d.SOFT)
    d.text(s,1.26,6.08,10.81,.34,'Kiểm tra / sửa → Báo cáo, kế hoạch, chi phí và nguồn → Người dùng phê duyệt',18,d.BLUE,True,PP_ALIGN.CENTER)

def make_privacy_router(s,spec):
    d.rect(s,.83,2.77,11.67,.64,d.NAVY)
    d.text(s,1.03,2.92,11.27,.31,'Tại trường: kiểm quyền → truy vấn / tính thống kê → giữ định danh hoặc thay mã tạm',18,d.WHITE,True,PP_ALIGN.CENTER)
    d.text(s,1.1,3.54,11.13,.34,'Cổng chính sách kiểm phần được gửi ra trước mọi lời gọi AI',17,d.BLUE,True,PP_ALIGN.CENTER)
    d.line(s,6.66,3.94,6.66,4.12,d.BLUE,1.3,True)
    for j,(title,body,color) in enumerate([
        ('API bên ngoài','Chỉ nội dung tối thiểu\nđã được phép xuất',d.TEAL),
        ('Model nội bộ','Nội dung bắt buộc giữ kín;\náp dụng cả review / tổng hợp',d.BLUE),
        ('Dừng / chờ duyệt','Chưa có tuyến hoặc quyền\nphù hợp để xử lý',d.AMBER)]):
        x=.83+j*3.99
        d.rect(s,x,4.21,3.69,1.30,d.WHITE,d.LINE)
        d.text(s,x+.15,4.35,3.39,.34,title,19,color,True,PP_ALIGN.CENTER)
        d.text(s,x+.15,4.79,3.39,.60,body,14,d.INK,align=PP_ALIGN.CENTER)
    d.rect(s,.83,5.90,11.67,.58,d.SOFT)
    d.text(s,1.02,6.03,11.29,.31,'Tại trường: kiểm đầu ra + quyền người nhận → ghép thông tin vào mẫu → hiển thị / xuất',17,d.BLUE,True,PP_ALIGN.CENTER)
    d.text(s,.94,5.57,11.41,.25,'Mã tạm không tự làm dữ liệu ẩn danh; không đủ điều kiện xuất thì giữ lại.',13,d.MUTED,align=PP_ALIGN.CENTER)

def make_pipeline(s,spec):
    for j,(head,body) in enumerate(spec['items']):
        x=.72+j*3.07
        d.node(s,x,3.16,2.77,1.80,head,body,[d.BLUE,d.PURPLE,d.TEAL,d.AMBER][j])
        if j<3:d.line(s,x+2.78,4.0,x+3.05,4.0,d.BLUE,1.5,True)
    d.text(s,1.0,5.44,11.25,.75,'Nginx + HTTPS → FastAPI / LangGraph → dữ liệu theo lĩnh vực\nModel hiện qua API; local là phương án bổ sung cần kiểm chứng.',20,d.MUTED,align=PP_ALIGN.CENTER)

def make_delegation(s,spec):
    d.node(s,4.57,2.67,4.18,.98,'AI Tổng hợp','Mô tả năng lực → kế hoạch giao việc',d.PURPLE)
    d.line(s,6.66,3.65,6.66,3.93,d.BLUE)
    d.line(s,3.35,3.93,9.98,3.93,d.BLUE)
    for x,title,body,color in [(1.15,'AI Tuyển sinh','70 văn bản · 19 truy vấn',d.TEAL),(7.77,'AI Đào tạo','36 văn bản · 17 truy vấn',d.AMBER)]:
        center=x+2.2;d.line(s,center,3.93,center,4.15,d.BLUE,arrow=True)
        d.node(s,x,4.18,4.40,1.12,title,body,color)
        d.line(s,center,5.30,center,5.51,d.BLUE)
    d.line(s,3.35,5.51,9.98,5.51,d.BLUE)
    d.line(s,6.66,5.51,6.66,5.75,d.BLUE,arrow=True)
    d.rect(s,2.25,5.76,8.8,.64,d.NAVY)
    d.text(s,2.43,5.87,8.45,.36,'Kết quả AI con → Phân tích khi cần → Master tổng hợp',19,d.WHITE,True,PP_ALIGN.CENTER)

def make_image(s,spec):
    d.screen(s,spec['image'],.77,2.60,8.27,3.92)
    d.text(s,9.4,2.92,3.02,.92,'Demo\nproxyllm.store',23,d.BLUE,True)
    labels=spec['items'] or [['Nguồn ảnh','Lượt chạy đã lưu'],['Dữ liệu','Nghiệp vụ giả lập']]
    for j,(head,body) in enumerate(labels):
        d.text(s,9.4,4.10+j*1.04,3,.4,head,17,d.INK,True)
        d.text(s,9.4,4.56+j*1.04,3,.70,body,14,d.MUTED)

for index,spec in enumerate(DECK,1):
    notes=spec['notes']
    if spec.get('explanation'):
        notes+='\n\nCHI TIẾT DÀNH CHO HỎI ĐÁP — KHÔNG ĐỌC TOÀN BỘ TRONG 15 PHÚT:\n'+spec['explanation']
    s=d.slide(spec['title'],spec['section'],spec['seconds'],notes,spec['sources'],dark=spec['kind']=='cover',backup=spec['backup'])
    if spec['backup']:
        s._element.set('show','0')  # Appendix stays in the file but is skipped in the regular slide show.
    if spec['kind']=='cover':
        # Cover headline has its own spacious layout.
        for sh in list(s.shapes):
            if sh.has_text_frame and sh.text==spec['title']:
                s.shapes._spTree.remove(sh._element)
        d.text(s,.78,1.68,7.3,2.18,'Trợ lý AI\ncho toàn trường.',43,d.WHITE,True)
        d.text(s,.81,4.0,7.1,1.07,'Sáu lĩnh vực nghiệp vụ.\nPhối hợp để hoàn thành công việc.',25,d.LIGHT)
        d.pill(s,.83,5.86,6.43,'15 PHÚT · TỔNG THỂ / VẬN HÀNH / CHI PHÍ / BẢO MẬT','283D57','D3E1F4',11)
        for j,(h,b) in enumerate(spec['items']):d.node(s,8.61,2.0+j*1.38,3.70,1.10,h,b,[d.BLUE,d.TEAL,d.AMBER][j],dark=True)
        d.text(s,.84,6.42,11.8,.32,'Tầm nhìn, phạm vi và phương án xây dựng hệ thống Credere',13,d.LIGHT)
        d.text(s,.84,5.25,7.0,.32,'Phục vụ nghiệp vụ và quyết định có căn cứ.',15,d.LIGHT)
    else:
        d.text(s,.71,2.17,11.86,.42,spec['takeaway'],16,d.MUTED)
        {'cards':make_cards,'table':make_table,'pipeline':make_pipeline,'delegation':make_delegation,'image':make_image,'six_domains':make_six_domains,'project_orchestration':make_project_orchestration,'privacy_router':make_privacy_router}[spec['kind']](s,spec)
        if spec['foot']:d.text(s,.79,6.60,11.77,.31,spec['foot'],11,d.MUTED)
    for shape in s.shapes:
        for ref in shape._element.xpath('.//a:effectRef'):ref.set('idx','0')
        if shape.has_text_frame:
            # Keep geometry stable between PowerPoint and LibreOffice.
            pr=shape.text_frame._txBody.bodyPr
            for fit in list(pr):
                if fit.tag in (qn('a:spAutoFit'),qn('a:normAutofit')):pr.remove(fit)
            if pr.find(qn('a:noAutofit')) is None:pr.append(etree.Element(qn('a:noAutofit')))
        if shape.left<0 or shape.top<0 or shape.left+shape.width>d.prs.slide_width+100 or shape.top+shape.height>d.prs.slide_height+100:
            raise ValueError(f'Shape outside page: slide {index}, {shape.name}')

d.prs.core_properties.title='Credere — toàn bộ dự án, triển khai và bảo mật (15 phút)'
d.prs.save(HERE/f'{NAME}.pptx')

mapping={k:[i for i,s in enumerate(DECK,1) if k in s['req']] for k in REQS}
lines=['# Nội dung chi tiết bài thuyết trình Credere — 15 phút','',
 'Theo đủ nội dung trong `yeucauslide.txt`. Bản chính **15 slide, tổng 15 phút**; 8 slide phụ lục chỉ mở khi hỏi đáp và được ẩn khỏi lượt trình chiếu thông thường. Mỗi slide có nội dung trình chiếu và lời nói đầy đủ dưới đây.','',
 '**Trọng tâm:** toàn bộ công việc mà dự án sẽ làm khi hoàn chỉnh, gồm sáu lĩnh vực, nhóm người dùng, đầu vào/đầu ra, phối hợp và bàn giao. Tình trạng demo chỉ là một mục minh chứng ở slide 6.','',
 '**Thời lượng:** bao gồm 1 phút 20 giây giới thiệu bản demo. Nếu yêu cầu live chưa xong, chuyển tiếp; ảnh phụ lục là kết quả đã lưu, phải nói rõ.','',
 '**Ngày đối chiếu:** 29/09/2026. **Demo:** https://proxyllm.store. Các tệp này không chứa mật khẩu, API key hay thông tin SSH.','',
 '## Đối chiếu yêu cầu','', '| Yêu cầu | Slide chính | Chi tiết phụ lục |','| --- | --- | --- |']
for k,v in REQS.items():
    ns=mapping[k];lines.append(f'| {v} | '+', '.join(str(n) for n in ns if n<=15)+' | '+', '.join(str(n) for n in ns if n>15)+' |')
lines+=['','## Phân bổ thời gian','','| Slide | Chủ đề | Thời lượng | Mốc kết thúc |','| --- | --- | --- | --- |']
elapsed=0
for i,s in enumerate(MAIN,1):
    elapsed+=s['seconds'];lines.append(f'| {i} | {s["title"]} | {s["seconds"]//60}:{s["seconds"]%60:02} | {elapsed//60}:{elapsed%60:02} |')
lines+=['','## Nội dung và lời nói','']
htmlparts=[]
for i,s in enumerate(DECK,1):
    lines += [f'### Slide {i}. {s["title"]}','',f'**Thông điệp:** {s["takeaway"]}','', '**Nội dung trên slide:**','']
    display=[]
    if s['headers']:
        lines+=['| '+' | '.join(s['headers'])+' |','| '+' | '.join('---' for _ in s['headers'])+' |']
        lines+=['| '+' | '.join(row)+' |' for row in s['rows']]
        display=[' / '.join(row) for row in s['rows']]
    else:
        lines += ['- **'+a+'** — '+b for a,b in s['items']]
        display=[a+': '+b for a,b in s['items']]
    if s['image']:lines+=['',f'Ảnh minh họa: `shots/current/{s["image"]}`.']
    if s['foot']:lines+=['',f'Ghi chú hiển thị: {s["foot"]}']
    lines+=['','**Lời thuyết trình:**','',s['notes'],'']
    if s.get('explanation'):
        lines+=['**Giải thích chi tiết để chuẩn bị/hỏi đáp — không đọc hết trong 15 phút:**','',s['explanation'],'']
    lines+=['**Căn cứ:** '+ '; '.join(f'[{u}]({u})' if u.startswith('https://') else f'`{u}`' for u in s['sources']), '']
    if i<len(MAIN):lines+=['**Chuyển ý:** '+f'Từ nội dung này, chuyển sang: {MAIN[i]["title"].lower()}.','']
    extra='<h3>Chi tiết để chuẩn bị/hỏi đáp</h3><p>'+html.escape(s['explanation'])+'</p>' if s.get('explanation') else ''
    htmlparts.append('<section><small>'+('PHỤ LỤC' if s['backup'] else f'SLIDE {i} · {s["seconds"]} GIÂY')+'</small><h2>'+html.escape(s['title'])+'</h2><p class="key">'+html.escape(s['takeaway'])+'</p><ul>'+''.join('<li>'+html.escape(v)+'</li>' for v in display)+'</ul><h3>Lời thuyết trình</h3><p>'+html.escape(s['notes'])+'</p>'+extra+'<p class="refs">Căn cứ: '+ '; '.join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' if u.startswith('https://') else html.escape(u) for u in s['sources'])+'</p></section>')
lines+=['## Chuẩn bị và trình diễn','','1. Mở slide, bật Presenter View để thấy Notes; dùng bản PDF nếu thiếu PowerPoint.',
 '2. Mở https://proxyllm.store, kiểm ba trợ lý, nhãn giả lập, kho nguồn; không nhập thông tin cá nhân thật.',
 '3. Chuẩn bị đúng một câu liên lĩnh vực. Câu nhập tay/gợi ý gọi API mới và có phí; không bấm nhiều lần.',
 '4. Giới hạn giới thiệu demo ở 1:20; nếu chưa xong thì tiếp tục slide. Dùng phụ lục ảnh kết quả và công khai đó là lượt đã lưu.',
 '5. Không mở file chứa khóa/mật khẩu trên màn hình chiếu. Trang cài đặt vẫn yêu cầu mật khẩu riêng.',
 '6. Phần hỏi đáp ngoài 15 phút có thể mở phụ lục cấu hình local, phép tính chi phí và chính sách dữ liệu.','',
 '## Giải thích mức tin cậy','','- **Đã có/đã đo:** code, inventory public domain và các bản ghi/tệp test đã được kiểm tra trong phiên này hoặc phiên trước, ghi rõ phạm vi.',
 '- **Giá tham khảo:** nguồn chính thức có ngày; không thay báo giá/hóa đơn của nhà cung cấp hoặc cổng trung gian.',
 '- **Giá local:** bốn GPU Max-Q 96GB cộng giá niêm yết gần 2 tỷ; tổng máy/hạ tầng chờ báo giá. Chi vận hành khoảng 354 triệu/năm là kịch bản giả định, chưa khấu hao và phát triển. Không còn điểm hòa vốn local chưa kiểm chứng.',
 '- **Đề xuất pilot:** phân quyền, policy local-only, phục hồi, lịch 12 tuần và ngưỡng nghiệm thu; chưa phải toàn bộ đã triển khai.']
(HERE/'NOI_DUNG_CHI_TIET_15P.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
shutil.copy2(HERE/'NOI_DUNG_CHI_TIET_15P.md',HERE/'KICH_BAN_TRINH_BAY.md')
style='body{font-family:"Segoe UI",sans-serif;background:#f6f7f9;color:#20334d;max-width:1000px;margin:auto;padding:40px;line-height:1.7}section{background:white;border:1px solid #dce4ed;padding:30px;margin:22px 0;border-radius:12px}h1,h2{line-height:1.3}h2{font-size:25px}h3{font-size:16px;color:#245bba}.key{font-size:18px;color:#526983}small,.refs{color:#76859a}.refs{font-size:11px;overflow-wrap:anywhere}a{color:#245bba}@media print{body{padding:0;background:white}section{break-before:page;border:0;margin:0}a{color:inherit}}'
(HERE/'NOI_DUNG_CHI_TIET_15P.html').write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><title>Credere — nội dung 15 phút</title><style>'+style+'</style><h1>Credere — nội dung chi tiết 15 phút</h1><p>15 slide chính + 8 phụ lục. Thuyết trình, giá tham khảo và kế hoạch bảo mật theo yeucauslide.txt. Cập nhật 29/09/2026.</p>'+''.join(htmlparts)+'</html>',encoding='utf-8')
reqtext=['# Đối chiếu yeucauslide.txt','','Nguồn yêu cầu: `presentation/yeucauslide.txt`. Đã ánh xạ đủ 6 nhóm ý trong 5 dòng gốc.','', '| Mã | Yêu cầu | Slide chính | Phụ lục |','| --- | --- | --- | --- |']
for k,v in REQS.items():reqtext.append(f'| {k} | {v} | '+', '.join(str(n) for n in mapping[k] if n<=15)+' | '+', '.join(str(n) for n in mapping[k] if n>15)+' |')
reqtext+=['','**Kiểm tra:** mọi nhóm đều có slide chính; tổng thời lượng 900 giây. Chi tiết lời nói có trong Notes và NOI_DUNG_CHI_TIET_15P.md.']
assert all(any(n<=15 for n in mapping[k]) for k in REQS)
(HERE/'DOI_CHIEU_YEU_CAU.md').write_text('\n'.join(reqtext)+'\n',encoding='utf-8')
sources=sorted(set(u for s in DECK for u in s['sources']))
source_lines=['# Nguồn tham khảo cho bộ slide 15 phút','','Kiểm tra 29/09/2026; giá và chính sách có thể thay đổi. Số liệu nội bộ đã có chứng cứ ở CONTENT_FACTS.json.','']
source_lines+=['- '+(f'[{u}]({u})' if u.startswith('https://') else f'`{u}`') for u in sources]
source_lines+=['','Không dùng khẳng định local luôn đắt/rẻ hơn API hoặc chất lượng tương đương khi chưa đo. Giá GPU là niêm yết từng card kèm build PC; toàn máy, hạ tầng và tổng năm đầu chờ báo giá. Chi vận hành là kịch bản giả định có công thức, không phải hóa đơn đã phát sinh.']
(HERE/'NGUON_THAM_KHAO.md').write_text('\n'.join(source_lines)+'\n',encoding='utf-8')
review={'pptx':f'{NAME}.pptx','main':15,'appendix':8,'seconds':900,'requirement_mapping':mapping,'slides':DECK}
(HERE/'review_15p.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {NAME}.pptx: 15 main slides / 900 seconds + 8 optional appendix slides; all requirement groups covered.')
