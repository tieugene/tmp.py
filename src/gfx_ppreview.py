#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import sys
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsLinearLayout, \
    QGraphicsWidget, QActionGroup, QShortcut, QGraphicsItemGroup, QGraphicsRectItem, QGraphicsLineItem, QGraphicsItem, \
    QGraphicsScene
# 3. local
from gfx_ppreview_const import DATA, DataValue, W_PAGE, H_ROW_BASE, H_HEADER, H_BOTTOM, W_LABEL, TICS, SAMPLES, \
    PORTRAIT, DATA_PREDEF, AUTOFILL, SIGNALS, COLORS
from gfx_ppreview_widgets import GraphView, RowItem, LayoutItem, GraphViewBase, HeaderItem, ThinPen, TCTextItem, \
    qsize2str


def data_fill():
    """Fill data witth predefined or auto"""
    if AUTOFILL:
        import random
        random.seed()
        for i in range(SIGNALS):
            DATA.append((
                f"Signal {i}",
                random.randint(0, SAMPLES-1),
                COLORS[random.randint(0, len(COLORS)-1)],
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
        __plot: 'PlotView'
        __x: float
        __line: QGraphicsLineItem
        __text: TCTextItem

        def __init__(self, x: float, num: int, plot: 'PlotView'):
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

    __plot: 'PlotView'
    __header: HeaderItem
    __frame: QGraphicsRectItem  # external border; TODO: clip all inners (header, tic labels) by this
    __colsep: QGraphicsLineItem  # columns separator
    __btmsep: QGraphicsLineItem  # bottom separator
    __grid: List[GridItem]  # tics (v-line+label)

    def __init__(self, plot: 'PlotView'):
        super().__init__()
        self.__plot = plot
        self.__header = HeaderItem(plot)
        pen = ThinPen(Qt.GlobalColor.gray)
        self.__frame = QGraphicsRectItem()
        self.__frame.setPen(pen)
        self.__frame.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # clip inners into this
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
        # print("Canvas 0:", qsize2str(self.boundingRect()), qsize2str(self.childrenBoundingRect()))
        self.__header.update_size()
        self.__frame.setRect(0, H_HEADER, self.__plot.w_full, self.__plot.h_full - H_HEADER)
        self.__colsep.setLine(W_LABEL, H_HEADER, W_LABEL, self.__plot.h_full - H_BOTTOM)
        self.__btmsep.setLine(0, self.__plot.h_full - H_BOTTOM, self.__plot.w_full, self.__plot.h_full - H_BOTTOM)
        for g in self.__grid:
            g.update_size()
        # print("Canvas 1:", qsize2str(self.boundingRect()), qsize2str(self.childrenBoundingRect()))


class TablePayload(QGraphicsWidget):  # <(QGraphicsObject<QGraphicsItem, QGraphicsLayoutItem)
    """Just rows with underlines"""
    def __init__(self, dlist: List[DataValue], plot: 'PlotView'):
        super().__init__()
        lt = QGraphicsLinearLayout(Qt.Vertical, self)
        lt.setContentsMargins(0, 0, 0, 0)
        lt.setSpacing(0)
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RowItem(d, plot)))
        self.setLayout(lt)

    def boundingRect(self) -> QRectF:  # update_sizes() fix
        return self.childrenBoundingRect()

    def update_sizes(self):
        self.layout().invalidate()  # FIXME: not helps
        for i in range(self.layout().count()):
            self.layout().itemAt(i).graphicsItem().update_size()
        self.layout().activate()  # not helps
        self.adjustSize()  # not helps


class PlotScene(QGraphicsScene):
    __canvas: TableCanvas
    __payload: TablePayload

    def __init__(self, data: List[DataValue], plot: 'PlotView'):
        super().__init__()
        self.__canvas = TableCanvas(plot)
        self.__payload = TablePayload(data, plot)
        self.__payload.setY(H_HEADER)
        self.addItem(self.__canvas)
        self.addItem(self.__payload)

    def update_sizes(self):
        def __diagnostics(title: str):
            print(title, qsize2str(self.sceneRect()), qsize2str(self.itemsBoundingRect()))
            for item in self.items():
                print(int(item.boundingRect().width()), type(item))
            print()
        # __diagnostics("B4:")
        self.__canvas.update_sizes()
        self.__payload.update_sizes()
        self.setSceneRect(self.itemsBoundingRect())
        # __diagnostics("After:")


