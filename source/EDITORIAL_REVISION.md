# Chỉnh sửa văn bản và hình sau phản biện — lượt 8

## Thay đổi

- Mục 3.2.3: truy nguyên việc chỉ có 132 MMSE và 131 CDR tại MRI đầu. Có 227 người không có bản ghi trong cửa sổ ±90 ngày; CDR có thêm một bản ghi giá trị không hợp lệ. Ở nhóm thiếu, bản ghi hợp lệ gần nhất cách MRI đầu trung vị 102 ngày. Các số đếm được tái tạo từ bảng nguồn và quy tắc hợp lệ/ghép gốc.
- Mục 4.1: sampler tạo cặp so sánh Cox; 96 vòng của ba seed có 4.032 lô hợp lệ và 0 lô không hợp lệ. Tách nhận xét thang đo loss khỏi xu hướng loss xác thực tăng về cuối và nguy cơ quá khớp. Chưa có đối chứng xác định nguyên nhân do cỡ lô.
- Mục 3.4 và 4.2: đối chiếu PCA 38/69/2 chiều với C-index 0.6625/0.7708/0.7917. Seed hai chiều có C-index cao nhất trong ba seed của baseline.
- Gọt các phủ định hiển nhiên ở phần khái niệm, công thức và chú thích; giữ các phân biệt có ý nghĩa về thời gian, RC-Free và phạm vi đối chứng.
- Hình CP ở Chương 2 được vẽ tổng quát; hình cấu hình MR ở Chương 3 giữ riêng.
- Sơ đồ tổng hợp chuyển thành Hình A.1 trong Phụ lục A, có mục lục và danh mục hình.
- Hình KM có hai panel xác thực/kiểm tra hậu nghiệm, CI 95%, dấu kiểm duyệt và bảng nguy cơ; dữ liệu được kiểm tra với bảng thống kê gốc.
- Mục 3.12.3 dùng công thức AUC theo tổng cặp có trọng số, nêu rõ triệt tiêu trọng số đối chứng chung và quy ước đồng điểm; phần chặn phải h+epsilon được rút gọn.

## Tái tạo và kiểm tra

Chạy tại `source/` trong môi trường phân tích đã mô tả ở `EMPIRICAL_ADDITIONS.md`:

```bash
python figures_source/audit_editorial_evidence.py
python figures_source/verify_ipcw_formula.py
python figures_source/build_cp_concept.py
python figures_source/build_survival.py
THESIS_TECTONIC=/path/to/tectonic bash build.sh
```

Hai script đầu cần truy cập dữ liệu gốc tại các đường dẫn được lưu trong mã. Các đầu ra kiểm toán chỉ chứa số liệu tổng hợp và thông tin nguồn, không chứa RID cá thể. Hai script hình dùng tài sản đóng gói. Việc biên dịch LaTeX dùng được trên máy không có dữ liệu ADNI.

`evidence/editorial_audit.json` lưu số đếm, thông tin sampler, PCA và checksum nguồn. `evidence/ipcw_formula_checks.json` ghi 22 đối chiếu với pipeline: 18 kết quả thực nghiệm cùng các tình huống đồng điểm, kiểm duyệt/biến cố đúng mốc và thời gian vượt hỗ trợ huấn luyện; sai số tối đa 2.22e-16.

Không đổi nhãn, checkpoint hay kết quả thực nghiệm gốc. Bản PDF và gói nguồn trước chỉnh sửa được lưu ở `qa/editorial_revision/before_revision*` ngoài gói nguồn bàn giao.
