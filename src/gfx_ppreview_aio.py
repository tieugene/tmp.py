#!/usr/bin/env python3
"""gfx_ppreview: all-in-one for demo"""
# 1. std
from typing import Tuple, List
import sys
import math
# 2. 3rd
from PyQt5.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt5.QtGui import QFont, QPolygonF, QPainterPath, QPen, QResizeEvent, QPainter, QIcon, QCloseEvent
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QShortcut, \
    QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, QWidget, \
    QStyleOptionGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLineItem

# ==== 0. Consts ====
# ---- user defined: ----
# .... debug ....
DEBUG = False  # paint borders around some items
PORTRAIT = False  # initial orientation
AUTOFILL = True
# .... play with this ....
SAMPLES = 24  # samples per signal
SIGNALS = 50  # Number of signals for autofill
# ---- hardcoded (don't touch) ----
W_PAGE = (1130, 748)  # Page width landscape/portrait; (A4-10mm)/0.254mm
W_LABEL = 53  # Label column width
H_HEADER = 56  # Header height, like 4×14
H_ROW_BASE = 28  # Base (slick) row height in landscape mode; like 2×14
H_BOTTOM = 20  # Bottom scale height
PPP = 6  # plots per page
FONT_MAIN = QFont('mono', 8)  # 7×14
COLORS = (
    Qt.GlobalColor.black,
    Qt.GlobalColor.red,
    Qt.GlobalColor.darkRed,
    Qt.GlobalColor.green,
    Qt.GlobalColor.darkGreen,
    Qt.GlobalColor.blue,
    Qt.GlobalColor.darkBlue,
    Qt.GlobalColor.cyan,
    Qt.GlobalColor.darkCyan,
    Qt.GlobalColor.magenta,
    Qt.GlobalColor.darkMagenta,
    Qt.GlobalColor.yellow,
    Qt.GlobalColor.darkYellow,
    Qt.GlobalColor.gray,
    Qt.GlobalColor.darkGray,
    Qt.GlobalColor.lightGray
)
# y. data
HEADER_TXT = '''This is the header with 3 lines.
Hotkeys: ^0: Original size, ^O: Switch landscape/portrait, ^V: Close (hide),
Go page: ^↑: 1st, ^←: Prev., ^→: Next, ^↓: Last.
'''
TICS = {  # scale tics {sample_no: text}
    0: 123,
    5: 456,
    SAMPLES * 0.98: 789
}
# name, x-offset/perios, color, analog
DataValue = Tuple[str, int, Qt.GlobalColor, bool]
DATA_PREDEF = (
    ("Signal 1", 0, Qt.GlobalColor.black, True),
    ("Signal 22", 1, Qt.GlobalColor.red, True),
    ("Signal 333", 2, Qt.GlobalColor.blue, True),
    ("Signal 4444", 3, Qt.GlobalColor.green, False),
    ("Signal 5", 4, Qt.GlobalColor.magenta, False),
    ("Signal 6", 5, Qt.GlobalColor.darkYellow, True),
    ("Signal 10", 6, Qt.GlobalColor.cyan, True),
    ("Signal 11", 7, Qt.GlobalColor.darkGreen, True),
    ("Signal 12", 8, Qt.GlobalColor.yellow, True),
    ("Signal 13", 9, Qt.GlobalColor.darkBlue, True),
)
DATA = []


# ==== 1. Widgets + utils ====

def data_fill():
    """Fill data witth predefined or auto"""
    if AUTOFILL:
        import random
        random.seed()
        for i in range(SIGNALS):
            DATA.append((
                f"Signal {i}",
                random.randint(0, SAMPLES - 1),
                COLORS[random.randint(0, len(COLORS) - 1)],
                bool(random.randint(0, 1))
            ))
    else:
        DATA.extend(DATA_PREDEF)


def data_split() -> List[int]:
    """Split data to scene pieces (6/24).
    :return: list of bar numbers
    """
    retvalue = list()
    cur_num = cur_height = 0  # heigth of current piece in basic (B) units
    for i, d in enumerate(DATA):
        h = 1 + int(d[3]) * 3
        if cur_height + h > 24:
            retvalue.append(cur_num)
            cur_num = cur_height = 0
        cur_num += 1
        cur_height += h
    retvalue.append(cur_num)
    return retvalue


