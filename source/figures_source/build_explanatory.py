"""Publication diagrams for Chapters 2 and 3."""

from matplotlib.patches import Rectangle

from academic_style import (
    CLINICAL, FUSION, INK as DARK, MRI, NAVY, PALE, RADIOMICS, RULE,
    SURVIVAL, TEMPORAL, WHITE, arrow, line, route, save, scene, text,
)


def heading(ax, x, y, label):
    text(ax, x, y, label, 10.5, 'bold', ha='left', color=NAVY)


def cell(ax, x, y, w, h, label, fill=WHITE, size=10, edge=NAVY, weight='normal'):
    """Place a labeled rectangle at the given center."""
    ax.add_patch(Rectangle((x-w/2, y-h/2), w, h, linewidth=.85,
                           edgecolor=edge, facecolor=fill, zorder=2))
    text(ax, x, y, label, size, weight, color=DARK)


def connect(ax, start, end, **kwargs):
    arrow(ax, start, end, color=DARK, lw=1.05, **kwargs)


def branch(ax, points):
    route(ax, points, color=DARK, lw=1.05)


def followup():
    fig, ax = scene(6.3, 2.55)
    b, s1, s2, p, landmark = .13, .24, .36, .48, .63
    ax.add_patch(Rectangle((p, .29), landmark-p, .44, facecolor=PALE,
                           edgecolor='none', zorder=0))
    connect(ax, (b, .84), (landmark, .84), style='<->')
    text(ax, (b+landmark)/2, .92, r'Cửa sổ 18 tháng $[b,L]$', 10)
    for x, label in zip((b, s1, s2, p, landmark),
                        (r'$b$', r'$s_1$', r'$s_2$', r'$p=s_3$', r'$L$')):
        line(ax, (x, .29), (x, .71), RULE, .65, ':')
        text(ax, x, .76, label, 10)
    for y, end, person, marker, observation, status in (
        (.58, .83, 'A', 'x', r'$o_A$', r'Biến cố $\delta_A=1$'),
        (.35, .93, 'B', '|', r'$o_B$', r'Kiểm duyệt $\delta_B=0$'),
    ):
        text(ax, .055, y, person, 10, 'bold')
        line(ax, (b, y), (p, y), RULE, 1.45)
        line(ax, (p, y), (end, y), DARK, 1.45)
        ax.plot([s1, s2, p], [y, y, y], 'o', markerfacecolor=MRI,
                markeredgecolor=NAVY, markersize=4.9, zorder=3)
        ax.plot(end, y, marker=marker, color=NAVY, markersize=8,
                markeredgewidth=1.4, zorder=3)
        text(ax, end, y+.078, observation, 9.5)
        text(ax, .68, y-.080, status, 9.5, ha='left')
    line(ax, (p, .248), (landmark, .248), NAVY, .7)
    text(ax, .13, .155, r'$[p,L]$: chưa tiến triển theo điều kiện chọn mẫu', 9.25, ha='left')
    text(ax, .13, .066, r'Thời gian phân tích: $t=(o-p)/365.25$', 9.5, ha='left')
    save(fig, 'concept-survival')


def sequence():
    fig, ax = scene(6.3, 2.65)
    for x, i in ((.15, 1), (.50, 2), (.85, 3)):
        text(ax, x, .81, rf'Lần khám {i}  ·  $F_{i}$', 10)
        connect(ax, (x, .75), (x, .64))
        cell(ax, x, .56, .187, .16, rf'T-LSTM · $h_{i}$', TEMPORAL)
        line(ax, (x, .48), (x, .31), DARK, 1.05)
        text(ax, x+.035, .391, rf'$\alpha_{i}$', 9.5, ha='left')
        ax.plot(x, .31, 'o', color=DARK, markersize=2.8, zorder=3)
    for left, right, gap in ((.244, .406, 2), (.594, .756, 3)):
        connect(ax, (left, .56), (right, .56))
        text(ax, (left+right)/2, .62, rf'$\Delta t_{gap}$', 9.5)
    line(ax, (.15, .31), (.85, .31), DARK, 1.05)
    connect(ax, (.5, .31), (.5, .204))
    cell(ax, .5, .126, .53, .155, r'Attention: $z=\sum_t \alpha_t h_t$', TEMPORAL)
    ax.set_ylim(0, .89)
    save(fig, 'concept-longitudinal')


def sources():
    fig, ax = scene(6.3, 2.45)
    heading(ax, .02, .94, '(a) Nguồn ảnh')
    heading(ax, .69, .94, '(b) Nguồn lâm sàng')
    line(ax, (.655, .07), (.655, .93), RULE, .7)
    cell(ax, .334, .77, .28, .155, 'MRI cấu trúc 3D', MRI)
    cell(ax, .83, .77, .26, .155, 'MMSE / CDR', CLINICAL)
    line(ax, (.334, .6925), (.334, .62), DARK, 1.05)
    for x, label, color, symbol in (
        (.158, 'CNN 3D\nĐặc trưng học', MRI, 'M'),
        (.510, 'Radiomics\nPhép đo định sẵn', RADIOMICS, 'R'),
        (.830, 'Xử lý dữ liệu thiếu\nvà mã hóa bằng MLP', CLINICAL, 'C'),
    ):
        if x < .65:
            branch(ax, [(.334, .62), (x, .62), (x, .55)])
        else:
            connect(ax, (x, .6925), (x, .55))
        cell(ax, x, .445, .26, .21, label, color)
        connect(ax, (x, .34), (x, .2285))
        cell(ax, x, .151, .14, .155, '$' + symbol + '$', color, 12)
    save(fig, 'concept-sources')


