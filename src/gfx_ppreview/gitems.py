"""gfx_ppreview/gitems: QGraphicsItem successors"""
# 1. std
from typing import List, Union
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF, QSize
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QPainter, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, \
    QWidget, QStyleOptionGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsPolygonItem, \
    QGraphicsTextItem
# 3. local
from consts import DEBUG, FONT_MAIN, W_LABEL, HEADER_TXT, H_BOTTOM, H_HEADER
from data import SAMPLES, TICS, ASigSuit, BSigSuit, BarSuit, BarSuitList, bs_is_bool, bs_to_html
from utils import qsize2str


# ---- Shortcuts ----
# simple successors with some predefines
class ThinPen(QPen):
    """Non-scalable QPen"""

    def __init__(self, color: Qt.GlobalColor, style: Qt.PenStyle = None):
        super().__init__(color)
        self.setCosmetic(True)
        if style is not None:
            self.setStyle(style)


class PlainTextItem(QGraphicsSimpleTextItem):
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


class RichTextItem(QGraphicsTextItem):
    """Non-scalable rich text"""
    def __init__(self, txt: str = None):
        super().__init__(txt)
        self.setFont(FONT_MAIN)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)


class GroupItem(QGraphicsItemGroup):
    def __init__(self):
        super().__init__()

    def boundingRect(self) -> QRectF:  # set_size() fix
        return self.childrenBoundingRect()


# ---- QGraphicsItem ----
class TCPlainTextItem(PlainTextItem):
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
        painter.translate(self.__br.left(), -self.__br.top())  # shift to top
        super().paint(painter, option, widget)


class ClipedPlainTextItem(PlainTextItem):
    """Clipped plain text.
    Used in: RecTextItem"""
    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__(txt, color)

    def boundingRect(self) -> QRectF:  # fix for upper br: return clipped size
        if self.isClipped():
            return self.parentItem().boundingRect()
        return super().boundingRect()


class ClipedRichTextItem(RichTextItem):
    """Clipped rich text."""
    def __init__(self, txt: str = None):
        super().__init__(txt)

    def boundingRect(self) -> QRectF:  # fix for upper br: return clipped size
        if self.isClipped():
            return self.parentItem().boundingRect()
        return super().boundingRect()


class AGraphItem(QGraphicsPathItem):
    __y: List[float]

    def __init__(self, d: ASigSuit):
        super().__init__()
        self.__y = [-v for v in d.nvalue]
        self.setPen(ThinPen(d.color))
        pp = QPainterPath()
        pp.addPolygon(QPolygonF([QPointF(x, y) for x, y in enumerate(self.__y)]))   # default: x=0..SAMPLES, y=0..1
        self.setPath(pp)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """For debug only"""
        super().paint(painter, option, widget)
        if DEBUG:
            painter.setPen(self.pen())
            painter.drawRect(option.rect)

    @property
    def ymin(self) -> float:
        return min(self.__y)

    @property
    def ymax(self) -> float:
        return max(self.__y)

    def set_size(self, s: QSizeF):
        """
        :param s: Dest size of graph (e.g. 1077 x 28/112 for Landscape
        """
        self.prepareGeometryChange()  # not helps
        # - prepare: X-scale factor, Y-shift, Y-scale factor
        kx = s.width() / (len(self.__y) - 1)  # 13-1=12
        ky = s.height()
        y0px = round(-min(0.0, self.ymin) * ky)
        pp = self.path()
        for i in range(pp.elementCount()):
            pp.setElementPositionAt(i, i * kx, self.__y[i] * ky + y0px)
        self.setPath(pp)


class BGraphItem(QGraphicsPolygonItem):
    __y: List[float]

    def __init__(self, d: BSigSuit):
        super().__init__()
        self.__y = [-v for v in d.nvalue]
        self.setPen(ThinPen(d.color))
        self.setBrush(QBrush(d.color, Qt.BrushStyle.Dense1Pattern))  #
        self.__set_size(1, 1)

    @property
    def ymin(self) -> float:
        return min(self.__y)

    @property
    def ymax(self) -> float:
        return max(self.__y)

    def set_size(self, s: QSize):
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
class RectTextItem(GroupItem):  # FIXME: rm
    """Text in border.
    Used in: HeaderItem
    Result: something strange."""

    text: Union[ClipedPlainTextItem, ClipedRichTextItem]
    rect: QGraphicsRectItem

    def __init__(self, txt: Union[ClipedPlainTextItem, ClipedRichTextItem]):
        super().__init__()
        # text
        self.text = txt
        self.addToGroup(self.text)
        # rect
        self.rect = QGraphicsRectItem(self.text.boundingRect())  # default size == text size
        self.rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # YES!!!
        self.rect.setPen(ThinPen(Qt.GlobalColor.black if DEBUG else Qt.GlobalColor.transparent))
        self.addToGroup(self.rect)
        # clip label
        self.text.setParentItem(self.rect)

    def set_width(self, w: float):
        self.prepareGeometryChange()  # not helps
        r = self.rect.rect()
        r.setWidth(w)
        self.rect.setRect(r)

    def set_height(self, h: float):
        self.prepareGeometryChange()  # not helps
        r = self.rect.rect()
        r.setHeight(h)
        self.rect.setRect(r)

    def set_size(self, s: QSizeF):  # self.rect.rect() = self.rect.boundingRect() + 1
        self.prepareGeometryChange()  # not helps
        r = self.rect.rect()
        r.setWidth(s.width())
        r.setHeight(s.height())
        self.rect.setRect(r)


