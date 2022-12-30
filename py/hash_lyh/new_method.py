from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QMainWindow


def lineEdit_dragEnterEvent(event: QDragEnterEvent):
    if event.mimeData().hasUrls:
        event.accept()
    else:
        event.ignore()


def lineEdit_dropEvent(window: QMainWindow, event: QDropEvent):
    window.clear_lineEdit()
    window.filename = event.mimeData().urls()[0].toLocalFile()
    window.lineEdit.setText(str(window.filename))