def fusion():
    fig, ax = scene(6.3, 2.6)
    for x, title in ((.25, '(a) Ghép nối'), (.75, '(b) Tích ngoài')):
        heading(ax, x-.213, .93, title)
        text(ax, x, .73, r'$x=(x_1,x_2),\ y=(y_1,y_2)$', 11)
    connect(ax, (.25, .65), (.25, .51))
    neutral_fills = (WHITE, '#E5E8EB')
    for i, label in enumerate((r'$x_1$', r'$x_2$', r'$y_1$', r'$y_2$')):
        cell(ax, .112+i*.092, .435, .092, .15, label, neutral_fills[i % 2], 12)
    connect(ax, (.75, .65), (.75, .585))
    for i in range(2):
        for j in range(2):
            cell(ax, .69+j*.12, .505-i*.16, .12, .16,
                 rf'$x_{i+1}y_{j+1}$', neutral_fills[(i+j)%2], 11)
    text(ax, .25, .185, r'$[x;y]\in\mathbb{R}^{4}$', 11, 'bold')
    text(ax, .75, .14, r'$xy^{\top}\in\mathbb{R}^{2\times2}$', 11, 'bold')
    save(fig, 'concept-fusion')


def literature_gates():
    fig, ax = scene(6.3, 4.95)
    rows = (
        (.835, '(a) Ryumina · Text Residual Fusion',
         r'Văn bản $b$', 'Âm thanh, khuôn mặt,\n' + r'cảnh $h_m$',
         r'Cổng $g_m$ và MLP $d_m$' + '\n' + r'Phần dư $g_m d_m(h_m)$',
         'Cộng phần dư vào $b$\nLN → MLP phân loại'),
        (.497, '(b) Liu · DyFADet+',
         r'RGB $\rightarrow F_r^{(\ell)}$', r'Bộ xương $\rightarrow F_s^{(\ell)}$',
         r'Cổng $G^{(\ell)}$' + '\n' + r'Adapter $\psi_\ell$, $\alpha=0.5$',
         'Cộng vào RGB\nĐầu phát hiện thời gian'),
    )
    for y, title, anchor, other, gate, result in rows:
        heading(ax, .018, y+.135, title)
        cell(ax, .153, y, .27, .070, anchor)
        cell(ax, .153, y-.092, .27, .082, other, size=9.6)
        cell(ax, .50, y-.046, .255, .113, gate, FUSION, 9.8)
        cell(ax, .846, y-.046, .27, .113, result, FUSION, 9.8)
        connect(ax, (.288, y), (.3725, y-.02))
        connect(ax, (.288, y-.092), (.3725, y-.07))
        connect(ax, (.6275, y-.046), (.711, y-.046))
        branch(ax, [(.153, y+.035), (.153, y+.077), (.846, y+.077), (.846, y+.012)])
    y = .145
    heading(ax, .018, y+.135, '(c) RC-Free · Tương tác theo cặp và bốn nhánh truyền')
    cell(ax, .153, y, .27, .105, 'MRI, radiomics,\nlâm sàng')
    cell(ax, .50, y, .255, .105, 'CP: MR và MC\nChiếu về từng đích', FUSION)
    cell(ax, .846, y, .27, .105, r'$U_d+\sum\lambda g\widehat E$' + '\n' + r'LN $\rightarrow$ ghép nối',
         FUSION)
    connect(ax, (.288, y), (.3725, y))
    connect(ax, (.6275, y), (.711, y))
    branch(ax, [(.153, y-.0525), (.153, .04), (.846, .04), (.846, y-.0525)])
    text(ax, .5, .068, r'Biểu diễn gốc $U_d$', 9.4)
    save(fig, 'literature-gates')


