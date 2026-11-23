"""Round 8: reproducible academic vector diagrams, with unchanged scientific content."""
import json
from academic_style import *
from matplotlib.image import imread
def emit(fig, name):
    save(fig, name)

def timeline():
    fig, ax = scene(w=6.3, h=2.15)
    baseline, first_scan, second_scan, last_scan, landmark, outcome = (
        .075, .225, .390, .555, .730, .895
    )
    axis_y = .535
    ax.add_patch(Rectangle((baseline, .455), landmark-baseline, .16,
                           facecolor=MRI, edgecolor='none', zorder=0))
    arrow(ax, (.039, axis_y), (.966, axis_y), lw=1.05)
    for x, symbol, label, fill in [
        (baseline, r'$b$', 'Ban đầu', 'white'),
        (first_scan, r'$s_1$', 'MRI 1', MRI),
        (second_scan, r'$s_2$', 'MRI 2', MRI),
        (last_scan, r'$p=s_3$', 'MRI cuối', MRI),
        (landmark, r'$L$', 'Mốc chọn mẫu', ORANGE),
        (outcome, r'$o$', 'Biến cố hoặc\nkiểm duyệt', ORANGE),
    ]:
        marker = 's' if x in (landmark, outcome) else 'o'
        ax.plot(x, axis_y, marker=marker, ms=5, mew=.9,
                mec=NAVY, mfc=fill, zorder=3)
        text(ax, x, .413, symbol, 11)
        text(ax, x, .322, label, 9.5, va='top')

    for x in (baseline, landmark):
        line(ax, (x, .615), (x, .820), lw=.55, ls=':')
    arrow(ax, (baseline, .820), (landmark, .820), style='<->', lw=.9)
    text(ax, (baseline+landmark)/2, .945,
         r'Cửa sổ chọn MRI 18 tháng $[b,L]$', 11, 'bold')
    text(ax, landmark-.115, .694,
         r'Chưa tiến triển đến $L$', 9.5)
    arrow(ax, (last_scan, .135), (outcome, .135), style='<->', lw=.9)
    text(ax, (last_scan+outcome)/2, .034, r'Theo dõi: $t=(o-p)/365.25$ năm', 10)
    emit(fig, 'mci-progression-timeline')


def cohort():
    fig, ax = scene(w=6.3, h=5.60)
    rows = [
        (899, 'Có MRI và liên kết định danh'),
        (843, 'MCI ở lần khám ban đầu'),
        (631, 'Chưa tiến triển đến mốc $L$'),
        (536, 'Có theo dõi hợp lệ sau $L$'),
        (359, 'Đủ ba thời điểm MRI'),
    ]
    exclusions = [
        (56, 'Không đạt tiêu chí MCI'),
        (212, 'Tiến triển tại hoặc trước $L$'),
        (95, 'Thiếu theo dõi sau $L$'),
        (177, 'Chưa đủ ba thời điểm MRI'),
    ]
    text(ax, .035, .957, 'Sàng lọc người tham gia', 11, 'bold', ha='left')
    text(ax, .615, .957, 'Loại khỏi nghiên cứu', 11, 'bold', ha='left')
    line(ax, (.035, .920), (.963, .920), NAVY, .75)

    left, right, center, row_height = .035, .548, .292, .054
    for index, (count, label) in enumerate(rows):
        y = .881 - index*.132
        ax.add_patch(Rectangle((left, y-row_height/2), right-left, row_height,
                               facecolor=RADIOMICS if index == len(rows) - 1 else TEMPORAL,
                               edgecolor=NAVY, lw=.7, zorder=2))
        text(ax, .093, y, str(count), 11, 'bold')
        text(ax, .155, y, label, 10, ha='left')
        if index == len(exclusions):
            continue
        branch_y = y - .066
        arrow(ax, (center, y-row_height/2), (center, y-.132+row_height/2),
              lw=.95)
        ax.plot(center, branch_y, 'o', ms=2.8, color=INK, zorder=3)
        arrow(ax, (center, branch_y), (.607, branch_y), lw=.85)
        removed, reason = exclusions[index]
        text(ax, .650, branch_y, str(removed), 10, 'bold')
        text(ax, .700, branch_y, reason, 9.5, ha='left')

    arrow(ax, (center, .326), (center, .285), lw=.95)
    text(ax, .5, .252, '1077 lần khám  ·  106 biến cố  ·  253 kiểm duyệt',
         10.5, 'bold')
    line(ax, (.035, .218), (.963, .218), NAVY, .75)
    text(ax, .035, .187, 'Chuẩn bị dữ liệu', 11, 'bold', ha='left')
    stages = [
        (.150, .230, 'Ghép ba nguồn\n theo lần khám', FUSION),
        (.498, .354, 'Chia tập theo RID\nHuấn luyện 251  ·  Xác thực 54\nKiểm tra (hậu nghiệm) 54', SURVIVAL),
        (.847, .230, 'Tiền xử lý dựa trên\n tập huấn luyện', CLINICAL),
    ]
    for x, width, label, fill in stages:
        box(ax, x, .083, width, .128, label, fill, 9.5)
    for a, b in ((.265, .321), (.675, .732)):
        arrow(ax, (a, .083), (b, .083), lw=.9)
    emit(fig, 'cohort-construction')


