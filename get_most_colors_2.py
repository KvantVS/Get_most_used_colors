import sys
from math import ceil
from PIL import Image
from PyQt5.QtWidgets import QWidget, QPushButton, QFrame, QApplication, QLabel, QGraphicsObject, QCheckBox
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.Qt import Qt


# change these parameters :)
how_much_colors = 30
maximum_allowed_distance = 125  # 50; 100  # дистанция между похожими цветами
max_square_w = 280  # width of "color-box"


def check_color_in_groups(color, d):
    """Ищем группу, в которую попадает цвет, с минимальной дистанцией по цвету"""

    b_finded = False
    d_distances = {}

    # Идём по уже сформированным цветовым группам
    for color_group in d:  # (238,15,80)
        dist_r = abs(color[0] - color_group[0])
        dist_g = abs(color[1] - color_group[1])
        dist_b = abs(color[2] - color_group[2])
        summ_dist = dist_r + dist_g + dist_b
        if summ_dist <= maximum_allowed_distance:
            # Если дистанция входит в допустимый диапазон (max_al_distance)
            # , то добавляем в словарик
            d_distances[color_group] = summ_dist

    # Потом если по словарю есть несколько цветовых дистанций, то сортируем по
    # самому минимальному значению (summ_dist) и берём первую (минимальную)
    if d_distances:
        lsort_distances = sorted(list(d_distances.items()),
                                 reverse=False,
                                 key=lambda x: x[1]
        )

        return lsort_distances[0][0]
    return b_finded


def get_colors_from_image(file, how_much_colors):
    im = Image.open(file)
    pxs = im.getdata()
    d_colors = {}
    for k, px in enumerate(pxs):
        # Variant 2 - with grouping by color
        if k == 0:
            d_colors[px] = 1
            continue
        color_group = check_color_in_groups(px, d_colors)
        if not color_group:
            d_colors[px] = 1
        else:
            d_colors[color_group] += 1
    im.close()

    ls_colors = sorted(list(d_colors.items()), reverse=True, key=lambda x: x[1])
    return ls_colors[:how_much_colors]


