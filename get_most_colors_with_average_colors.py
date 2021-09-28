from PIL import Image
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QFrame, QApplication, QLabel
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.Qt import Qt
from math import ceil
from pprint import pprint


### Вариант с усреднением цветов по группе

# change this parameters :)
how_much_colors = 30
rows_in_column = 10
maximum_allowed_distance = 125  # 50; 100


def check_color_in_groups(color, d):
    d_good_distances = {}
    # Проверяем предыдущие цвета (вернее группы цветов), чтобы понять, куда 
    # засунуть этот цвет
    for color_group in d:  # (238,15,80)
        dist_r = abs(color[0] - color_group[0])
        dist_g = abs(color[1] - color_group[1])
        dist_b = abs(color[2] - color_group[2])
        summ_dist = dist_r + dist_g + dist_b
        # Если разница в цвете допустимая, то не сразу возвращаем эту группу, а 
        # помещаем в словарь "хороших разниц", потом отсортируем и выдаём группу
        # с наименьшей разницей в цвете.
        if summ_dist <= maximum_allowed_distance:  # 50; 100
            d_good_distances[color_group] = summ_dist

    if d_good_distances:
        lsort_distances = sorted(list(d_good_distances.items()),
                                 reverse=False,
                                 key=lambda x: x[1]
        )
        return lsort_distances[0][0]
    return False


def get_colors_from_image(file, how_much_colors):
    im = Image.open(file)
    pxs = im.getdata()
    d_colors_count = {}
    d_contained_colors = {}  # словарь для усреднения потом цветов в нём, и
                             # выдачи в кач-ве результата
    k_glob = 0
    for k, px in enumerate(pxs):
        if isinstance(px, int):
            print(px, '- INT!', type(px))
        # else:
        #     print(px, type(px))
        if k == 0:
            d_colors_count[px] = 1
            d_contained_colors[px] = set()  # [px]  # добавляем цвет в группу цветов
            d_contained_colors[px].add(px)
            continue
        color_group = check_color_in_groups(px, d_colors_count)
        if not color_group:
            d_colors_count[px] = 1
            d_contained_colors[px] = set()
            d_contained_colors[px].add(px)
        else:
            d_colors_count[color_group] += 1
            d_contained_colors[color_group].add(px)
        k_glob = k
    print('Всего Обработано: ', k_glob)
    im.close()

    # #test
    # print(len(d_contained_colors.keys()))
    # for k, v in d_contained_colors.items():
    #     print(len(v))

    d_rezult_color_groups = {}
    cc = 0
    for color_group in d_contained_colors.keys():
        colors = d_contained_colors[color_group]  # множество кортежей c 3мя значениями (R,G,B)
        summ_r, summ_g, summ_b = 0, 0, 0
        for tup in colors:
            r, g, b = tup
            summ_r += r
            summ_g += g
            summ_b += b
        print('Обработано кортежей: ', len(colors))
        print("суммы:", summ_r, summ_g, summ_b)
        rez_r = round(summ_r / len(colors))
        rez_g = round(summ_g / len(colors))
        rez_b = round(summ_b / len(colors))
        rez_color = (rez_r, rez_g, rez_b)
        print("Получившийся цвет: ", rez_color)
        print('Оригинальный цвет: ', color_group)
        print('-------')
        d_rezult_color_groups[rez_color] = d_colors_count[color_group]

    # test
    for k,v in d_colors_count.items():
        print(f'{k} = {v}')
    print('---')
    for k,v in d_rezult_color_groups.items():
        print(f'{k} = {v}')

    # ls_colors = sorted(list(d_colors_count.items()), reverse=True, key=lambda x: x[1])
    ls_colors = sorted(list(d_rezult_color_groups.items()), reverse=True, key=lambda x: x[1])
    return ls_colors[:how_much_colors]


def my_sort_by_color(el):
    color = el[0]
    rez = color[0]*255*255 + color[1] * 255 + color[2]
    return rez


def test1(colors_list):
    testing_color = (0, 51, 111)
    colors = [c[0] for c in colors_list]
    for c in colors:
        rgb_dist = (abs(testing_color[0] - c[0]), abs(testing_color[1] - c[1]), abs(testing_color[2] - c[2]))
        print(c, 'dist:', rgb_dist, sum(rgb_dist))
    print(type(rgb_dist))


class Example(QWidget):
    def __init__(self, colors, file, rows_in_column):
        super().__init__()

        self.initUI(colors, file, rows_in_column)


    def initUI(self, colors, file, rows_in_column):
        # геометрические константы
        square_w = 130
        square_h = 50
        margin = 20
        window_rezult_height = margin

        wanted_size_px = 180
        self.img = QLabel(self)
        pixmap = QPixmap(file)
        w = pixmap.width()
        h = pixmap.height()
        if (w > wanted_size_px) or (h > wanted_size_px):
            pixmap = pixmap.scaled(wanted_size_px, wanted_size_px,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img.setPixmap(pixmap)

        self.img.setGeometry(margin, margin, wanted_size_px, wanted_size_px)
        if h > w:
            self.img.resize(ceil(wanted_size_px * (w / h)), wanted_size_px)
        elif w > h:
            self.img.resize(wanted_size_px, ceil(wanted_size_px * (h / w)))

        # Идём по цветам, полученным из-вне, и создаём QFrame'ы с каждым цветом
        for idx in range(len(colors)):
            c = colors[idx]
            if idx < rows_in_column:
                window_rezult_height += square_h

            column = idx // rows_in_column
            row = idx % rows_in_column

            color = QColor(*c[0])
            self.square = QFrame(self)
            self.square.setGeometry(self.img.width() + margin * 2 + column * (margin + square_w),
                                    row * square_h,
                                    square_w,
                                    square_h
            )
            self.square.setAutoFillBackground(True)
            # self.square.setStyleSheet("QWidget { background-color: %s }" % 'black')

            label = QLabel(self.square)
            label.setText(str(c))
            if c[0][0] < 80 and c[0][1] < 80 and c[0][2] < 80:
                label.setStyleSheet("QLabel {color: white;}")
            else:
                label.setStyleSheet("QLabel {color: black;}")

            pal = self.square.palette()
            pal.setBrush(QPalette.Background, color)  # QColor("#ff00ff"))
            self.square.setPalette(pal)

        self.setGeometry(300, 300,
            self.img.width() + margin * 2 + (len(colors) // rows_in_column + 1) * (margin + square_w),
            window_rezult_height)
        self.setWindowTitle('Colors pallete')
        self.show()


if __name__ == '__main__':
    # file = r'photo_2021-09-27_22-37-15.jpg'
    file = r'photo_2021-09-27_23-36-46.jpg'

    colors = get_colors_from_image(file, how_much_colors)
    app = QApplication(sys.argv)
    ex = Example(colors, file, rows_in_column)
    sys.exit(app.exec_())



# backup:

# def get_colors_from_image(how_much_colors=30):
#     im = Image.open(file)
#     # pixs = im.load()
#     pxs = im.getdata()
#     d_colors_count = {}
#     print('Считаем...')
#     for px in pxs:
#         pass
#         if px in d_colors_count:
#             d_colors_count[px] += 1
#         else:
#             d_colors_count[px] = 1
#     im.close()
#     print('Посчитали')

#     ls_colors = sorted(list(d_colors_count.items()), reverse=True, key=lambda x: x[1])
#     for i in range(how_much_colors):
#         print(ls_colors[i])
#     return ls_colors[:how_much_colors]
