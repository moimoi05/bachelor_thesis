"""Render the generic full bilinear and CP comparison for Chapter 2."""

from academic_style import save, scene, text
from build_explanatory import DARK, FUSION, cell, connect


def render():
    fig, ax = scene(6.3, 3.45)
    centers = (.095, .301, .511, .716, .916)
    widths = (.160, .176, .164, .173, .127)
    inputs = r'$x\in\mathbb{R}^{d_x}$' + '\n' + r'$y\in\mathbb{R}^{d_y}$'
    output = r'$h\in\mathbb{R}^{d_o}$'
    rows = (
        (.738, '(a) Ánh xạ song tuyến đầy đủ',
         (inputs, 'Tích ngoài\n' + r'$xy^\top$: $d_x\times d_y$',
          'Trải phẳng\n' + r'$d_xd_y$ chiều', r'Ánh xạ $W$' + '\n' + r'$+\ b$', output),
         r'$d_od_xd_y$ trọng số'),
        (.322, '(b) Tham số hóa bằng CP',
         (inputs, r'$u=A^\top x$' + '\n' + r'$v=B^\top y$',
          r'$u\odot v$' + '\n' + r'$Q$ chiều', r'$O(u\odot v)+b$', output),
         r'$Q(d_x+d_y+d_o)$ trọng số'),
    )
    for y, title, labels, count in rows:
        text(ax, .015, y+.156, title, 10.5, 'bold', ha='left')
        for index, (x, width, label) in enumerate(zip(centers, widths, labels)):
            style = {'fill': FUSION} if index in (1, 2, 3) else {}
            cell(ax, x, y, width, .155, label, size=9.5, **style)
        for left, left_width, right, right_width in zip(
                centers, widths, centers[1:], widths[1:]):
            connect(ax, (left+left_width/2, y), (right-right_width/2, y))
        text(ax, .985, y-.119, count, 9.5, ha='right', color=DARK)
    text(ax, .5, .150,
         r'$A$: $d_x\times Q$' + '     ' + r'$B$: $d_y\times Q$'
         + '     ' + r'$O$: $d_o\times Q$', 9.6)
    text(ax, .5, .049, r'$W_{kij}\approx\sum_{q=1}^{Q}O_{kq}A_{iq}B_{jq}$', 12)
    save(fig, 'cp-concept-general')


if __name__ == '__main__':
    render()
