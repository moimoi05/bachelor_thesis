"""Illustrate preprocessing with the same MRI slice used in the input figure."""
from PIL import Image
from academic_style import S, MRI, TEMPORAL, PALE, arrow, box, line, save, scene, text

ASSET = S / 'figures_source/assets/mri_t1_three_planes.png'


def slice_at(ax, image, x, y, size, angle=0):
    tile = ax.inset_axes([x, y, size, size * ax.figure.get_figwidth() / ax.figure.get_figheight()])
    tile.imshow(image.rotate(angle, resample=Image.Resampling.BILINEAR), cmap='gray')
    tile.axis('off')


def overview(image):
    fig, ax = scene(7.2, 2.25)
    slice_at(ax, image, .020, .38, .132)
    text(ax, .087, .27, 'MRI T1\nBa lần khám', 10)
    for x, title, caption in [
        (.30, 'RAS và SynthStrip', 'Thống nhất hướng ảnh\nvà tách vùng não'),
        (.56, 'Đăng ký cứng', 'Lần 2, 3 về lần 1\nLần 1 về mẫu MNI'),
        (.84, 'Lấy mẫu và z-score', 'Lưới 144 × 144 × 144\nVoxel 1,5 mm mỗi trục'),
    ]:
        box(ax, x, .63, .230, .22, title, MRI, 10)
        text(ax, x, .35, caption, 9)
    for x1, x2 in [(.153, .183), (.417, .443), (.678, .722)]:
        arrow(ax, (x1, .63), (x2, .63))
    text(ax, .84, .12, 'Ba ảnh cho bộ mã hóa', 9, 'bold')
    save(fig, 'mri-preprocessing')


def registration(image):
    fig, ax = scene(7.2, 3.15)
    for y, angle, visit in [(.56, 12, 'Lần 2'), (.10, -9, 'Lần 3')]:
        slice_at(ax, image, .06, y, .14, angle)
        text(ax, .13, y-.045, visit, 10, 'bold')
        arrow(ax, (.205, y+.16), (.408, .55 if angle > 0 else .43))
    slice_at(ax, image, .42, .33, .16)
    text(ax, .50, .24, 'Lần 1 · ảnh tham chiếu', 10, 'bold')
    text(ax, .30, .85, 'Xoay và dịch chuyển', 9)
    arrow(ax, (.59, .51), (.71, .51))
    box(ax, .85, .51, .26, .24, 'Hệ tọa độ mẫu\nMNI152NLin2009cAsym', TEMPORAL, 9)
    text(ax, .85, .27, 'Mốc chung cho cả chuỗi', 9)
    save(fig, 'mri-registration')


if __name__ == '__main__':
    with Image.open(ASSET) as asset:
        slice_image = asset.crop((97, 81, 634, 618)).convert('L')
    overview(slice_image)
    registration(slice_image)
