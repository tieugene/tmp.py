import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QScrollArea,
    QGridLayout,
    QLabel,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    )


ROWS = 10
COLS = 20
SIZE = 35


style = """
Button {
    padding: 0;
    margin: 0;
    border: 1px solid black;
}
Button::checked {
    background-color: lightgreen;
}
"""


class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(SIZE, SIZE)
        self.setCheckable(True)
        self.setStyleSheet(style)


class Label(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(SIZE, SIZE)


class Labels(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FrozenScrollArea(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setEnabled(False)
        self.horizontalScrollBar().setEnabled(False)


class FrozenRow(FrozenScrollArea):
    def __init__(self, parent):
        super().__init__()

        labels = Labels(parent)
        for c in range(COLS):
            label = Label(self, text = str(c))
            labels.layout().addWidget(label, 0, c, 1, 1, Qt.AlignCenter)

        labels.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, COLS, 1, 1)

        self.setFrameShape(QFrame.NoFrame)
        self.setFixedHeight(SIZE)
        self.setWidget(labels)


class FrozenColumn(FrozenScrollArea):
    def __init__(self, parent):
        super().__init__()

        labels = Labels(parent)
        for r in range(ROWS):
            label = Label(self, text = str(r))
            labels.layout().addWidget(label, r, 0, 1, 1, Qt.AlignCenter)

        labels.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), ROWS, 0, 1, 1)

        self.setFrameShape(QFrame.NoFrame)
        self.setFixedWidth(SIZE)
        self.setWidget(labels)


class ButtonGroup(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QGridLayout()
        for r in range(ROWS):
            for c in range(COLS):
                button = Button(self)
                layout.addWidget(button, r, c, 1, 1)

        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)


class Buttons(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setWidget(ButtonGroup(parent))


class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # layout
        layout = QGridLayout()
        self.setLayout(layout)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # frozen row (top)
        self.frozenRow = FrozenRow(self)
        layout.addWidget(self.frozenRow, 0, 1, 1, 1)

        # frozen column (left)
        self.frozenColumn = FrozenColumn(self)
        layout.addWidget(self.frozenColumn, 1, 0, 1, 1)

        # button grid
        self.buttons = Buttons(self)
        layout.addWidget(self.buttons, 1, 1, 1, 1)

        # scrollbar connections
        self.buttons.horizontalScrollBar().valueChanged.connect(self.frozenRow.horizontalScrollBar().setValue)  # horizontal scroll affects frozen row only
        self.buttons.verticalScrollBar().valueChanged.connect(self.frozenColumn.verticalScrollBar().setValue)  # vertical scroll affects frozemn column only

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
