# Biên dịch và dựng lại hình

Chạy từ thư mục `source/`:

```bash
THESIS_TECTONIC=/path/to/tectonic bash build.sh
```

Trên Windows, dùng `build.ps1 -TectonicPath C:\path\tectonic.exe`.
Nếu không dùng Tectonic: XeLaTeX, BibTeX, rồi XeLaTeX ít nhất hai lượt cho
đến khi mục lục và tham chiếu ổn định. Các hình PDF và bảng đã được đóng gói,
nên không cần chạy mã dựng hình để biên dịch; không cần GPU hay huấn luyện lại.

## Dựng lại bộ hình

Từ thư mục `source/`, dùng Python 3.12 có `numpy`, `pandas`,
`matplotlib`, `Pillow`, `PyMuPDF` và draw.io Desktop. Có thể đặt biến
môi trường `THESIS_DRAWIO` thay cho đối số `--drawio`.

```powershell
python figures_source/export_architecture.py --drawio C:\path\draw.io.exe
python figures_source/render_revision.py
python figures_source/build_explanatory.py
python figures_source/build_cp_concept.py
python figures_source/render_empirical.py
python figures_source/build_survival.py --km-only
```

Các lệnh trên đọc tài sản và bằng chứng trong gói. Chế độ `--km-only`
chỉ xuất Hình 4.3. `build_empirical.py` và chế độ dựng bảng của
`build_survival.py` được giữ lại để tra cứu quy trình lượt 8.

Tectonic có thể tải gói TeX khi chạy lần đầu nếu bộ nhớ đệm chưa có.

## Đầu ra

PDF đầu ra ở thư mục cha: `Nguyen_Phuong_Nam_Thesis_UET.pdf`.
Các hình PDF vector, SVG và PNG 300 DPI được lưu trong `image/`;
`academic_style.py` chứa quy chuẩn thiết kế dùng chung.
Cài Python với `numpy`, `pandas`, `matplotlib` và `Pillow` khi cần dựng hình.
`build_survival.py` đồng thời dựng bảng từ dữ liệu bằng chứng tổng hợp.

Kiểm tra log và chạy lại nếu công cụ còn báo tham chiếu cần cập nhật.
Sau build, dùng PyMuPDF hoặc Poppler để render các trang có hình và công thức.
Ký hiệu lambda toán học của `newtxmath` được trích xuất thành `𝜆` (U+1D706),
trong khi hình có thể dùng `λ` (U+03BB); cần nhận diện cả hai khi kiểm tra.

## Đối chiếu phát hành

```powershell
python figures_source/check_release.py --pdf main.pdf --render C:\path\thesis-qa
```

Kiểm tra bao gồm 21 hình và liên kết danh mục hình, hướng trang phụ lục và định dạng xuất.