def outer():
    fig, ax = scene(w=6.3, h=2.72)
    text(ax, .033, .943, '(a) Tích ngoài MRI–radiomics', 11, 'bold', ha='left')
    text(ax, .594, .943, '(b) Biểu diễn tương tác', 11, 'bold', ha='left')
    line(ax, (.032, .891), (.495, .891), NAVY, .75)
    line(ax, (.594, .891), (.966, .891), NAVY, .75)

    box(ax, .316, .764, .315, .121, r'$y^\top$ (radiomics), $1\times32$',
        RADIOMICS, 10)
    box(ax, .079, .486, .131, .234, r'$x$'+'\nMRI\n'+r'$32\times1$', MRI, 9.5)
    arrow(ax, (.316, .7035), (.316, .630), lw=.95)
    arrow(ax, (.1445, .486), (.184, .486), lw=.95)

    ax.add_patch(Rectangle((.184, .339), .274, .291, facecolor=FUSION,
                           edgecolor=NAVY, lw=.7, zorder=2))
    rows = [
        (r'$x_1y_1$', r'$\cdots$', r'$x_1y_{32}$'),
        (r'$\vdots$', r'$\ddots$', r'$\vdots$'),
        (r'$x_{32}y_1$', r'$\cdots$', r'$x_{32}y_{32}$'),
    ]
    for y, row in zip((.582, .486, .390), rows):
        for x, cell in zip((.232, .319, .410), row):
            text(ax, x, y, cell, 10)
    text(ax, .320, .245, r'$xy^\top\in\mathbb{R}^{32\times32}$', 11)

    arrow(ax, (.458, .486), (.6105, .486), lw=.95)
    text(ax, .531, .550, 'Trải phẳng', 9.5)
    box(ax, .787, .486, .353, .175,
        r'$v=\mathrm{vec}(xy^\top)$', FUSION, 11)
    arrow(ax, (.787, .3985), (.787, .3065), lw=.95)
    box(ax, .787, .219, .353, .175, 'MLP\n1024 → 128 → 64', FUSION, 11)
    arrow(ax, (.787, .1315), (.787, .070), lw=.95)
    text(ax, .787, .018, r'$E_{\mathrm{MR}}\in\mathbb{R}^{64}$', 10.5)
    emit(fig, 'mr-outer-product')


