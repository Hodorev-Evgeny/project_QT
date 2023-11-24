import sys
import sqlite3
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QScrollArea, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from random import shuffle
from PyQt5.QtGui import QPixmap
from pyqtgraph import PlotWidget


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class MainProduct(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.con = sqlite3.connect("SQLbd.sqlite")
        self.namber_thems = 0

        self.flag, self.thems = 1, 1
        self.max_paragraf, self.max_task_number = 2, 3
        self.max_paragraf = 2
        self.max_task_number = 3

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(0)
        self.scroll_2 = QScrollArea()
        self.scroll_2.setVerticalScrollBarPolicy(0)

        self.cur = self.con.cursor()

        self.pushButton_updatetab.clicked.connect(self.graf)

        for bn in self.buttonGroup.buttons():
            bn.clicked.connect(self.paragraph)
        for bn in self.option.buttons():
            bn.clicked.connect(self.window_option)

        que = self.cur.execute("""SELECT id, number_correct_answers
                    FROM data_graphics""").fetchall()

        self.ox = [elem[0] for elem in que]
        self.oy = [elem[1] for elem in que]

        self.plot(self.ox, self.oy)

    def plot(self, x, y):
        self.graphWidget.plot(x, y)

    def paragraph(self):
        self.window(self.sender().text())

    def bd(self, name_thems):
        date = self.cur.execute(f"""SELECT name_paragraph, content FROM paragref_thems
                         WHERE name_them = {name_thems[0][0]} 
                         AND number_paragraf = {self.thems}""").fetchall()

        name_par, text = date[0][0], date[0][1]

        self.con.commit()

        return name_par, text

    def window(self, name):
        self.name_thems = self.cur.execute(f"SELECT id FROM themes WHERE name = '{name}'").fetchall()

        name_par, text = (self.bd(self.name_thems))

        self.window_1 = QWidget(self, Qt.Window)
        self.window_1.setWindowModality(Qt.WindowModal)
        self.window_1.setWindowTitle(f'Теория по {name}')
        self.window_1.resize(700, 500)
        self.label_paragraf = QLabel(self.window_1)
        self.label_name_paragraf = QLabel(self.window_1)

        self.scroll = QScrollArea(self.window_1)
        self.scroll.setVerticalScrollBarPolicy(0)

        result_text = ''.join(text)

        self.label_name_paragraf.setText(name_par)
        self.label_name_paragraf.setStyleSheet("font-size: 18px")

        self.label_paragraf.setText(result_text)
        self.label_paragraf.setStyleSheet("font-size: 16px")
        self.label_paragraf.setWordWrap(True)
        self.label_paragraf.adjustSize()
        self.scroll.setWidget(self.label_paragraf)
        self.scroll.move(10, 30)
        self.scroll.resize(670, 400)

        self.btn_next_window_1 = QPushButton('Следущие параграф', self.window_1)
        self.btn_next_window_1.resize(200, 50)
        self.btn_next_window_1.move(470, 430)
        self.btn_next_window_1.clicked.connect(self.update_thems)

        self.btn_back_window_1 = QPushButton('Предыдущие параграф', self.window_1)
        self.btn_back_window_1.resize(200, 50)
        self.btn_back_window_1.move(50, 430)
        self.btn_back_window_1.clicked.connect(self.return_thems)
        self.btn_back_window_1.hide()

        self.con.commit()

        self.window_1.show()

    def update_thems(self):
        if self.thems < self.max_paragraf:
            self.thems += 1

        name_par, text = (self.bd(self.name_thems))

        self.label_name_paragraf.setText(''.join(name_par))
        self.label_name_paragraf.adjustSize()

        if self.thems > 1:
            self.btn_back_window_1.show()

        self.label_paragraf.setText(''.join(text))
        self.label_paragraf.adjustSize()

        if self.thems == self.max_paragraf:
            self.btn_end_thems = QPushButton('Завершить работу', self.window_1)
            self.btn_end_thems.resize(200, 50)
            self.btn_end_thems.move(470, 430)
            self.btn_next_window_1.hide()
            self.btn_end_thems.show()
            self.btn_end_thems.clicked.connect(self.close_wind_1)

        self.update()

    def close_wind_1(self):
        self.thems = 1
        self.window_1.close()


    def return_thems(self):
        if self.thems > 1:
            self.thems -= 1
        if self.thems == 1:
            self.btn_back_window_1.hide()

        name_par, text = self.bd(self.name_thems)

        self.label_name_paragraf.setText(name_par)
        self.label_name_paragraf.adjustSize()

        if self.thems != self.max_paragraf:
            self.btn_end_thems.hide()
            self.btn_next_window_1.show()

        self.label_paragraf.setText(''.join(text))
        self.label_paragraf.adjustSize()

        self.update()

    def graf(self):
        self.graphWidget.clear()
        self.graphWidget.plot(self.ox, self.oy)

    def content_task(self):
        que = self.cur.execute("""SELECT id FROM variants""")
        res = [elem[0] for elem in que]
        if self.number_variant == 1:
            res = res[:6]
        elif self.number_variant == 2:
            res = res[6:12]
        elif self.number_variant == 3:
            res = res[2:8]
        shuffle(res)
        self.id_number = res[:self.max_task_number]
        content = []
        for j in self.id_number:
            content.append(*self.cur.execute(f"""SELECT text_task, photo_task FROM variants WHERE id = {j}"""))
        return content

    def photo_task(self, image):
        self.pixmap = QPixmap(f'photo\{image}.png')
        self.image.setPixmap(self.pixmap)
        self.image.adjustSize()

    def window_option(self):
        self.number_variant = int(self.sender().text()[-1])

        self.content = self.content_task()

        self.window_2 = QWidget(self, Qt.Window)
        self.window_2.setWindowModality(Qt.WindowModal)
        self.window_2.setWindowTitle(f'{self.sender().text()}')
        self.window_2.resize(700, 500)

        self.content_layout = QVBoxLayout(self.window_2)

        self.image = QLabel(self.window_2)
        self.image.move(80, 190)

        self.label_option = QLabel(self.window_2)
        if self.content[self.flag - 1][1] != None:
            self.photo_task(self.content[self.flag - 1][1])
        self.label_option.setText(''.join(self.content[self.flag - 1][0]))
        self.label_option.setStyleSheet("font-size: 16px")
        self.label_option.move(80, 30)
        self.label_option.setWordWrap(True)
        self.label_option.adjustSize()

        self.btn_next = QPushButton('Следущие задание', self.window_2)
        self.btn_next.resize(200, 50)
        self.btn_next.move(470, 430)

        self.name_input = QLineEdit(self.window_2)
        self.name_input.resize(300, 30)
        self.name_input.move(80, 380)

        self.btn_next.clicked.connect(self.update_window)

        self.btn_back = QPushButton('Предыдущие задание', self.window_2)
        self.btn_back.resize(200, 50)
        self.btn_back.move(470, 350)
        self.btn_back.clicked.connect(self.return_window)
        self.btn_back.hide()

        self.btn_save = QPushButton('Сохронить ответ', self.window_2)
        self.btn_save.resize(300, 30)
        self.btn_save.move(80, 450)
        self.btn_save.clicked.connect(self.save_answer)

        self.con.commit()

        self.window_2.show()


    def update_window(self):
        if self.flag < self.max_task_number:
            self.flag += 1
            self.btn_next.setText('Следущие задание')


        self.name_input.setText('')

        if self.flag > 1:
            self.btn_back.show()

        if self.content[self.flag - 1][1] != None:
            self.photo_task(self.content[self.flag - 1][1])
            self.image.show()
        else:
            self.image.hide()
        self.label_option.setText(''.join(self.content[self.flag - 1][0]))
        self.label_option.setWordWrap(True)
        self.label_option.adjustSize()

        if self.flag == self.max_task_number:
            self.btn_end = QPushButton('Завершить работу', self.window_2)
            self.btn_end.resize(200, 50)
            self.btn_end.move(470, 430)

            self.btn_next.hide()
            self.btn_end.show()
            self.btn_end.clicked.connect(self.result_window)

        self.con.commit()

        self.update()

    def result_window(self):
        self.flag = 1

        self.window_2.close()
        self.window_3 = QWidget(self, Qt.Window)
        self.window_3.setWindowModality(Qt.WindowModal)
        self.window_3.setWindowTitle('Результаты')
        self.window_3.resize(300, 200)

        res = self.checking_responses()

        self.label_result = QLabel(self.window_3)
        self.label_result.setText(f'Вы решили {res} из {self.max_task_number}')
        self.label_result.setStyleSheet("font-size: 16px")
        self.label_result.move(80, 30)

        self.btn_close = QPushButton('Выйти', self.window_3)
        self.btn_close.resize(100, 50)
        self.btn_close.move(100, 80)
        self.btn_close.clicked.connect(self.window_3.close)

        self.window_3.show()


    def return_window(self):
        if self.flag > 1:
            self.flag -= 1


        self.name_input.setText('')

        if self.flag == 1:
            self.btn_back.hide()

        elif self.flag != self.max_task_number:
            self.btn_end.hide()
            self.btn_next.show()

        if self.content[self.flag - 1][1] != None:
            self.photo_task(self.content[self.flag - 1][1])
            self.image.show()
        else:
            self.image.hide()
        self.label_option.setText(''.join(self.content[self.flag - 1][0]))
        self.label_option.setWordWrap(True)
        self.label_option.adjustSize()

        self.con.commit()

        self.update()

    def checking_responses(self):
        cur = self.con.cursor()

        date = []
        for i in self.id_number:
            date.append(*self.cur.execute(f"""SELECT input, corect FROM ansewers
                WHERE id = {i}""").fetchall())

        res = len([1 for elems in date if elems[0] == elems[1]])

        self.ox[self.number_variant - 1] = self.number_variant
        self.oy[self.number_variant - 1] = res

        cur.execute(f"""UPDATE data_graphics
                    SET number_correct_answers = {res}
                    WHERE id = {self.number_variant}""").fetchall()

        for i in self.id_number:
            cur.execute(f"""UPDATE ansewers
            SET input = ''
            WHERE id = {i}""").fetchall()

        self.con.commit()
        return res

    def save_answer(self):
        cur = self.con.cursor()
        new_date = (self.name_input.text(), self.number_variant, self.flag)

        cur.execute(f"""UPDATE ansewers
            SET input = '{new_date[0]}'
            WHERE id = {self.id_number[self.flag - 1]}""")

        self.con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainProduct()
    ex.show()
    sys.exit(app.exec_())