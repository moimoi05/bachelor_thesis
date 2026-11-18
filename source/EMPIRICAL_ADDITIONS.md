# Bổ sung thực nghiệm ngày 2026-11-14

## Tái tạo số liệu

Dùng Python có numpy, pandas, scipy, matplotlib, scikit-survival, lifelines, pyreadr. Hai script chỉ đọc dữ liệu nguồn, không huấn luyện hoặc cập nhật checkpoint:

```
python figures_source/build_characteristics.py
python figures_source/build_empirical.py
```

Các đường dẫn dữ liệu gốc nằm trong script và các tệp `evidence/*provenance.json`. Script thực nghiệm sử dụng trực tiếp `alzheimer_training/scripts/analyze_rc_free_survival.py` để đối chiếu AUC và xác minh dự đoán. Máy không có dữ liệu ADNI vẫn biên dịch được PDF từ bảng/hình đóng gói. Gói không chứa dữ liệu cá thể ADNI.

## Quy ước

- Đặc điểm tại MRI đầu s1; dùng điểm lâm sàng thô ghép bởi pipeline, không điền thiếu. Có 132 MMSE và 131 CDR hợp lệ. Mỗi ô ghi n quan sát nếu thiếu.
- Tuổi tính từ tháng/năm sinh PTDEMOG, lấy ngày 15; nhân khẩu học dùng bản ghi hợp lệ gần nhất không sau s1. Kiểm định so sánh ba tập tổng thể, không so sánh sáu nhóm kết cục với nhau.
- ROC: định nghĩa cumulative/dynamic, trọng số kiểm duyệt fit trên train, cắt nhãn tại nextafter(h,+inf). Kiểm tra từng AUC với pipeline gốc và mean/SD với bảng báo cáo. SD mẫu dùng ddof=1.
- ROC trung bình dùng nội suy trên 1001 điểm FPR; không dùng diện tích đường nội suy thay AUC thực nghiệm. Các điểm ngưỡng và đường bậc thang gốc được giữ.
- Huấn luyện: trung bình loss của batch hợp lệ; val loss toàn tập dùng trục riêng. Chỉ có val C-index theo epoch. Dấu sao là checkpoint, hình vuông là vòng dừng; không kéo dài lịch sử seed đã dừng.
- Lưu checkpoint theo cải thiện C-index bất kỳ, trong khi dừng sớm dùng min_delta=0.002; đây là hai điều kiện riêng trong trainer.

## Kiểm tra đã thực hiện

- 359 RID, 1077 MRI, mỗi RID đúng một tập; N train/val/test = 251/54/54, biến cố 74/16/16.
- Đối chiếu nhãn và ngày kết cục bằng pipeline gốc; xác minh checksum checkpoint theo báo cáo gốc.
- 18 AUC thực nghiệm trùng hàm tham chiếu (sai số tuyệt đối dưới 1e-12); sáu mean/SD khớp bảng với sai số dưới 1e-10.
- Best epoch 16/7/25; stop epoch 36/30/30; C-index checkpoint khớp báo cáo gốc.
- Bảng đặc điểm, hình ROC, hình huấn luyện và sơ đồ hai bài báo đã kiểm tra trực quan trong PDF.