class HeaderItem(RectTextItem):
    __plot: 'PlotBase'

    def __init__(self, plot: 'PlotBase'):
        super().__init__(ClipedPlainTextItem(HEADER_TXT))
        self.__plot = plot
        self.update_size()

    def update_size(self):
        self.set_width(self.__plot.w_full)


class BarLabelItem(RectTextItem):
    """Label part of signal bar"""

    def __init__(self, bs: BarSuit):
        super().__init__(ClipedRichTextItem())
        self.text.setHtml(bs_to_html(bs))
        self.set_width(W_LABEL)


class BarGraphItem(GroupItem):
    """Graph part of signal bar"""
    __graph: List[Union[AGraphItem, BGraphItem]]
    __y0line: QGraphicsLineItem  # Y=0 line
    __ymin: float
    __ymax: float

    def __init__(self, bs: BarSuit):
        super().__init__()
        self.__graph = list()
        self.__ymin = self.__ymax = 0.0  # same as self.__y0line
        for d in bs:
            self.__graph.append(BGraphItem(d) if d.is_bool else AGraphItem(d))
            self.addToGroup(self.__graph[-1])
            self.__ymin = min(self.__ymin, self.__graph[-1].ymin)
            self.__ymax = max(self.__ymax, self.__graph[-1].ymax)
        self.__y0line = QGraphicsLineItem()
        self.__y0line.setPen(ThinPen(Qt.GlobalColor.gray, Qt.PenStyle.DotLine))
        self.__y0line.setLine(0, 0, SAMPLES, 0)
        self.addToGroup(self.__y0line)

    def __set_size_via_tr(self, s: QSize):
        """Resize self using QTransform"""
        ky = s.height() / (self.__ymax - self.__ymin)
        # self.resetTransform()  # not helps
        self.setTransform(QTransform().translate(0, -self.__ymin * ky))
        self.setTransform(QTransform().scale(s.width() / SAMPLES, ky), True)
        self.update()

    def set_size(self, s: QSize):
        """Note: Children boundingRect() includes pen width.
        :todo: chk pen width
        """
        for gi in self.__graph:
            gi.set_size(s)
        y0px = -self.__ymin * s.height()
        self.__y0line.setLine(0, y0px, s.width(), y0px)


class RowItem(GroupItem):
    """For View/Print"""
    __plot: 'PlotBase'  # ref to father
    __label: BarLabelItem  # left side
    __graph: BarGraphItem  # right side
    __uline: QGraphicsLineItem  # underline
    __wide: bool  # A/B indictor

    def __init__(self, bs: BarSuit, plot: 'PlotBase'):
        super().__init__()
        self.__plot = plot
        self.__label = BarLabelItem(bs)
        self.__graph = BarGraphItem(bs)
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

    def update_size(self):
        w = self.__plot.w_full - W_LABEL
        h = self.__plot.h_row_base * (1 + int(self.__wide) * 3)  # 28/112, 42/168
        self.__label.set_height(h-1)
        self.__graph.set_size(QSize(w, h-1))
        self.__uline.setLine(0, h-1, self.__plot.w_full, h-1)


class TableCanvas(GroupItem):
    """Table frame with:
    - header
    - border
    - columns separator
    - bottom underline
    - bottom scale
    - grid
    """

    class GridItem(GroupItem):
        __plot: 'PlotBase'
        __x: float
        __line: QGraphicsLineItem
        __text: TCPlainTextItem

        def __init__(self, x: float, num: int, plot: 'PlotBase'):
            super().__init__()
            self.__x = x
            self.__plot = plot
            self.__line = QGraphicsLineItem()
            self.__line.setPen(ThinPen(Qt.GlobalColor.lightGray))
            self.__text = TCPlainTextItem(str(num))
            # layout
            self.addToGroup(self.__line)
            self.addToGroup(self.__text)

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

    def update_sizes(self):
        self.__header.update_size()
        self.__frame.setRect(0, H_HEADER, self.__plot.w_full, self.__plot.h_full - H_HEADER)
        self.__colsep.setLine(W_LABEL, H_HEADER, W_LABEL, self.__plot.h_full - H_BOTTOM)
        self.__btmsep.setLine(0, self.__plot.h_full - H_BOTTOM, self.__plot.w_full, self.__plot.h_full - H_BOTTOM)
        for g in self.__grid:
            g.update_size()


class TablePayload(GroupItem):
    __rowitem: list[RowItem]

    """Just rows with underlines"""

    def __init__(self, bslist: BarSuitList, plot: 'PlotBase'):
        super().__init__()
        self.__rowitem = list()
        y = 0
        for bs in bslist:
            item = RowItem(bs, plot)
            item.setY(y)
            y += item.boundingRect().height()
            self.__rowitem.append(item)
            self.addToGroup(self.__rowitem[-1])

    def update_sizes(self):
        y = self.__rowitem[0].boundingRect().y()
        for item in self.__rowitem:
            item.update_size()
            item.setY(y)
            y += item.boundingRect().height()


class PlotScene(QGraphicsScene):
    __canvas: TableCanvas
    __payload: TablePayload

    def __init__(self, bslist: BarSuitList, plot: 'PlotBase'):
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
