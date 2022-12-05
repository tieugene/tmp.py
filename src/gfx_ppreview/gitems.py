"""gfx_ppreview/gitems: QGraphicsItem successors"""
# 1. std
from typing import List
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, \
    QWidget, QStyleOptionGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsPolygonItem, \
    QGraphicsTextItem
# 3. local
from consts import DEBUG, FONT_MAIN, W_LABEL, HEADER_TXT, H_BOTTOM, H_HEADER
from data import SAMPLES, TICS, ASigSuit, BSigSuit, BarSuit, BarSuitListType, bs_is_bool, bs_to_html
# from utils import qsize2str


# ---- Shortcuts ----
class ThinPen(QPen):
    """Non-scalable QPen"""

    def __init__(self, color: Qt.GlobalColor, style: Qt.PenStyle = None):
        super().__init__(color)
        self.setCosmetic(True)
        if style is not None:
            self.setStyle(style)


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


class RectTextItem(QGraphicsItemGroup):  # FIXME: rm
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


class AGraphItem(QGraphicsPathItem):
    __y: List[float]
    __y0: float
    __y0pen: QPen

    def __init__(self, d: ASigSuit):
        super().__init__()
        self.__y = [-v for v in d.nvalue]
        self.__y0px = 0  # current Y=0, px
        self.__y0pen = ThinPen(Qt.GlobalColor.darkGray, Qt.PenStyle.DotLine)  # FIXME: tmp
        self.setPen(ThinPen(d.color))
        pp = QPainterPath()
        pp.addPolygon(QPolygonF([QPointF(x, y) for x, y in enumerate(self.__y)]))   # default: x=0..SAMPLES, y=0..1
        self.setPath(pp)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """For debug only"""
        super().paint(painter, option, widget)
        # FIXME: tmp
        # painter.setPen(self.__y0pen)
        # print(option.rect.left(), option.rect.right(), option.rect.top(), option.rect.bottom())
        # painter.drawLine(option.rect.left(), self.__y0px, option.rect.right(), self.__y0px)
        if DEBUG:
            painter.setPen(self.pen())
            painter.drawRect(option.rect)

    def set_size(self, s: QSizeF):
        """
        :param s: Dest size of graph (e.g. 1077 x 28/112 for Landscape
        """
        self.prepareGeometryChange()  # not helps
        # - prepare: X-scale factor, Y-shift, Y-scale factor
        kx = s.width() / (len(self.__y) - 1)  # 13-1=12
        ky = s.height()
        self.__y0px = round(-min(0, min(self.__y)) * ky)
        pp = self.path()
        for i in range(pp.elementCount()):
            pp.setElementPositionAt(i, i * kx, self.__y[i] * ky + self.__y0px)
        self.setPath(pp)


class BGraphItem(QGraphicsPolygonItem):
    __y: List[float]

    def __init__(self, d: BSigSuit):
        super().__init__()
        self.__y = [-v for v in d.nvalue]
        self.setPen(ThinPen(d.color))
        self.setBrush(QBrush(d.color, Qt.BrushStyle.Dense1Pattern))  #
        self.__set_size(1, 1)

    def set_size(self, s: QSizeF):
        """
        L: s=(1077 x 28/112)
        :param s: Size of graph
        """
        self.prepareGeometryChange()  # not helps
        self.__set_size(s.width() / (len(self.__y) - 1), s.height())

    def __set_size(self, kx: float, ky: float):
        point_list = [QPointF(x * kx, y * ky) for x, y in enumerate(self.__y)]
        if int(self.__y[0]) == 0:  # always start with 0
            point_list.insert(0, QPointF(0, ky))
        if int(self.__y[-1]) == 0:  # always end with 0
            point_list.append(QPointF((len(self.__y)-1) * kx, ky))
        self.setPolygon(QPolygonF(point_list))