def mk_sin(o: int = 0) -> List[float]:
    """
    Make sinusoide graph coordinates. Y=0..1
    :param o: Offset, points
    :return: list of y (0..1)
    """
    return [(1 + math.sin((i + o) * 2 * math.pi / SAMPLES)) / 2 for i in range(SAMPLES + 1)]


def mk_meander(p: int) -> List[float]:
    """Make meander. Starts from 0.
    :param p: Period
    """
    p = p % SAMPLES or 1
    return [int(i / p) % 2 for i in range(SAMPLES + 1)]


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

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
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


# 2. ==== Main ====
class PlotBase(GraphViewBase):
    _portrait: bool
    _scene: List[PlotScene]

    def __init__(self):
        super().__init__()
        self._portrait = PORTRAIT
        self._scene = list()
        i0 = 0
        for k in data_split():
            self._scene.append(PlotScene(DATA[i0:i0 + k], self))
            i0 += k

    @property
    def portrait(self) -> bool:
        return self._portrait

    @property
    def w_full(self) -> int:
        """Current full table width"""
        return W_PAGE[int(self.portrait)]

    @property
    def h_full(self) -> int:
        """Current full table width"""
        return W_PAGE[1 - int(self.portrait)]

    @property
    def h_row_base(self) -> int:
        """Current base (short) row height.
        :note: in theory must be (W_PAGE - header - footer) / num
        :todo: cache it
        """
        return round(H_ROW_BASE * 1.5) if self.portrait else H_ROW_BASE

    @property
    def scene_count(self) -> int:
        return len(self._scene)

    def slot_set_portrait(self, v: bool):
        if self._portrait ^ v:
            self._portrait = v
            for scene in self._scene:
                scene.update_sizes()
            # self.slot_reset_size()  # optional


class PlotView(PlotBase):
    _father: 'MainWindow'
    scene_cur: int
    # shortcuts
    __sc_close: QShortcut
    __sc_size0: QShortcut
    __sc_o: QShortcut
    __sc_p_1st: QShortcut
    __sc_p_prev: QShortcut
    __sc_p_next: QShortcut
    __sc_p_last: QShortcut

    def __init__(self, father: 'MainWindow'):
        super().__init__()
        self._father = father
        self.__set_scene(0)
        # shortcuts
        self.__sc_close = QShortcut("Ctrl+V", self)
        self.__sc_size0 = QShortcut("Ctrl+0", self)
        self.__sc_o = QShortcut("Ctrl+O", self)
        self.__sc_p_1st = QShortcut("Ctrl+Up", self)
        self.__sc_p_prev = QShortcut("Ctrl+Left", self)
        self.__sc_p_next = QShortcut("Ctrl+Right", self)
        self.__sc_p_last = QShortcut("Ctrl+Down", self)
        # ...and their connections
        self.__sc_close.activated.connect(self.close)
        self.__sc_size0.activated.connect(self.slot_reset_size)
        self.__sc_o.activated.connect(self.__slot_o)
        self.__sc_p_1st.activated.connect(self.slot_p_1st)
        self.__sc_p_prev.activated.connect(self.slot_p_prev)
        self.__sc_p_next.activated.connect(self.slot_p_next)
        self.__sc_p_last.activated.connect(self.slot_p_next)

    def closeEvent(self, _: QCloseEvent):
        """Masq closing with switch off"""
        self._father.act_view.setChecked(False)

    def slot_reset_size(self):
        """[Re]set view to original size."""
        self.resize(self.scene().itemsBoundingRect().size().toSize())

    def __slot_o(self):
        """To avoid loopback"""
        self._father.act_o_p.toggle()

    def __set_scene(self, i: int):
        self.scene_cur = i
        self.setScene(self._scene[self.scene_cur])

    def slot_p_1st(self):
        if self.scene_cur:
            self.__set_scene(0)

    def slot_p_prev(self):
        if self.scene_cur:
            self.__set_scene(self.scene_cur - 1)

    def slot_p_next(self):
        if self.scene_cur + 1 < self.scene_count:
            self.__set_scene(self.scene_cur + 1)

    def slot_p_last(self):
        if self.scene_cur < self.scene_count - 1:
            self.__set_scene(self.scene_count - 1)


