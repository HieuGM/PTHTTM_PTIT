"""Input fields, coding and Vietnamese labels for the two independent tasks."""


def spec(name, label, low, high, default, integer=True, coding=None):
    item = dict(name=name, label=label, min=low, max=high,
                default=default, integer=integer)
    if coding:
        item['coding'] = coding
    return item


YES_NO = '0 = Không; 1 = Có'
CDC = [
    spec('HighBP', 'Đã được thông báo huyết áp cao', 0, 1, 0, coding=YES_NO),
    spec('HighChol', 'Đã được thông báo cholesterol cao', 0, 1, 0, coding=YES_NO),
    spec('CholCheck', 'Kiểm tra cholesterol trong 5 năm', 0, 1, 1, coding=YES_NO),
    spec('BMI', 'BMI (kg/m²)', 12, 98, 25, integer=False),
    spec('Smoker', 'Đã hút ít nhất 100 điếu thuốc', 0, 1, 0, coding=YES_NO),
    spec('Stroke', 'Tiền sử đột quỵ', 0, 1, 0, coding=YES_NO),
    spec('HeartDiseaseorAttack', 'Tiền sử bệnh tim hoặc nhồi máu', 0, 1, 0, coding=YES_NO),
    spec('PhysActivity', 'Vận động trong 30 ngày', 0, 1, 1, coding=YES_NO),
    spec('Fruits', 'Ăn trái cây mỗi ngày', 0, 1, 1, coding=YES_NO),
    spec('Veggies', 'Ăn rau mỗi ngày', 0, 1, 1, coding=YES_NO),
    spec('HvyAlcoholConsump', 'Uống rượu nhiều theo mã BRFSS', 0, 1, 0,
         coding='0 = Không; 1 = Nam >14 ly/tuần, nữ >7 ly/tuần theo khảo sát'),
    spec('AnyHealthcare', 'Có bảo hiểm/quyền tiếp cận y tế', 0, 1, 1, coding=YES_NO),
    spec('NoDocbcCost', 'Không đi khám vì chi phí trong 12 tháng', 0, 1, 0, coding=YES_NO),
    spec('GenHlth', 'Tự đánh giá sức khỏe', 1, 5, 3,
         coding='1 = Xuất sắc; 2 = Rất tốt; 3 = Tốt; 4 = Trung bình; 5 = Kém'),
    spec('MentHlth', 'Số ngày sức khỏe tinh thần kém / 30 ngày', 0, 30, 0),
    spec('PhysHlth', 'Số ngày sức khỏe thể chất kém / 30 ngày', 0, 30, 0),
    spec('DiffWalk', 'Khó đi bộ hoặc leo cầu thang', 0, 1, 0, coding=YES_NO),
    spec('Sex', 'Giới tính theo mã bộ dữ liệu', 0, 1, 1, coding='0 = Nữ; 1 = Nam'),
    spec('Age', 'Nhóm tuổi BRFSS', 1, 13, 7,
         coding='1:18–24; 2:25–29; 3:30–34; 4:35–39; 5:40–44; 6:45–49; '
                '7:50–54; 8:55–59; 9:60–64; 10:65–69; 11:70–74; 12:75–79; 13:≥80'),
    spec('Education', 'Trình độ học vấn theo mã khảo sát Mỹ', 1, 6, 4,
         coding='1: Chưa học; 2: Lớp 1–8; 3: Lớp 9–11; 4: Tốt nghiệp phổ thông; '
                '5: Học cao đẳng/đại học chưa tốt nghiệp; 6: Tốt nghiệp cao đẳng/đại học'),
    spec('Income', 'Nhóm thu nhập hộ/năm (USD, Mỹ 2015)', 1, 8, 5,
         coding='1:<10k; 2:10–15k; 3:15–20k; 4:20–25k; 5:25–35k; '
                '6:35–50k; 7:50–75k; 8:≥75k. Không quy đổi từ VND để áp dụng lâm sàng.'),
]
HOSPITAL = [
    spec('time_in_hospital', 'Số ngày nằm viện', 1, 14, 4),
    spec('num_lab_procedures', 'Số xét nghiệm trong đợt nằm viện', 1, 132, 40),
    spec('num_procedures', 'Số thủ thuật khác', 0, 6, 1),
    spec('num_medications', 'Số thuốc khác nhau trong đợt nằm viện', 1, 81, 15),
    spec('number_outpatient', 'Số lần ngoại trú trong năm trước', 0, 42, 0),
    spec('number_emergency', 'Số lần cấp cứu trong năm trước', 0, 76, 0),
    spec('number_inpatient', 'Số lần nội trú trong năm trước', 0, 21, 0),
    spec('number_diagnoses', 'Số chẩn đoán trong hồ sơ', 1, 16, 7),
    spec('AgeGroup', 'Nhóm tuổi lúc nhập viện', 1, 10, 6,
         coding='1:0–9; 2:10–19; 3:20–29; 4:30–39; 5:40–49; '
                '6:50–59; 7:60–69; 8:70–79; 9:80–89; 10:90–99'),
    spec('Gender', 'Giới tính theo mã hồ sơ', 0, 1, 1, coding='0 = Female; 1 = Male'),
]
SCHEMAS = {'cdc': CDC, 'hospital': HOSPITAL}
TASKS = {
    'cdc': 'Phân loại nhãn tự khai báo đái tháo đường/tiền đái tháo đường trong BRFSS 2015',
    'hospital': 'Phân loại tái nhập viện dưới 30 ngày trong hồ sơ nội trú có đái tháo đường',
}
LABELS = {
    'cdc': '1 = diabetes hoặc prediabetes gộp theo bản CDC binary; 0 = không có nhãn đó',
    'hospital': '1 = readmitted <30 ngày; 0 = >30 ngày hoặc NO trong bộ dữ liệu',
}
