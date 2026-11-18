# Nguồn khóa luận

Nguồn LaTeX của bản PDF phát hành. Bằng chứng thực nghiệm tổng hợp nằm trong `evidence/`.

Biên dịch trong thư mục này:

```bash
THESIS_TECTONIC=/path/to/tectonic bash build.sh
```

Có thể dùng XeLaTeX/BibTeX nếu không cài Tectonic. Xem `COMPILE.md`.
Không cần GPU, checkpoint hoặc dữ liệu bệnh nhân để biên dịch.

Bộ hình đã đánh số gồm 21 hình, với PDF để nhúng, SVG có chữ chỉnh sửa
được và PNG 300 dpi. Xem lệnh dựng lại hình trong `COMPILE.md`. Hai sơ đồ tổng thể 3.1 và
A.1 có thêm tệp nguồn `.drawio`. Hình AUC tổng hợp ngoài bản in được lưu
để tham khảo.

Thuật toán 1 nằm trong `algorithms/rcfree_forward.tex`, được chèn sau mục 3.11. Môi trường algorithm dùng gói float sẵn có, không cần cài thêm gói thuật toán.

Các hình giải thích mới ở Chương 2–3 được dựng bằng `python figures_source/build_explanatory.py`. Bảng nhóm radiomics và bảng chín biến lâm sàng nằm trong `tables/`; danh sách đủ 107 tên đặc trưng nằm trong `evidence/radiomics_feature_inventory.csv` (chỉ có tên, không có số đo cá nhân).

Quy chuẩn màu và bố cục: `figures_source/DESIGN_SYSTEM.md`. Các sơ đồ dùng chung `academic_style.py`; PDF vector và PNG 300 DPI có đệm 0,15 inch. Dùng Python 3.12+ cùng numpy, pandas, matplotlib; PyMuPDF và Pillow chỉ cần cho kiểm tra artefact.
