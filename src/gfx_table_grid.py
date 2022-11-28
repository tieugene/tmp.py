"""Signal table.
GridTable version
Resume: setStretch, setHeight not work
Note: now stretch factors depends on (label/graph).boundingRect() ratio
"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt, QSizeF, QRectF
from PyQt5.QtWidgets import QGraphicsWidget, QGraphicsGridLayout, QGraphicsLayoutItem, QGraphicsItem
# 3. local
from gfx_table_widgets import W_LABEL, DataValue, RectTextItem, GraphItem


class TableItem(QGraphicsWidget):
    class LayoutItem(QGraphicsLayoutItem):
        """QGraphicsLayoutItem(QGraphicsItem) based."""
        __subj: QGraphicsItem  # must live

        def __init__(self, subj: QGraphicsItem):
            super().__init__()
            self.__subj = subj
            self.setGraphicsItem(self.__subj)
            # experiments:
            self.__subj.bordered = True
            # self.__subj.setFlag(QGraphicsItem.ItemClipsToShape, True)
            # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
            # self.__subj.setFlag(QGraphicsItem.ItemContainsChildrenInShape)
            # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # ✗

        def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
            if which in {Qt.SizeHint.MinimumSize, Qt.SizeHint.PreferredSize}:
                return self.__subj.boundingRect().size()
            return constraint

        def setGeometry(self, rect: QRectF):  # Warn: Calling once on init
            self.__subj.prepareGeometryChange()
            super().setGeometry(rect)
            self.__subj.setPos(rect.topLeft())

    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsGridLayout()
        # lt.addItem(TextGfxWidget(HEADER_TXT), 0, 0, 1, 2)  # ✗ (span)
        for row, d in enumerate(dlist):
            lt.addItem(self.LayoutItem(RectTextItem(W_LABEL, d[0], d[2])), row, 0)  # A: GridTextItem, B: TextGfxWidget
            lt.addItem(self.LayoutItem(GraphItem(d)), row, 1)
            # lt.setRowFixedHeight(row, 100)  # works strange
            # lt.setRowSpacing(row, 0)  # ✗
            lt.setRowStretchFactor(row, row)  # ✗
        # Layout tuning
        lt.setSpacing(0)
        lt.setContentsMargins(0, 0, 0, 0)
        # lt.setRowFixedHeight(0, 50)  # ✗
        self.setLayout(lt)
