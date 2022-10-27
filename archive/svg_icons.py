"""Test actions with SVG icons.
QCtion(QIcon(...)):
- file
- QPixmap(...):
  - QSvgRenderer(...)
    - QXmlStreamReader(QByteArea)
    - QByteArea()
[RTFM](https://www.qtcentre.org/threads/7321-Loading-SVG-icons) (QSvgRenderer)
"""
import sys

from PyQt5.QtCore import QXmlStreamReader, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication

icon1_src = '''<?xml version="1.0" encoding="utf-8"?>
<svg width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <path
        d="M 1 1 H 19 V 19 H 1 Z L 19 19 M 1 19 L 19 1"
        stroke-width="1" stroke="black" fill="white"
    />
</svg>'''
icon2_src = '''<?xml version="1.0" encoding="utf-8"?>
<svg width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <polyline points="5,6 10,1 15,6" stroke-width="1" stroke="black" fill="none"/>
    <polyline points="5,14 10,19 15,14" stroke-width="1" stroke="black" fill="none"/>
</svg>'''
icon_curve = '''<?xml version="1.0" encoding="utf-8"?>
<svg width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <path d="M1,10 Q5,0 10,10 T19,10" stroke-width="1" stroke="black" fill="none"/>
</svg>'''


def svg2icon(svg: str) -> QIcon:
    svg_renderer = QSvgRenderer(QXmlStreamReader(svg))
    pix = QPixmap(svg_renderer.defaultSize())
    pix.fill(Qt.transparent)
    svg_renderer.render(QPainter(pix))
    return QIcon(pix)


class MainWindow(QMainWindow):
    act_exit: QAction
    act_act_vzoom_in: QAction
    act_act_vzoom_out: QAction

    def __init__(self):
        super().__init__()
        # self.__set_icons()
        self.__set_actions()
        self.__set_menubar()
        self.__set_toolbar()

    def __set_actions(self):
        self.act_exit = QAction(QIcon.fromTheme("application-exit"),
                                "E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.act_vzoom_in = QAction(QIcon.fromTheme("zoom-in"), "V-Zoom &in", self)
        self.act_vzoom_out = QAction(svg2icon(icon_curve), "V-Zoom &out", self)

    def __set_menubar(self):
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_exit)
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(self.act_vzoom_in)
        menu_view.addAction(self.act_vzoom_out)

    def __set_toolbar(self):
        tb = self.addToolBar("Main")
        tb.addAction(self.act_vzoom_in)
        tb.addAction(self.act_vzoom_out)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # window.resize(400, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
