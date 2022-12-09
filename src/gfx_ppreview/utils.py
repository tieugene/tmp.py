from typing import Union

from PyQt5.QtCore import QRect, QRectF, QSize, QSizeF, Qt
from PyQt5.QtGui import QColor


def qsize2str(size: Union[QRect, QRectF, QSize, QSizeF]) -> str:
    if isinstance(size, QRectF):
        v = size.size().toSize()
    elif isinstance(size, QRect):
        v = size.size()
    elif isinstance(size, QSizeF):
        v = size.toSize()
    else:
        v = size
    return f"({v.width()}, {v.height()})"


def gc2str(c: Qt.GlobalColor) -> str:
    """
    :param c: Global color
    :return: HTML-compatible string representation
    """
    qc = QColor(c)
    return f"rgb({qc.red()},{qc.green()},{qc.blue()})"