def pair_routes():
    fig, ax = scene(7.4, 3.2)
    for x, pair, left, right in [
        (.17, 'MR · 64 chiều', ('MRI', 128, MRI), ('Radiomics', 64, RADIOMICS)),
        (.50, 'MC · 64 chiều', ('MRI', 128, MRI), ('Lâm sàng', 64, CLINICAL)),
        (.83, 'RC · 32 chiều', ('Radiomics', 64, RADIOMICS), ('Lâm sàng', 64, CLINICAL)),
    ]:
        box(ax, x, .83, .25, .14, pair, FUSION, 10)
        for offset, (source, dims, color) in zip((-.077, .077), (left, right)):
            end = x + offset
            arrow(ax, (x, .755), (end, .61))
            box(ax, end, .50, .148, .20, f'Chiếu riêng\n{dims} chiều', PALE, 9)
            arrow(ax, (end, .39), (end, .275))
            box(ax, end, .19, .148, .15, source, color, 9)
    save(fig, 'pair-update-routes')


def cp():
    fig, ax = scene(w=6.2, h=2.04)
    ax.set_ylim(.20, 1)
    text(ax, .025, .94, '(a) Hai phép chiếu hạng 8', 10, 'bold', ha='left')
    text(ax, .50, .94, '(b) Tương tác và ánh xạ đầu ra', 10, 'bold', ha='left')
    line(ax, (.025, .864), (.975, .864), NAVY, lw=.65)
    line(ax, (.489, .235), (.489, .995), '#B1BBC5', lw=.75, ls='--')

    inputs = [
        (.68, r'$x$ · 32 chiều', r'$A^\top x$', r'$u$ · 8 chiều', MRI),
        (.36, r'$y$ · 32 chiều', r'$B^\top y$', r'$v$ · 8 chiều', RADIOMICS),
    ]
    for y, source, projection, output, fill in inputs:
        box(ax, .105, y, .16, .12, source, fill, 9)
        arrow(ax, (.185, y), (.2275, y))
        box(ax, .285, y, .115, .12, projection, FUSION, 11)
        text(ax, .355, y+.067, output, 9, ha='left')
        route(ax, [(.3425, y), (.475, y), (.534, .544 if y > .5 else .496)])

    op(ax, .555, .52, r'$\odot$', FUSION, r=.024, size=14)
    text(ax, .555, .785, 'Nhân từng\nphần tử', 9)
    text(ax, .61, .594, r'$q$', 10)
    arrow(ax, (.579, .52), (.668, .52))
    box(ax, .726, .52, .116, .15, r'$Oq+b$'+'\n128 chiều', FUSION, 9)
    arrow(ax, (.784, .52), (.825, .52))
    box(ax, .895, .52, .14, .15, 'PostMLP', FUSION, 9)
    arrow(ax, (.895, .445), (.895, .373))
    text(ax, .895, .332, r'$E_{\mathrm{MR}}$ · 64 chiều', 9)

    emit(fig, 'outer-vs-cp')


def residual():
    fig, ax = scene(w=6.3, h=2.4225)
    ax.set_ylim(0, .85)
    text(ax, .065, .798, 'Gốc', 10)
    text(ax, .065, .695, r'$U_d$', 12)
    arrow(ax, (.094, .695), (.770, .695))
    op(ax, .792, .695, r'$+$', NAVY, r=.022, size=13)
    arrow(ax, (.814, .695), (.930, .695))
    text(ax, .872, .785, 'LayerNorm', 9.5)
    text(ax, .956, .695, r'$Z_d$', 12)

    box(ax, .480, .435, .562, .139,
        r'$g=\sigma(\mathrm{MLP}[\mathrm{LN}(U_d)\parallel\widehat{E}])$', FUSION, 11)
    route(ax, [(.145, .695), (.145, .435), (.199, .435)])
    text(ax, .062, .152, r'$E_k$', 12)
    arrow(ax, (.092, .152), (.151, .152))
    box(ax, .244, .152, .186, .145, 'Chiếu + LN', FUSION, 10.5)
    arrow(ax, (.337, .152), (.398, .152))
    box(ax, .441, .152, .086, .145, r'$\widehat{E}$', FUSION, 12)
    arrow(ax, (.441, .2245), (.441, .3655))
    arrow(ax, (.484, .152), (.564, .152))
    box(ax, .649, .152, .170, .145, r'$\lambda\,g\,\widehat{E}$', FUSION, 12)
    arrow(ax, (.649, .3655), (.649, .2245))
    text(ax, .677, .297, r'$g$', 10)
    radius_y = .022 * fig.get_figwidth() * .96 / (fig.get_figheight() * .95) * .85
    route(ax, [(.734, .152), (.792, .152), (.792, .695-radius_y)])
    emit(fig, 'gated-residual-route')


