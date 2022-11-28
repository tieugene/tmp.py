#!/usr/bin/env python3
"""Test of rescaling print (and multipage).
- [ ] TODO: Grid: grid lines (paint over layout)
- [ ] TODO: Footer
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsView,\
    QGraphicsScene, QDialog, QVBoxLayout
# 3. local
from gfx_table_widgets import DATA, GraphView
from gfx_table_line import TableItem


class Plot(QGraphicsView):
    def __init__(self, parent: 'ViewWindow'):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.scene().addItem(TableItem(DATA[:3]))

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max


class ViewWindow(QDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(Plot(self))


class MainWidget(QTableWidget):
    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setRowCount(len(DATA))
        self.setColumnCount(2)
        for r, d in enumerate(DATA):
            self.setItem(r, 0, (QTableWidgetItem(d[0])))
            self.setCellWidget(r, 1, GraphView(d))


class MainWindow(QMainWindow):
    view: ViewWindow

    def __init__(self):
        super().__init__()
        self.setCentralWidget(MainWidget(self))
        self.view = ViewWindow(self)
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(QAction(QIcon.fromTheme("view-fullscreen"), "&View", self, shortcut="Ctrl+V",
                                    triggered=self.__view))
        menu_file.addAction(QAction(QIcon.fromTheme("document-print-preview"), "&Print", self, shortcut="Ctrl+P",
                                    triggered=self.__print))
        menu_file.addAction(QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                    triggered=self.close))
        self.menuBar().setVisible(True)

    def __view(self):
        self.view.show()

    def __print(self):
        ...


def main() -> int:
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    # mw.resize(600, 600)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
