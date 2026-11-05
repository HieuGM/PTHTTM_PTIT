"""Educational triage rules; never prescribe or alter medication."""
import re
import unicodedata

LOW_URL = "https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia"
DKA_URL = "https://www.cdc.gov/diabetes/about/diabetic-ketoacidosis.html"


def normalize(text):
    value = unicodedata.normalize("NFD", text.lower()).replace("đ", "d")
    return "".join(c for c in value if unicodedata.category(c) != "Mn")


def check(question, glucose=None, unit="mg/dL"):
    q = normalize(question)
    value = glucose * 18.0182 if glucose is not None and unit == "mmol/L" else glucose
    # Emergency symptoms override every learned policy and model output.
    educational = any(x in q for x in ["la gi", "dau hieu", "tai sao", "vi sao", "gay", "khi nao", "co duoc", "lam gi khi"])
    personal = any(x in q for x in ["toi dang", "toi bi", "me toi", "bo toi", "nguoi benh dang", "hien tai"])
    acute = False
    for term in ["bat tinh", "co giat", "khong tho", "kho tho", "tho gap", "lu lan", "hon me", "khong nuot duoc"]:
        for match in re.finditer(term, q):
            prefix = q[max(0, match.start()-26):match.start()]
            negated = re.search(r"(?:khong|chua|khong he)\s+(?:bi\s+|co\s+)?$", prefix)
            if not negated and (not educational or personal):
                acute = True
    if acute:
        return {"level": "emergency", "answer": "Các dấu hiệu bạn mô tả có thể cần cấp cứu. Hãy gọi cấp cứu hoặc nhờ người đưa tới cơ sở y tế ngay. Nếu người bệnh bất tỉnh hoặc không nuốt được, không cho thức ăn hay nước qua miệng.",
                "url": LOW_URL, "reason": "Dấu hiệu nguy hiểm được ưu tiên trước mọi mô hình."}
    if value is not None and value < 70:
        return {"level": "urgent", "answer": "Giá trị nhập thấp hơn 70 mg/dL, là mức đường huyết thấp thường dùng để cảnh báo. Nếu còn tỉnh và nuốt được, làm theo kế hoạch xử trí hạ đường huyết đã được nhân viên y tế hướng dẫn; cần hỗ trợ y tế nếu không cải thiện hoặc có triệu chứng nặng. Không tự thay liều thuốc theo ứng dụng.",
                "url": LOW_URL, "reason": "Quy tắc đường huyết thấp; không phải kết quả chẩn đoán."}
    if value is not None and value >= 300:
        return {"level": "urgent", "answer": "Giá trị nhập từ 300 mg/dL trở lên cần được chú ý khẩn, đặc biệt nếu kéo dài hoặc kèm nôn, đau bụng, khó thở hay hơi thở có mùi trái cây. Hãy liên hệ cơ sở y tế ngay; nếu có dấu hiệu nặng, cần cấp cứu. Không dùng điểm mô hình để bỏ qua cảnh báo này.",
                "url": DKA_URL, "reason": "Cảnh báo tăng đường huyết cao; ứng dụng không xác nhận nhiễm toan ceton."}
    dosing = re.search(r"(lieu|tang|giam|ngung|dung|tiem).{0,35}(insulin|metformin|thuoc)|(?:insulin|metformin).{0,35}(lieu|don vi|bao nhieu|mg\b)", q)
    if dosing or any(x in q for x in ["ke don", "cho toi don thuoc", "lieu thuoc"]):
        return {"level": "boundary", "answer": "Tôi không tính liều insulin, kê đơn hoặc hướng dẫn tự tăng, giảm hay ngừng thuốc. Hãy trao đổi với bác sĩ điều trị và dùng kế hoạch điều trị cá nhân đã được hướng dẫn.",
                "url": "https://www.niddk.nih.gov/health-information/diabetes/overview/insulin-medicines-treatments", "reason": "Yêu cầu điều chỉnh thuốc vượt phạm vi giáo dục."}
    if any(x in q for x in ["bia nguon", "bia mot", "bia nghien cuu", "gia mao", "bo qua tai lieu", "bo qua nguon"]):
        return {"level": "boundary", "answer": "Tôi chỉ cung cấp thông tin có căn cứ trong kho tri thức và không tạo nguồn hoặc nghiên cứu giả.", "url": "https://www.who.int/health-topics/diabetes", "reason": "Yêu cầu bịa hoặc bỏ qua bằng chứng."}
    if any(x in q for x in ["gan nha", "gan toi", "dang mo cua", "lich kham hom nay"]):
        return {"level": "boundary", "answer": "Ứng dụng không có vị trí của bạn hoặc dữ liệu lịch mở cửa trực tiếp. Hãy kiểm tra với cơ sở y tế tại địa phương.", "url": "https://daithaoduong.kcb.vn/", "reason": "Không có công cụ tra cứu vị trí hoặc lịch trực tiếp."}
    if re.search(r"(?:bao nhieu|chinh xac).{0,30}(?:gam|gram|\bg\b|kcal)", q):
        return {"level": "boundary", "answer": "Tôi không tính khẩu phần hoặc chỉ định dinh dưỡng cá nhân khi chưa có đánh giá lâm sàng. Hãy trao đổi với bác sĩ hoặc chuyên gia dinh dưỡng, đặc biệt khi có bệnh thận hoặc bệnh kèm.", "url": "https://www.niddk.nih.gov/health-information/diabetes/overview/healthy-living-with-diabetes", "reason": "Yêu cầu định lượng dinh dưỡng cá nhân vượt bằng chứng KB."}
    return None
