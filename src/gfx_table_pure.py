#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsView,\
    QGraphicsScene, QDialog, QVBoxLayout, QGraphicsItem, QGraphicsItemGroup
# 3. local
from gfx_table_widgets import DataValue, GraphItem, TextItem, GraphView

# x. const
PPP = 5  # plots per page
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line."
W_LABEL = 50  # width of label column
DATA = (  # name, x-offset, color
    ("Signal 1", 0, Qt.GlobalColor.black),
    ("Signal 2", 1, Qt.GlobalColor.red),
    ("Signal 3", 2, Qt.GlobalColor.blue),
    ("Signal 4", 3, Qt.GlobalColor.green),
    ("Signal 5", 4, Qt.GlobalColor.yellow),
    ("Signal 6", 5, Qt.GlobalColor.magenta),
)


class ViewWindow(QDialog):
    class Plot(QGraphicsView):
        class RowItem(QGraphicsItemGroup):
            def __init__(self, d: DataValue, parent: QGraphicsItem = None):
                super().__init__(parent)
                label = TextItem(d[0], d[2])
                self.addToGroup(label)
                graph = GraphItem(d)
                graph.setX(W_LABEL)
                graph.bordered = True
                self.addToGroup(graph)

        def __init__(self, parent: 'ViewWindow' = None):
            super().__init__(parent)
            self.setScene(QGraphicsScene())
            # header = TextItem(HEADER_TXT)
            # y = header.boundingRect().height()
            # self.scene().addItem(header)
            y = 0
            for r, d in enumerate(DATA[:3]):
                item = self.RowItem(d)
                item.setY(y)
                self.scene().addItem(item)
                y += item.boundingRect().height()

        def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max

    def __init__(self, parent: 'MainWindows'):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.Plot(self))


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
