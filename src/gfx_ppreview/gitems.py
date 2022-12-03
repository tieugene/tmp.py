"""gfx_ppreview/gitems: QGraphicsItem successors"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QPainter
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, \
    QWidget, QStyleOptionGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLineItem
# 3. local
from consts import DEBUG, FONT_MAIN, W_LABEL, HEADER_TXT,  H_BOTTOM, H_HEADER
from data import SAMPLES, TICS, DataValue, mk_sin, mk_meander


class ThinPen(QPen):
    """Non-scalable QPen"""
    def __init__(self, color: Qt.GlobalColor):
        super().__init__(color)
        self.setCosmetic(True)


# ---- QGraphicsItem ----
class TextItem(QGraphicsSimpleTextItem):
    """
    Non-scalable plain text
    Warn: on resize:
    - not changed: boundingRect(), pos(), scenePos()
    - not call: deviceTransform(), itemTransform(), transform(), boundingRegion()
    - call: paint()
    :todo: add align
    """
    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__(txt)
        self.setFont(FONT_MAIN)
        if color:
            self.setBrush(color)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)


class TCTextItem(TextItem):
    """Top-H=centered text"""
    __br: QRectF  # boundingRect()

    def __init__(self, txt: str):
        super().__init__(txt)
        self.__br = super().boundingRect()

    def boundingRect(self) -> QRectF:
        self.__br = super().boundingRect()
        self.__br.translate(-self.__br.width() / 2, 0.0)
        return self.__br

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """H-center"""
        painter.translate(self.__br.left(), -self.__br.top())
        super().paint(painter, option, widget)


class RectTextItem(QGraphicsItemGroup):
    class ClipedTextITem(TextItem):
        def __init__(self, txt: str, color: Qt.GlobalColor = None):
            super().__init__(txt, color)

        def boundingRect(self) -> QRectF:  # fix for upper br: return clipped size
            if self.isClipped():
                return self.parentItem().boundingRect()
            return super().boundingRect()

    """Text in border.
    Result: something strange."""
    text: ClipedTextITem
    rect: QGraphicsRectItem

    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__()
        # text
        self.text = self.ClipedTextITem(txt, color)
        self.addToGroup(self.text)
        # rect
        self.rect = QGraphicsRectItem(self.text.boundingRect())  # default size == text size
        self.rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # YES!!!
        if DEBUG:
            pen = ThinPen(color or Qt.GlobalColor.black)
        else:
            pen = ThinPen(Qt.GlobalColor.transparent)
        self.rect.setPen(pen)
        self.addToGroup(self.rect)
        # clip label
        self.text.setParentItem(self.rect)

    def boundingRect(self) -> QRectF:  # set_size() fix
        return self.childrenBoundingRect()

    def set_width(self, w: float):
        r = self.rect.rect()
        r.setWidth(w)
        self.rect.setRect(r)

    def set_height(self, h: float):
        r = self.rect.rect()
        r.setHeight(h)
        self.rect.setRect(r)

    def set_size(self, s: QSizeF):  # self.rect.rect() = self.rect.boundingRect() + 1
        self.prepareGeometryChange()  # not helps
        r = self.rect.rect()
        r.setWidth(s.width())
        r.setHeight(s.height())
        self.rect.setRect(r)


class GraphItem(QGraphicsPathItem):
    __y: List[float]

    def __init__(self, d: DataValue):
        super().__init__()
        self.__y = mk_sin(d[1]) if d[3] else mk_meander(d[1])
        self.setPen(ThinPen(d[2]))
        pp = QPainterPath()
        # default: x=0..SAMPLES, y=0..1
        pp.addPolygon(QPolygonF([QPointF(x, y) for x, y in enumerate(self.__y)]))  # default
        self.setPath(pp)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """For debug only"""
        super().paint(painter, option, widget)
        if DEBUG:
            painter.setPen(self.pen())
            painter.drawRect(option.rect)

    def set_size(self, s: QSizeF):
        """

        :param s: Size of graph
        :return:
        """
        self.prepareGeometryChange()  # not helps
        pp = self.path()
        step = s.width() / (pp.elementCount() - 1)
        for i in range(pp.elementCount()):
            pp.setElementPositionAt(i, i * step, self.__y[i] * s.height())
        self.setPath(pp)


# ---- QGraphicsView
class GraphViewBase(QGraphicsView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize __view to content)
        # super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max
        # Note: KeepAspectRatioByExpanding is extremally CPU-greedy


class GraphView(GraphViewBase):  # <= QAbstractScrollArea <= QFrame
    def __init__(self, d: DataValue):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.scene().addItem(GraphItem(d))


# ---- Containers
class HeaderItem(RectTextItem):
    __plot: 'PlotBase'

    def __init__(self, plot: 'PlotBase'):
        super().__init__(HEADER_TXT)
        self.__plot = plot
        self.update_size()

    def update_size(self):
        self.set_width(self.__plot.w_full)


class RowItem(QGraphicsItemGroup):
    __plot: 'PlotBase'  # ref to father
    __label: RectTextItem  # left side
    __graph: GraphItem  # right side
    __uline: QGraphicsLineItem  # underline
    __wide: bool  # A/B indictor

    def __init__(self, d: DataValue, plot: 'PlotBase'):
        super().__init__()
        self.__plot = plot
        self.__label = RectTextItem(d[0], d[2])
        self.__graph = GraphItem(d)
        self.__uline = QGraphicsLineItem()
        self.__wide = d[3]
        # initial positions/sizes
        self.__label.set_width(W_LABEL)
        self.__graph.setX(W_LABEL + 1)
        self.update_size()
        self.addToGroup(self.__label)
        self.addToGroup(self.__graph)
        self.addToGroup(self.__uline)

    def boundingRect(self) -> QRectF:  # update_size() fix
        return self.childrenBoundingRect()

    def update_size(self):
        w = self.__plot.w_full - W_LABEL
        h = self.__plot.h_row_base * (1 + int(self.__wide) * 3)  # 28/112, 42/168
        self.__label.set_height(h)
        self.__graph.set_size(QSizeF(w, h))
        self.__uline.setLine(0, h, self.__plot.w_full, h)


class TableCanvas(QGraphicsItemGroup):
    """Table frame with:
    - header
    - border
    - columns separator
    - bottom underline
    - bottom scale
    - grid
    """

    class GridItem(QGraphicsItemGroup):
        __plot: 'PlotBase'
        __x: float
        __line: QGraphicsLineItem
        __text: TCTextItem

        def __init__(self, x: float, num: int, plot: 'PlotBase'):
            super().__init__()
            self.__x = x
            self.__plot = plot
            self.__line = QGraphicsLineItem()
            self.__line.setPen(ThinPen(Qt.GlobalColor.lightGray))
            self.__text = TCTextItem(str(num))
            # layout
            self.addToGroup(self.__line)
            self.addToGroup(self.__text)

        def boundingRect(self) -> QRectF:  # update_size() fix
            return self.childrenBoundingRect()

        def update_size(self):
            x = W_LABEL + (self.__plot.w_full - W_LABEL) * self.__x / SAMPLES
            y = self.__plot.h_full - H_BOTTOM
            self.__line.setLine(x, H_HEADER, x, y)
            self.__text.setPos(x, y)

    __plot: 'PlotBase'
    __header: HeaderItem
    __frame: QGraphicsRectItem  # external border; TODO: clip all inners (header, tic labels) by this
    __colsep: QGraphicsLineItem  # columns separator
    __btmsep: QGraphicsLineItem  # bottom separator
    __grid: List[GridItem]  # tics (v-line+label)

    def __init__(self, plot: 'PlotBase'):
        super().__init__()
        self.__plot = plot
        self.__header = HeaderItem(plot)
        pen = ThinPen(Qt.GlobalColor.gray)
        self.__frame = QGraphicsRectItem()
        self.__frame.setPen(pen)
        self.__frame.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
        self.__colsep = QGraphicsLineItem()
        self.__colsep.setPen(pen)
        self.__btmsep = QGraphicsLineItem()
        self.__btmsep.setPen(pen)
        # layout
        self.addToGroup(self.__header)
        self.addToGroup(self.__frame)
        self.addToGroup(self.__colsep)
        self.addToGroup(self.__btmsep)
        # grid
        self.__grid = list()
        for x, num in TICS.items():
            self.__grid.append(self.GridItem(x, num, plot))
            self.addToGroup(self.__grid[-1])
            self.__grid[-1].setParentItem(self.__frame)
        # go
        self.update_sizes()

    def boundingRect(self) -> QRectF:  # update_sizes() fix
        return self.childrenBoundingRect()

    def update_sizes(self):
        self.__header.update_size()
        self.__frame.setRect(0, H_HEADER, self.__plot.w_full, self.__plot.h_full - H_HEADER)
        self.__colsep.setLine(W_LABEL, H_HEADER, W_LABEL, self.__plot.h_full - H_BOTTOM)
        self.__btmsep.setLine(0, self.__plot.h_full - H_BOTTOM, self.__plot.w_full, self.__plot.h_full - H_BOTTOM)
        for g in self.__grid:
            g.update_size()


class TablePayload(QGraphicsItemGroup):
    __rowitem: list[RowItem]

    """Just rows with underlines"""
    def __init__(self, dlist: List[DataValue], plot: 'PlotBase'):
        super().__init__()
        self.__rowitem = list()
        y = 0
        for d in dlist:
            item = RowItem(d, plot)
            item.setY(y)
            y += item.boundingRect().height()
            self.__rowitem.append(item)
            self.addToGroup(self.__rowitem[-1])

    def boundingRect(self) -> QRectF:  # update_sizes() fix
        return self.childrenBoundingRect()

    def update_sizes(self):
        y = self.__rowitem[0].boundingRect().y()
        for item in self.__rowitem:
            item.update_size()
            item.setY(y)
            y += item.boundingRect().height()


class PlotScene(QGraphicsScene):
    __canvas: TableCanvas
    __payload: TablePayload

    def __init__(self, data: List[DataValue], plot: 'PlotBase'):
        super().__init__()
        self.__canvas = TableCanvas(plot)
        self.__payload = TablePayload(data, plot)
        self.__payload.setY(H_HEADER)
        self.addItem(self.__canvas)
        self.addItem(self.__payload)

    def update_sizes(self):
        self.__canvas.update_sizes()
        self.__payload.update_sizes()
        self.setSceneRect(self.itemsBoundingRect())
