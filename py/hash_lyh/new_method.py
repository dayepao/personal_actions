from PySide6.QtGui import QDragEnterEvent, QDropEvent

from hash_lyh import mainwindow


def lineEdit_dragEnterEvent(event: QDragEnterEvent):
    if event.mimeData().hasUrls:
        event.accept()
    else:
        event.ignore()


def lineEdit_dropEvent(window: mainwindow, event: QDropEvent):
    window.clear_lineEdit()
    window.filename = event.mimeData().urls()[0].toLocalFile()
    window.lineEdit.setText(str(window.filename))