def clinical():
    fig, ax = scene(6.3, 3.17)
    heading(ax, .018, .94, '(a) Hai nhánh xử lý cùng chín biến')
    text(ax, .982, .94, 'Ví dụ minh họa', 9.25, ha='right')
    columns = [.30+i*.077 for i in range(9)]
    indicator_fill = SURVIVAL
    missing_fill = '#F7D9CF'
    for i, (x, present) in enumerate(zip(columns, [1, 1, 0, 1, 1, 1, 0, 1, 1]), 1):
        text(ax, x, .805, str(i), 9.5, 'bold')
        value = rf'$v_{i}$' if present else rf'$m_{i}$'
        cell(ax, x, .682, .069, .122, value, CLINICAL if present else missing_fill, 10)
        cell(ax, x, .521, .069, .122, str(present), indicator_fill if present else missing_fill,
             10, weight='normal' if present else 'bold')
    text(ax, .018, .805, 'Biến', 9.5, 'bold', ha='left')
    text(ax, .018, .682, 'Giá trị sau điền', 9.5, ha='left')
    text(ax, .018, .521, 'Chỉ báo quan sát', 9.5, ha='left')
    text(ax, .018, .407, r'$m_i$: trung vị tập huấn luyện. Giá trị được chuẩn hóa sau khi điền thiếu.',
         9.25, ha='left')
    heading(ax, .018, .27, '(b) Ghép đầu vào')
    cell(ax, .139, .124, .240, .115, '9 giá trị chuẩn hóa', CLINICAL, 9.4)
    cell(ax, .379, .124, .240, .115, '9 chỉ báo', indicator_fill, 9.4)
    connect(ax, (.499, .124), (.56, .124))
    cell(ax, .677, .124, .234, .115, 'MLP 18 → 64 → 64', CLINICAL, 9.55)
    connect(ax, (.794, .124), (.842, .124))
    text(ax, .916, .124, r'$C\in\mathbb{R}^{64}$', 10.25)
    save(fig, 'clinical-18-inputs')


def concat():
    fig, ax = scene(6.3, 2.59)
    heading(ax, .015, .929, r'Ghép nối tại lần khám $t$')
    for y, label, color in ((.756, r'$M_t$', MRI), (.540, r'$R_t$', RADIOMICS),
                            (.324, r'$C_t$', CLINICAL)):
        cell(ax, .11, y, .184, .149, label, color, 10.35)
        line(ax, (.202, y), (.267, y), DARK, 1.05)
    line(ax, (.267, .324), (.267, .756), DARK, 1.05)
    connect(ax, (.267, .54), (.324, .54))
    text(ax, .492, .715, r'$[M_t;R_t;C_t]\in\mathbb{R}^{256}$', 10.4)
    for left, width, label, color in ((.324, .167, '128', MRI), (.491, .0835, '64', RADIOMICS),
                                      (.5745, .0835, '64', CLINICAL)):
        cell(ax, left+width/2, .54, width, .181, label, color, 10)
    connect(ax, (.658, .540), (.716, .540))
    cell(ax, .799, .540, .164, .181, 'MLP\n256 → 128', FUSION, 9.5)
    connect(ax, (.881, .540), (.913, .540))
    text(ax, .922, .54, r'$F_t\in\mathbb{R}^{128}$', 10.5, ha='left')
    text(ax, .5, .12, r'$F_1,F_2,F_3$  →  T-LSTM  →  Attention  →  Cox', 10.25)
    save(fig, 'concat-baseline')


def metrics():
    fig, ax = scene(6.3, 3.12)
    cell(ax, .5, .905, .86, .135,
         r'Điểm nguy cơ $\eta$  ·  Thời gian theo dõi $t$  ·  Biến cố $\delta$', SURVIVAL)
    line(ax, (.5, .8375), (.5, .765), DARK, 1.05)
    line(ax, (.173, .765), (.827, .765), DARK, 1.05)
    columns = (
        (.173, '(a) C-index', 'Xếp hạng nguy cơ', 'Các cặp so sánh được', MRI),
        (.500, '(b) Kaplan–Meier', 'Diễn biến sống còn', 'Hai nhóm nguy cơ', RADIOMICS),
        (.827, r'(c) AUC tại $h$', r'Phân biệt tại mốc $h$', r'Biến cố / theo dõi $>h$', CLINICAL),
    )
    for x, label, purpose, detail, fill in columns:
        connect(ax, (x, .765), (x, .697))
        cell(ax, x, .64, .305, .114, label, fill, size=10.3, weight='bold')
        text(ax, x, .267, purpose, 10, 'bold')
        text(ax, x, .169, detail, 9.4)
    for y, end in ((.513, .142), (.445, .211), (.377, .266)):
        line(ax, (.077, y), (end, y), '#37618D', 1.6)
        ax.plot(end, y, 'o', color='#37618D', ms=3)
    ax.plot([.396,.442,.442,.501,.501,.602], [.511,.511,.466,.466,.424,.424],
            color='#43745A', lw=1.6)
    ax.plot([.396,.423,.423,.481,.481,.602], [.511,.511,.432,.432,.365,.365],
            color='#A14F4E', lw=1.6)
    line(ax, (.733,.36), (.925,.36), DARK, .8)
    line(ax, (.733,.36), (.733,.545), DARK, .8)
    line(ax, (.733,.36), (.925,.545), RULE, .8, '--')
    ax.plot([.733,.755,.807,.873,.925], [.36,.44,.502,.533,.545],
            color='#946C26', lw=1.6)
    for x in (.3365, .6635):
        line(ax, (x,.117), (x,.564), RULE, .7)
    save(fig, 'evaluation-map')


if __name__ == '__main__':
    for draw in (followup, sequence, sources, fusion, literature_gates, clinical, concat, metrics):
        draw()
    print('Eight explanatory figures generated as PDF, SVG and 300 DPI PNG.')