def rcfree_update():
    fig, ax = scene(7.4, 3.3)
    text(ax, .15, .94, 'Tương tác theo cặp', 10, 'bold')
    text(ax, .57, .94, 'Cộng vào biểu diễn gốc', 10, 'bold')
    box(ax, .15, .69, .26, .18, 'MRI × radiomics\nCP hạng 8 · MR', FUSION, 10)
    box(ax, .15, .31, .26, .18, 'MRI × lâm sàng\nCP hạng 8 · MC', FUSION, 10)
    for start, end in [(.72, .78), (.66, .53), (.34, .47), (.28, .22)]:
        arrow(ax, (.282, start), (.435, end))
    for y, label, color in [
        (.79, 'R + phần từ MR\nLayerNorm · 64 chiều', RADIOMICS),
        (.50, 'M + phần từ MR và MC\nLayerNorm · 128 chiều', MRI),
        (.21, 'C + phần từ MC\nLayerNorm · 64 chiều', CLINICAL),
    ]:
        box(ax, .57, y, .26, .20, label, color, 9.5)
        arrow(ax, (.702, y), (.797, .50 + (y-.5)*.34))
    box(ax, .89, .50, .18, .32, 'Ghép nối\n$M_{\\mathrm{out}}, R_{\\mathrm{out}}, C_{\\mathrm{out}}$\n256 chiều', PALE, 10)
    text(ax, .5, .025, 'Mỗi mũi tên từ khối CP là một nhánh có phép chiếu, cổng và hệ số riêng.', 9)
    save(fig, 'rcfree-update')


def temporal():
    fig, ax = scene(w=6.3, h=3.7)
    text(ax, .500, .958, r'$\Delta t_t=(s_t-s_{t-1})/365.25$ năm, $t\geq2$',
         10)
    line(ax, (.031, .916), (.969, .916), NAVY, .75)

    cell_centers = (.166, .500, .834)
    for index, x in enumerate(cell_centers, 1):
        text(ax, x, .858, f'Lần khám {index}', 10.5, 'bold')
        text(ax, x-.048, .778, rf'$F_{index}$', 10)
        gap = r'$\Delta t_1=0$' if index == 1 else rf'$\Delta t_{index}$'
        text(ax, x+.064, .778, gap, 10)
        for x_input in (x-.048, x+.064):
            arrow(ax, (x_input, .744), (x_input, .642), lw=.95)
        box(ax, x, .575, .216, .128, 'T-LSTM', TEMPORAL, 11)
        arrow(ax, (x, .509), (x, .334), lw=.95)
        text(ax, x+.021, .443, rf'$h_{index}$', 10.5, ha='left')

    for index, (left, right) in enumerate(zip(cell_centers, cell_centers[1:]), 1):
        arrow(ax, (left+.108, .575), (right-.108, .575), lw=.95)
        text(ax, (left+right)/2, .642, rf'$h_{index},c_{index}$', 9.5)

    box(ax, .500, .270, .884, .119, '', TEMPORAL)
    text(ax, .410, .270, r'$z=\sum_{t\in\mathcal{V}}\alpha_t h_t$', 12.5)
    text(ax, .924, .270, r'$\mathcal{V}$: lần khám hợp lệ', 9.5, ha='right')
    arrow(ax, (.500, .209), (.500, .143), lw=.95)
    box(ax, .500, .074, .180, .130, 'Đầu Cox', SURVIVAL, 11)
    arrow(ax, (.590, .074), (.658, .074), lw=.95)
    text(ax, .685, .074, r'$\eta$ · Điểm log-nguy cơ', 10.5, ha='left')
    emit(fig, 'temporal-model')