class PlotPrint(PlotBase):
    """
    :todo: just scene container; can be replaced with QObject
    """

    def __init__(self):
        super().__init__()
        # print("Render__init__")

    def slot_paint_request(self, printer: QPrinter):
        """
        Call _B4_ show dialog
        Use printer.pageRect(QPrinter.Millimeter/DevicePixel).
        :param printer: Where to draw to
        """
        # print("Render.slot_paint_request()")
        self.slot_set_portrait(printer.orientation() == QPrinter.Orientation.Portrait)
        painter = QPainter(printer)
        self._scene[0].render(painter)  # Sizes: dst: printer.pageSize(), src: self.scene().sceneRect()
        for scene in self._scene[1:]:
            printer.newPage()
            scene.render(painter)


class PDFOutPreviewDialog(QPrintPreviewDialog):
    def __init__(self, __printer: QPrinter):
        super().__init__(__printer)

    def exec_(self):
        """Exec print dialog from Print action activated until Esc (0) or 'OK' (print) pressed.
        :todo: mk render | connect | exec | disconnect | del render
        """
        rnd = PlotPrint()
        self.paintRequested.connect(rnd.slot_paint_request)
        retvalue = super().exec_()
        self.paintRequested.disconnect(rnd.slot_paint_request)  # not helps
        del rnd  # not helps
        return retvalue


class TableView(QTableWidget):
    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setRowCount(len(DATA))
        self.setColumnCount(2)
        for r, d in enumerate(DATA):
            self.setItem(r, 0, (QTableWidgetItem(d[0])))
            self.setCellWidget(r, 1, GraphView(d))


class MainWindow(QMainWindow):
    class PdfPrinter(QPrinter):
        def __init__(self):
            super().__init__(QPrinter.PrinterMode.HighResolution)
            self.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            self.setResolution(100)
            self.setPageMargins(10, 10, 10, 10, QPrinter.Unit.Millimeter)
            self.setOrientation(QPrinter.Orientation.Portrait if PORTRAIT else QPrinter.Orientation.Landscape)

    view: PlotView
    __printer: PdfPrinter
    __print_preview: PDFOutPreviewDialog
    # actionas
    act_view: QAction
    act_o_p: QAction

    def __init__(self):
        super().__init__()
        self.setCentralWidget(TableView(self))
        self.view = PlotView(self)
        self.__printer = self.PdfPrinter()
        self.__print_preview = PDFOutPreviewDialog(self.__printer)
        self.__mk_actions()

    def __mk_actions(self):
        # grouping
        self.act_o_p = QAction(QIcon.fromTheme("object-flip-vertical"), "Portrait", self, shortcut="Ctrl+O",
                               checkable=True, toggled=self.view.slot_set_portrait)
        self.act_view = QAction(QIcon.fromTheme("view-fullscreen"), "&View", self, shortcut="Ctrl+V",
                                checkable=True, toggled=self.view.setVisible)
        # menu
        self.menuBar().setVisible(True)
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_view)
        menu_file.addAction(QAction(QIcon.fromTheme("document-print-preview"), "&Print", self, shortcut="Ctrl+P",
                                    triggered=self.__print_preview.exec_))
        menu_file.addAction(QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                    triggered=self.close))
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(QAction(QIcon.fromTheme("zoom-original"), "Original size", self, shortcut="Ctrl+0",
                                    triggered=self.view.slot_reset_size))
        menu_view.addAction(self.act_o_p)
        menu_view.addAction(QAction(QIcon.fromTheme("go-first"), "1st page", self, shortcut="Ctrl+Up",
                                    triggered=self.view.slot_p_1st))
        menu_view.addAction(QAction(QIcon.fromTheme("go-previous"), "Prev. page", self, shortcut="Ctrl+Left",
                                    triggered=self.view.slot_p_prev))
        menu_view.addAction(QAction(QIcon.fromTheme("go-next"), "Next page", self, shortcut="Ctrl+Right",
                                    triggered=self.view.slot_p_next))
        menu_view.addAction(QAction(QIcon.fromTheme("go-last"), "Last page", self, shortcut="Ctrl+Down",
                                    triggered=self.view.slot_p_last))


def main() -> int:
    data_fill()
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    # mw.resize(600, 600)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