# ---- QGraphicsView
class GraphViewBase(QGraphicsView):
    """Basic QGraphicsView parent (auto-resizing)
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize __view to content)
        # super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max
        # Note: KeepAspectRatioByExpanding is extremally CPU-greedy


class BarGraphView(GraphViewBase):
    """# <= QAbstractScrollArea <= QFrame
    Used in: main.TableView
    """
    def __init__(self, bs: BarSuit):
        super().__init__()
        self.setScene(QGraphicsScene())
        for ss in bs:
            self.scene().addItem(BGraphItem(ss) if ss.is_bool else AGraphItem(ss))
        y0item = QGraphicsLineItem(0, 0, SAMPLES, 0)
        y0item.setPen(ThinPen(Qt.GlobalColor.black, Qt.PenStyle.DotLine))
        self.scene().addItem(y0item)


# ---- Containers
class HeaderItem(RectTextItem):
    __plot: 'PlotBase'

    def __init__(self, plot: 'PlotBase'):
        super().__init__(HEADER_TXT)
        self.__plot = plot
        self.update_size()

    def update_size(self):
        self.set_width(self.__plot.w_full)


class BarLabelItem(QGraphicsItemGroup):
    """Label part of signal bar"""
    __txt: QGraphicsTextItem

    def __init__(self, bs: BarSuit):
        super().__init__()
        self.__txt = QGraphicsTextItem()
        self.__txt.setFont(FONT_MAIN)
        self.__txt.setHtml(bs_to_html(bs))
        self.addToGroup(self.__txt)
        # RectTextItem(d.name, d.color)

    def boundingRect(self) -> QRectF:  # update_size() fix
        return self.childrenBoundingRect()

    def set_width(self, w: int):
        ...

    def set_size(self, s: QSizeF):
        ...


class BarGraphItem(QGraphicsItemGroup):
    """Graph part of signal bar"""
    def __init__(self, bs: BarSuit):
        super().__init__()
        # BGraphItem(d) if d.is_bool else AGraphItem(d)

    def boundingRect(self) -> QRectF:  # update_size() fix
        return self.childrenBoundingRect()

    def set_size(self, s: QSizeF):
        ...


class RowItem(QGraphicsItemGroup):
    """For View/Print"""
    __plot: 'PlotBase'  # ref to father
    __label: BarLabelItem  # left side
    __graph: BarGraphItem  # right side
    __y0line: QGraphicsLineItem  # Y=0 line
    __uline: QGraphicsLineItem  # underline
    __wide: bool  # A/B indictor

    def __init__(self, bs: BarSuit, plot: 'PlotBase'):
        super().__init__()
        self.__plot = plot
        self.__label = BarLabelItem(bs)
        self.__graph = BarGraphItem(bs)
        self.__y0line = QGraphicsLineItem()
        self.__y0line.setPen(ThinPen(Qt.GlobalColor.gray, Qt.PenStyle.DotLine))
        self.__uline = QGraphicsLineItem()
        self.__uline.setPen(ThinPen(Qt.GlobalColor.black, Qt.PenStyle.DashLine))
        self.__wide = not bs_is_bool(bs)
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
        s = QSizeF(w, h-1)
        self.__label.set_size(s)
        self.__graph.set_size(s)
        self.__y0line.setLine(0, h/2, self.__plot.w_full, h/2)
        self.__uline.setLine(0, h-1, self.__plot.w_full, h-1)


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

    def __init__(self, bslist: BarSuitListType, plot: 'PlotBase'):
        super().__init__()
        self.__rowitem = list()
        y = 0
        for bs in bslist:
            item = RowItem(bs, plot)
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

    def __init__(self, bslist: BarSuitListType, plot: 'PlotBase'):
        super().__init__()
        self.__canvas = TableCanvas(plot)
        self.__payload = TablePayload(bslist, plot)
        self.__payload.setY(H_HEADER)
        self.addItem(self.__canvas)
        self.addItem(self.__payload)

    def update_sizes(self):
        self.__canvas.update_sizes()
        self.__payload.update_sizes()
        self.setSceneRect(self.itemsBoundingRect())
