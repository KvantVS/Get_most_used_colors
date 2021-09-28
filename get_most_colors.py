from PIL import Image
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QFrame, QApplication, QLabel
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.Qt import Qt
from math import ceil


# change this parameters :)
how_much_colors = 30
rows_in_column = 10
maximum_allowed_distance = 125  # 50; 100


def check_color_in_groups(color, d):
    b_finded = False
    d_distances = {}
    for color_group in d:  # (238,15,80)
        dist_r = abs(color[0] - color_group[0])
        dist_g = abs(color[1] - color_group[1])
        dist_b = abs(color[2] - color_group[2])
        summ_dist = dist_r + dist_g + dist_b
        if summ_dist <= maximum_allowed_distance:  # 50; 100
            d_distances[color_group] = summ_dist

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
        # # Variant 1 - w/o grouping (every color will be counted)
        # if px in d_colors:
        #     d_colors[px] += 1
        # else:
        #     d_colors[px] = 1

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
    def __init__(self, colors, file, rows_in_column):
        super().__init__()

        self.initUI(colors, file, rows_in_column)


    def initUI(self, colors, file, rows_in_column):
        # === geometry constants ===
        square_w = 130  # Width
        square_h = 50   # and height for QFrames (colored boxes) 
        margin = 20     # space between elements on window
        wanted_size_px = 180  # resolution for Image-file box

        # Initiate basic window height
        window_rezult_height = margin

        # Drawing image file
        self.img = QLabel(self)
        pixmap = QPixmap(file)
        w = pixmap.width()
        h = pixmap.height()
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

        # Идём по цветам, полученным из-вне, и создаём QFrame'ы с каждым цветом
        # Going through the colors received from outside and create QFrames with 
        # each color
        for idx in range(len(colors)):
            c = colors[idx]
            if idx < rows_in_column:
                window_rezult_height += square_h

            column = idx // rows_in_column
            row = idx % rows_in_column

            color = QColor(*c[0])

            # QFrame - colored box
            self.square = QFrame(self)
            self.square.setGeometry(
                self.img.width() + margin * 2 + column * (margin + square_w),
                row * square_h,
                square_w,
                square_h
            )
            self.square.setAutoFillBackground(True)
            pal = self.square.palette()
            pal.setBrush(QPalette.Background, color)
            self.square.setPalette(pal)

            # Label inside QFrame, with text info about color and quantity
            label = QLabel(self.square)
            label.setText(str(c))
            if c[0][0] < 80 and c[0][1] < 80 and c[0][2] < 80:
                label.setStyleSheet("QLabel {color: white;}")
            else:
                label.setStyleSheet("QLabel {color: black;}")

        # Window parameters
        self.setGeometry(
            300,
            300,
            self.img.width() + margin * 2
            + (len(colors) // rows_in_column + 1) * (margin + square_w),
            window_rezult_height)
        self.setWindowTitle('Colors pallete')
        self.show()


if __name__ == '__main__':
    # file = r'photo_2021-09-27_22-37-15.jpg'
    file = r'photo_2021-09-27_23-36-46.jpg'

    colors = get_colors_from_image(file, how_much_colors)
    app = QApplication(sys.argv)
    ex = MyWindow(colors, file, rows_in_column)
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
