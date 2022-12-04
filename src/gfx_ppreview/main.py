#!/usr/bin/env python3
"""gfx_preview/main: main module.
Test of rescaling print + multipage print."""
# 1. std
import sys
from typing import List
# 2. 3rd
from PyQt5.QtGui import QIcon, QCloseEvent, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QShortcut, QToolBar
# 3. local
from consts import PORTRAIT, W_PAGE, H_ROW_BASE
from data import SigSuitList
from gitems import GraphView, GraphViewBase, PlotScene


class PlotBase(GraphViewBase):
    _portrait: bool
    _scene: List[PlotScene]

    def __init__(self):
        super().__init__()
        self._portrait = PORTRAIT
        self._scene = list()
        i0 = 0
        for k in self.__data_split(SigSuitList):
            self._scene.append(PlotScene(SigSuitList[i0:i0 + k], self))
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

    @staticmethod
    def __data_split(__dlist: SigSuitList) -> List[int]:
        """Split data to scene pieces (6/24).
        :return: list of bar numbers
        """
        retvalue = list()
        cur_num = cur_height = 0  # heigth of current piece in basic (B) units
        for i, d in enumerate(__dlist):
            h = 1 + int(not d.is_bool) * 3
            if cur_height + h > 24:
                retvalue.append(cur_num)
                cur_num = cur_height = 0
            cur_num += 1
            cur_height += h
        retvalue.append(cur_num)
        return retvalue


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
        """[Re]set __view to original size."""
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
        self.setRowCount(len(SigSuitList))
        self.setColumnCount(2)
        for r, d in enumerate(SigSuitList):
            self.setItem(r, 0, (QTableWidgetItem(d.name)))
            self.setCellWidget(r, 1, GraphView(d))


class MainWindow(QMainWindow):
    class PdfPrinter(QPrinter):
        def __init__(self):
            super().__init__(QPrinter.PrinterMode.HighResolution)
            self.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            self.setResolution(100)
            self.setPageMargins(10, 10, 10, 10, QPrinter.Unit.Millimeter)
            self.setOrientation(QPrinter.Orientation.Portrait if PORTRAIT else QPrinter.Orientation.Landscape)

    __toolbar: QToolBar
    __view: PlotView
    __printer: PdfPrinter
    __print_preview: PDFOutPreviewDialog
    # actionas
    act_view: QAction
    act_print: QAction
    act_exit: QAction
    act_size0: QAction
    act_o_p: QAction
    act_go_1st: QAction
    act_go_prev: QAction
    act_go_next: QAction
    act_go_last: QAction

    def __init__(self):
        super().__init__()
        self.setCentralWidget(TableView(self))
        self.__view = PlotView(self)
        self.__printer = self.PdfPrinter()
        self.__print_preview = PDFOutPreviewDialog(self.__printer)
        self.__mk_actions()
        self.__mk_menu()
        self.__mk_toolbar()

    def __mk_actions(self):
        # grouping
        self.act_view = QAction(QIcon.fromTheme("document-print-preview"), "&View", self, shortcut="Ctrl+V",
                                checkable=True, toggled=self.__view.setVisible)
        self.act_print = QAction(QIcon.fromTheme("document-print"), "&Print", self, shortcut="Ctrl+P",
                                 triggered=self.__print_preview.exec_)
        self.act_exit = QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                triggered=self.close)
        self.act_size0 = QAction(QIcon.fromTheme("zoom-original"), "Original size", self, shortcut="Ctrl+0",
                                 triggered=self.__view.slot_reset_size)
        self.act_o_p = QAction(QIcon.fromTheme("object-flip-vertical"), "Portrait", self, shortcut="Ctrl+O",
                               checkable=True, toggled=self.__view.slot_set_portrait)
        self.act_go_1st = QAction(QIcon.fromTheme("go-first"), "1st page", self, shortcut="Ctrl+Up",
                                  triggered=self.__view.slot_p_1st)
        self.act_go_prev = QAction(QIcon.fromTheme("go-previous"), "Prev. page", self, shortcut="Ctrl+Left",
                                   triggered=self.__view.slot_p_prev)
        self.act_go_next = QAction(QIcon.fromTheme("go-next"), "Next page", self, shortcut="Ctrl+Right",
                                   triggered=self.__view.slot_p_next)
        self.act_go_last = QAction(QIcon.fromTheme("go-last"), "Last page", self, shortcut="Ctrl+Down",
                                   triggered=self.__view.slot_p_last)

    def __mk_menu(self):
        self.menuBar().setVisible(True)
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_view)
        menu_file.addAction(self.act_print)
        menu_file.addAction(self.act_exit)
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(self.act_size0)
        menu_view.addAction(self.act_o_p)
        menu_view.addAction(self.act_go_1st)
        menu_view.addAction(self.act_go_prev)
        menu_view.addAction(self.act_go_next)
        menu_view.addAction(self.act_go_last)

    def __mk_toolbar(self):
        self.__toolbar = QToolBar(self)
        self.__toolbar.addAction(self.act_view)
        self.__toolbar.addAction(self.act_print)
        self.__toolbar.addAction(self.act_size0)
        self.__toolbar.addAction(self.act_o_p)
        self.__toolbar.addAction(self.act_go_1st)
        self.__toolbar.addAction(self.act_go_prev)
        self.__toolbar.addAction(self.act_go_next)
        self.__toolbar.addAction(self.act_go_last)
        self.__toolbar.addSeparator()
        self.__toolbar.addAction(self.act_exit)
        self.addToolBar(self.__toolbar)


def main() -> int:
    app = QApplication(sys.argv)
    MainWindow().show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
