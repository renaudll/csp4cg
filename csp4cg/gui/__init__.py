"""Graphical user interface"""
from PySide2.QtWidgets import QApplication

from .main_window import MainWindow
from ._manager import Manager

__all__ = ("show", "Manager")


def show():
    """Show the main window."""
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