class PlotView(GraphViewBase):
    __father: 'MainWindow'
    __portrait: bool
    __scene: List[PlotScene]
    scene_cur: int
    # shortcuts
    __sc_close: QShortcut
    __sc_size0: QShortcut
    __sc_o_L: QShortcut
    __sc_o_P: QShortcut
    __sc_p_1st: QShortcut
    __sc_p_prev: QShortcut
    __sc_p_next: QShortcut
    __sc_p_last: QShortcut

    def __init__(self, father: 'MainWindow'):
        super().__init__()
        self.__father = father
        self.__portrait = PORTRAIT
        self.__scene = list()
        # fill scenes
        i0 = 0
        for k in data_split():
            self.__scene.append(PlotScene(DATA[i0:i0+k], self))
            i0 += k
        # set default scene
        self.__set_scene(0)
        # shortcuts
        self.__sc_close = QShortcut("Ctrl+V", self)
        self.__sc_size0 = QShortcut("Ctrl+0", self)
        self.__sc_o_L = QShortcut("Ctrl+L", self)
        self.__sc_o_P = QShortcut("Ctrl+P", self)
        self.__sc_p_1st = QShortcut("Ctrl+Up", self)
        self.__sc_p_prev = QShortcut("Ctrl+Left", self)
        self.__sc_p_next = QShortcut("Ctrl+Right", self)
        self.__sc_p_last = QShortcut("Ctrl+Down", self)
        # ...and their connections
        self.__sc_close.activated.connect(self.close)
        self.__sc_size0.activated.connect(self.slot_reset_size)
        self.__sc_o_L.activated.connect(self.__slot_set_o_l)
        self.__sc_o_P.activated.connect(self.__slot_set_o_p)
        self.__sc_p_1st.activated.connect(self.slot_p_1st)
        self.__sc_p_prev.activated.connect(self.slot_p_prev)
        self.__sc_p_next.activated.connect(self.slot_p_next)
        self.__sc_p_last.activated.connect(self.slot_p_next)

    def closeEvent(self, _: QCloseEvent):
        """Masq closing with switch off"""
        self.__father.act_view.setChecked(False)

    @property
    def w_full(self) -> int:
        """Current full table width"""
        return W_PAGE[int(self.__portrait)]

    @property
    def h_full(self) -> int:
        """Current full table width"""
        return W_PAGE[1 - int(self.__portrait)]

    @property
    def h_row_base(self) -> int:
        """Current base (short) row height.
        :note: in theory must be (W_PAGE - header - footer) / num
        :todo: cache it
        """
        return round(H_ROW_BASE * 1.5) if self.__portrait else H_ROW_BASE

    @property
    def portrait(self) -> bool:
        return self.__portrait

    @portrait.setter
    def portrait(self, v: bool):
        # FIXME: shrink width
        if self.__portrait ^ v:
            self.__portrait = v
            self.scene().update_sizes()
            # skip
            # self.setSceneRect(self.scene().itemsBoundingRect())  # not works
            self.slot_reset_size()

    @property
    def scene_count(self) -> int:
        return len(self.__scene)

    def __slot_set_o_l(self):
        self.portrait = False

    def __slot_set_o_p(self):
        self.portrait = True

    def slot_reset_size(self):
        """[Re]set view to original size."""
        self.resize(self.scene().itemsBoundingRect().size().toSize())

    def __set_scene(self, i: int):
        self.scene_cur = i
        self.setScene(self.__scene[self.scene_cur])

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
    view: PlotView
    act_view: QAction
    act_o_l: QAction
    act_o_p: QAction
    act_o: QActionGroup

    def __init__(self):
        super().__init__()
        self.setCentralWidget(TableView(self))
        self.view = PlotView(self)
        self.__mk_actions()

    def __mk_actions(self):
        # grouping
        self.act_o_l = QAction(QIcon.fromTheme("object-flip-horizontal"), "Landscape", self, shortcut="Ctrl+L",
                               checkable=True)
        self.act_o_p = QAction(QIcon.fromTheme("object-flip-vertical"), "Portrait", self, shortcut="Ctrl+P",
                               checkable=True)
        self.act_o = QActionGroup(self)
        self.act_o.addAction(self.act_o_l).setChecked(True)
        self.act_o.addAction(self.act_o_p)
        self.act_o.triggered.connect(self.__do_o)
        self.act_view = QAction(QIcon.fromTheme("view-fullscreen"), "&View", self, shortcut="Ctrl+V", checkable=True,
                                toggled=self.__do_view)
        # menu
        self.menuBar().setVisible(True)
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_view)
        menu_file.addAction(QAction(QIcon.fromTheme("document-print-preview"), "&Print", self, shortcut="Ctrl+P",
                                    triggered=self.__do_print))
        menu_file.addAction(QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                    triggered=self.close))
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(QAction(QIcon.fromTheme("zoom-original"), "Original size", self, shortcut="Ctrl+0",
                                    triggered=self.view.slot_reset_size))
        menu_view.addAction(self.act_o_l)
        menu_view.addAction(self.act_o_p)
        menu_view.addAction(QAction(QIcon.fromTheme("go-first"), "1st page", self, shortcut="Ctrl+Up",
                                    triggered=self.view.slot_p_1st))
        menu_view.addAction(QAction(QIcon.fromTheme("go-previous"), "Prev. page", self, shortcut="Ctrl+Left",
                                    triggered=self.view.slot_p_prev))
        menu_view.addAction(QAction(QIcon.fromTheme("go-next"), "Next page", self, shortcut="Ctrl+Right",
                                    triggered=self.view.slot_p_next))
        menu_view.addAction(QAction(QIcon.fromTheme("go-last"), "Last page", self, shortcut="Ctrl+Down",
                                    triggered=self.view.slot_p_last))

    def __do_o(self, a: QAction):
        """Switch page orientation"""
        self.view.portrait = (a == self.act_o_p)

    def __do_view(self, v: bool):
        """Switch View on/off"""
        self.view.setVisible(v)

    def __do_print(self):
        ...


def main() -> int:
    data_fill()
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    # mw.resize(600, 600)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
