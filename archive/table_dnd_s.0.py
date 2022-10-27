#!/bin/env python3
"""Drag-n-drop rows in table (singlerow version).
Powered by [Stackoverflow](https://stackoverflow.com/questions/26227885/drag-and-drop-rows-within-qtablewidget)
"""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QWidget, QHBoxLayout, \
    QApplication


class TableWidgetDragRows(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.SingleSelection)  # multiselect; or .SingleSelection?
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            dst_row_num = self.__drop_on(event)
            src_row_num = self.selectedItems()[0].row()
            src_row_data = [QTableWidgetItem(self.item(src_row_num, column_index)) for column_index in range(self.columnCount())]
            self.removeRow(src_row_num)
            if src_row_num < dst_row_num:
                dst_row_num -= 1
            self.insertRow(dst_row_num)
            for column_index, column_data in enumerate(src_row_data):
                self.setItem(dst_row_num, column_index, column_data)
            event.accept()
            self.reset()
            self.item(dst_row_num, 0).setSelected(True)
            self.item(dst_row_num, 1).setSelected(True)
        super().dropEvent(event)

    def __drop_on(self, event) -> int:
        index = self.indexAt(event.pos())
        if not index.isValid():  # below last
            return self.rowCount()
        return index.row() + 1 if self.__is_below(event.pos(), index) else index.row()

    def __is_below(self, pos, index) -> bool:
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        return rect.contains(pos, True) \
               and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) \
               and pos.y() >= rect.center().y()


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.table_widget = TableWidgetDragRows()
        layout.addWidget(self.table_widget)

        # setup table widget
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['Type', 'Name'])

        items = [('Zero', 'Toyota'), ('One', 'RV'), ('Two', 'Beetle'), ('Three', 'Chevy'), ('Four', 'BMW')]
        self.table_widget.setRowCount(len(items))
        for i, (color, model) in enumerate(items):
            self.table_widget.setItem(i, 0, QTableWidgetItem(color))
            self.table_widget.setItem(i, 1, QTableWidgetItem(model))

        self.resize(400, 400)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