class MyWindow(QWidget):
    def chb_click(self):
        global current_colors_count, colors

        isChecked = self.sender().isChecked()
        idx = self.sender().objectName()[3:]
        finded_box = self.findChild(QFrame, 'colorbox' + idx)
        idx = int(idx)
        finded_box.setVisible(isChecked)

        if isChecked:
            current_colors_count = current_colors_count + colors[idx][1]
        else:
            current_colors_count = current_colors_count - colors[idx][1]

        for i in range(len(colors)):
            finded_checkbox = self.findChild(QCheckBox, 'chb' + str(i))
            if finded_checkbox.isChecked():
                finded_box = self.findChild(QFrame, 'colorbox' + str(i))
                qbox = finded_box.geometry()
                # print(qbox)
                w = round(colors[i][1] / current_colors_count * max_square_w)
                if w < 1:
                    w = 1
                finded_box.setGeometry(
                    qbox.left(),
                    qbox.top(),
                    w,
                    qbox.height()
                )


    def __init__(self, colors, file):
        super().__init__()

        self.initUI(colors, file)


    def initUI(self, colors, file):
        global init_colors_count, current_colors_count
        # === geometry constants ===
        square_h = 25   # and height for QFrames (colored boxes) 
        margin = 20     # space between elements on window
        wanted_size_px = 180  # resolution for Image-file box

        # Initiate basic window height
        # window_result_height = margin

        # Drawing image file
        self.img = QLabel(self)
        pixmap = QPixmap(file)
        w = pixmap.width()
        h = pixmap.height()
        init_colors_count = w * h
        current_colors_count = init_colors_count
        if (w > wanted_size_px) or (h > wanted_size_px):
            pixmap = pixmap.scaled(wanted_size_px, wanted_size_px,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img.setPixmap(pixmap)

        # Set x, y, w, h and resizing Image-box by bitmap true resolution
        self.img.setGeometry(margin, margin, wanted_size_px, wanted_size_px)
        if w < h:
            self.img.resize(ceil(wanted_size_px * (w / h)), wanted_size_px)
        elif w > h:
            self.img.resize(wanted_size_px, ceil(wanted_size_px * (h / w)))

        # left for colorboxes
        start_x = self.img.width() + margin * 2 + 25 + margin
        # left for bottom colorbox
        next_x = start_x

        # Идём по цветам, полученным из-вне, и создаём QFrame'ы с каждым цветом
        max_w = 0
        for idx in range(len(colors)):
            c = colors[idx]
            color_value = QColor(*c[0])

            # Создаём чекбокс для отключения бара
            chb = QCheckBox(self)
            chb.setObjectName('chb' + str(idx))
            chb.setChecked(True)
            chb.setGeometry(
                self.img.width() + margin * 2,
                idx * square_h,
                25,
                square_h
            )
            chb.clicked.connect(self.chb_click)
            
            # Расчитаем длину прямоугольника
            square_w = round(c[1] / init_colors_count * max_square_w)
            if square_w < 1:
                square_w = 1
            if square_w > max_w:
                max_w = square_w

            self.square = QFrame(self)
            self.square.setObjectName('colorbox' + str(idx))
            self.square.setGeometry(
                start_x,
                idx * square_h,
                square_w,
                square_h
            )
            self.square.setAutoFillBackground(True)
            pal = self.square.palette()
            pal.setBrush(QPalette.Background, color_value)
            self.square.setPalette(pal)
            
            # Label inside QFrame, with text info about color and quantity
            label = QLabel(self)
            label.setGeometry(
                start_x,
                idx * square_h,
                160,
                16
            )
            label.setText(str(c))
            if ((c[0][0] < 80) and (c[0][1] < 80) and (c[0][2] < 80)) or (c[0][0] < 80 and c[0][1] < 80):
                label.setStyleSheet("QLabel {color: white;}")
            else:
                label.setStyleSheet("QLabel {color: black;}")

            # additional bottom colorbox
            bottom_sq = QFrame(self)
            bottom_sq.setGeometry(
                next_x,
                1+len(colors) * square_h,
                square_w,
                square_h
            )
            bottom_sq.setAutoFillBackground(True)
            pal = bottom_sq.palette()
            pal.setBrush(QPalette.Background, color_value)
            bottom_sq.setPalette(pal)

            next_x += square_w

        # Window parameters
        self.setGeometry(
            300,
            300,
            self.img.width() + margin * 2 + (margin + max_square_w)  + 25 + margin,
            square_h * len(colors) + margin  # window_result_height
        )
        self.setWindowTitle('Colors pallete')
        self.show()


if __name__ == '__main__':
    # if len(sys.argv) > 1:
    #     if sys.argv[1]:
    #         file = sys.argv[1].strip()
    #     else:
    #         file = input('Specify image file for calculate colors: ').strip()
    # else:
    #     file = input('Specify image file for calculate colors: ').strip()
    # if file.startswith('"'):
    #     file = file[1:-1]
    
    file = r"E:\3440\wallhaven-dpgzgg.png"

    init_colors_count = 0
    current_colors_count = 0
    colors = get_colors_from_image(file, how_much_colors)
    for color in colors:
        print(color[0], ',', sep='')

    app = QApplication(sys.argv)
    ex = MyWindow(colors, file)
    sys.exit(app.exec_())



# backup:

# def get_colors_from_image(how_much_colors=30):
#     im = Image.open(file)
#     # pixs = im.load()
#     pxs = im.getdata()
#     d_colors = {}
#     print('Считаем...')
#     for px in pxs:
#         pass
#         if px in d_colors:
#             d_colors[px] += 1
#         else:
#             d_colors[px] = 1
#     im.close()
#     print('Посчитали')

#     ls_colors = sorted(list(d_colors.items()), reverse=True, key=lambda x: x[1])
#     for i in range(how_much_colors):
#         print(ls_colors[i])
#     return ls_colors[:how_much_colors]


# self.square.setStyleSheet("QWidget { background-color: %s }" % 'black')

# file = r'photo_2021-09-27_22-37-15.jpg'
# file = r'photo_2021-09-27_23-36-46.jpg'
# # file = r"C:\Users\kvant\Downloads\girl0102304 (1).jpg"
# file = r"C:\Users\kvant\Downloads\girl0102304 (2).jpg"
# file = r"C:\Users\kvant\Downloads\girl0102304 (3).jpg"
# file = r"C:\Users\kvant\Downloads\girl0102304 (4).jpg"
# file = r"E:\testcolor\test,png.png"
# file = r"E:\3440\wallhaven-dpgzgg.png"