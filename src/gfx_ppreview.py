#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import sys
from typing import List
# 2. 3rd
from PyQt5.QtGui import QIcon, QCloseEvent, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QShortcut, \
    QGraphicsScene
# 3. local
from gfx_ppreview_const import PORTRAIT, AUTOFILL, SAMPLES, SIGNALS, DATA, W_PAGE, H_ROW_BASE, DATA_PREDEF, COLORS
from gfx_ppreview_widgets import GraphView, GraphViewBase, PlotScene


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


class PlotBase(GraphViewBase):
    _father: 'MainWindow'
    _portrait: bool
    _scene: List[PlotScene]

    def __init__(self, father: 'MainWindow'):
        super().__init__()
        self._father = father
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
        super().__init__(father)
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
    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        # print("Render init")

    def print_(self, printer: QPrinter):
        """
        Call _B4_ show dialog
        Use printer.pageRect(QPrinter.Millimeter/DevicePixel).
        :param printer: Where to draw to
        """
        # print("Render.print_(): start")
        # print("Res:", printer.resolution())
        self.slot_set_portrait(printer.orientation() == QPrinter.Orientation.Portrait)
        painter = QPainter(printer)
        self._scene[0].render(painter)  # Sizes: dst: printer.pageSize(), src: self.scene().sceneRect()
        for scene in self._scene[1:]:
            printer.newPage()
            scene.render(painter)
        # print("Render.print_(): end")


class PDFOutPreviewDialog(QPrintPreviewDialog):
    __render: PlotPrint

    def __init__(self, __printer: QPrinter, parent: 'MainWindow'):
        super().__init__(__printer, parent)
        self.__render = PlotPrint(parent)
        self.paintRequested.connect(self.__render.print_)

    def exec_(self):
        """Exec print dialog from Print action activated until Esc (0) or 'OK' (print) pressed.
        :todo: mk render | connect | exec | disconnect | del render
        """
        #
        # rnd = PlotPrint(self.parent())
        # self.paintRequested.connect(rnd.print_)
        retvalue = super().exec_()
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
        self.__print_preview = PDFOutPreviewDialog(self.__printer, self)
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
