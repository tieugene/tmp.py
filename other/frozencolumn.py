#!/usr/bin/env python
from PyQt5.QtCore import QFile, QFileInfo, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView


class FrozenColumn(QTableView):
    def __init__(self, parent: QTableView):
        super().__init__(parent)
        self.setModel(parent.model())
        self.setFocusPolicy(Qt.NoFocus)
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setStyleSheet(
            'QTableView { border: none; background-color: #8EDE21; selection-background-color: #999;}'
            )
        self.setSelectionModel(parent.selectionModel())
        for col in range(1, parent.model().columnCount()):
            self.setColumnHidden(col, True)
        self.setColumnWidth(0, parent.columnWidth(0))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerPixel)


class FreezeTableWidget(QTableView):
    __frozenTableView: FrozenColumn

    def __init__(self, model):
        super().__init__()
        # init data
        self.setModel(model)
        self.__frozenTableView = FrozenColumn(self)
        # self._frozenTableView.show()
        # self.update_frozen_table_geometry()
        # tuning
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.viewport().stackUnder(self.__frozenTableView)
        # signal connections
        self.horizontalHeader().sectionResized.connect(self.slot_update_section_width)
        self.verticalHeader().sectionResized.connect(self.slot_update_section_height)
        self.__frozenTableView.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(self.__frozenTableView.verticalScrollBar().setValue)

    def slot_update_section_width(self, logical_idx, _, new_size):
        if logical_idx == 0:
            self.__frozenTableView.setColumnWidth(0, new_size)
            self.update_frozen_table_geometry()

    def slot_update_section_height(self, logical_idx, _, new_size):
        self.__frozenTableView.setRowHeight(logical_idx, new_size)

    def resizeEvent(self, event):
        super(FreezeTableWidget, self).resizeEvent(event)
        self.update_frozen_table_geometry()

    def moveCursor(self, cursor_action, modifiers):
        current = super(FreezeTableWidget, self).moveCursor(cursor_action, modifiers)
        if (cursor_action == self.MoveLeft and
                self.current.column() > 0 and
                self.visualRect(current).topLeft().x() < self.__frozenTableView.columnWidth(0)):
            new_value = (self.horizontalScrollBar().value() +
                         self.visualRect(current).topLeft().x() -
                         self.__frozenTableView.columnWidth(0))
            self.horizontalScrollBar().setValue(new_value)
        return current

    def scrollTo(self, index, hint):
        if index.column() > 0:
            super(FreezeTableWidget, self).scrollTo(index, hint)

    def update_frozen_table_geometry(self):
        self.__frozenTableView.setGeometry(
            self.verticalHeader().width() + self.frameWidth(),
            self.frameWidth(), self.columnWidth(0),
            self.viewport().height() + self.horizontalHeader().height())


def main(args):
    def split_and_strip(src, splitter):
        return [s.strip() for s in src.split(splitter)]

    app = QApplication(args)
    model = QStandardItemModel()
    file = QFile(QFileInfo(__file__).absolutePath() + '/grades.txt')
    if file.open(QFile.ReadOnly):
        line = file.readLine(200).decode('utf-8')
        header = split_and_strip(line, ',')
        model.setHorizontalHeaderLabels(header)
        row = 0
        while file.canReadLine():
            line = file.readLine(200).decode('utf-8')
            if not line.startswith('#') and ',' in line:
                fields = split_and_strip(line, ',')
                for col, field in enumerate(fields):
                    new_item = QStandardItem(field)
                    model.setItem(row, col, new_item)
                row += 1
    file.close()
    table_view = FreezeTableWidget(model)
    table_view.setWindowTitle("Frozen Column Example")
    table_view.resize(560, 680)
    table_view.show()
    return app.exec_()


if __name__ == '__main__':
    import sys

    main(sys.argv)