def inputfigure(redacted=False):
    schema = json.loads((S/'figures_source/input_schema_verified.json')
                        .read_text(encoding='utf-8'))
    fig, ax = scene(w=6.3, h=5.02)
    text(ax, .034, .963, '(a) MRI T1 · Ba mặt phẳng của cùng một ảnh',
         11, 'bold', ha='left')
    line(ax, (.034, .924), (.966, .924), NAVY, .75)
    centers = (.179, .500, .821)
    if not redacted:
        asset = imread(S/'figures_source/assets/mri_t1_three_planes.png')
        # Pixel bounds of each MRI tile, excluding the source's raster image labels.
        for center, (left, right) in zip(centers, ((97, 634), (812, 1348), (1526, 2063))):
            tile = ax.inset_axes([center-.114, .605, .228, .284])
            tile.imshow(asset[81:618, left:right], interpolation='none')
            tile.set_axis_off()
    else:
        text(ax, .500, .741, 'MRI đã che trong bản kiểm tra bố cục', 10)
    for x, label in zip(centers, ('Ngang', 'Trán', 'Dọc giữa')):
        text(ax, x, .566, label, 10)
    mri_dim = schema['mri_embedding_dim']
    box(ax, .500, .510, .604, .061, f'ResNet-18 3D → {mri_dim} chiều', MRI, 10)

    radiomics = schema['radiomics']
    preprocessing = radiomics['preprocessing']
    clinical = schema['clinical']
    text(ax, .034, .431, f"(b) Radiomics · {preprocessing['raw_feature_count']} đặc trưng",
         11, 'bold', ha='left')
    text(ax, .553, .431, '(c) Lâm sàng', 11, 'bold', ha='left')
    for left, right in ((.034, .492), (.553, .966)):
        line(ax, (left, .392), (right, .392), NAVY, .75)

    group_names = {
        'shape': 'Hình dạng', 'firstorder': 'Bậc nhất', 'glcm': 'GLCM',
        'glrlm': 'GLRLM', 'glszm': 'GLSZM', 'gldm': 'GLDM', 'ngtdm': 'NGTDM',
    }
    groups = radiomics['groups']
    for index, (name, count) in enumerate(groups.items()):
        y = .357 - index*.038
        text(ax, .164, y, group_names[name], 9.5, ha='right')
        width = .236*count/max(groups.values())
        ax.add_patch(Rectangle((.182, y-.0125), width, .025, facecolor=RADIOMICS,
                               edgecolor=NAVY, lw=.55, zorder=2))
        text(ax, .192+width, y, str(count), 9.5, ha='left')
    text(ax, .262, .077,
         f"Loại {preprocessing['constant_removed']} đặc trưng hằng", 9.5)
    radiomics_flow = (f"{preprocessing['post_filter_feature_count']} → PCA "
                      f"{preprocessing['pca_components']} → MLP → {radiomics['embedding_dim']} chiều")
    box(ax, .262, .033, .458, .055, radiomics_flow, RADIOMICS, 9.5)

    text(ax, .760, .344, 'MMSE, CDR toàn cục, CDR-SB\nvà sáu miền CDR', 10.5)
    values, indicators = clinical['input_values'], clinical['input_indicators']
    for y, count, label, fill in [
        (.239, values, 'giá trị đo', CLINICAL),
        (.140, indicators, 'chỉ báo quan sát', CLINICAL),
    ]:
        text(ax, .553, y+.037, f'{count} {label}', 9.5, ha='left')
        for i in range(count):
            ax.add_patch(Rectangle((.553+i*.045, y-.010), .040, .028,
                                   facecolor=fill, edgecolor=NAVY, lw=.55, zorder=2))
    box(ax, .759, .033, .413, .055,
        f"{values+indicators} đầu vào → MLP → {clinical['embedding_dim']} chiều", CLINICAL, 9.5)
    emit(fig, 'input-three-sources-redacted' if redacted else 'input-three-sources')


if __name__=='__main__':
    for f in [timeline, cohort, outer, pair_routes, cp, residual, rcfree_update, temporal, inputfigure]:
        f()
    print('Nine thesis figures generated (PDF/SVG/PNG 300 DPI).')
