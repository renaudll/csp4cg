"""Gant view using QML."""
import os
import datetime
from PySide2 import QtCore, QtWidgets, QtQuickWidgets
from csp4cg.tasks import Artist, Shot, ArtistAssignment
from csp4cg.gui.models import ArtistsModel, ShotAssignmentModel

_DIR = os.path.dirname(__file__)
_QML = os.path.join(_DIR, "gantt.qml")

artist1 = Artist(id=0, name="Artist 1", tags={}, availability=100)
artist2 = Artist(id=1, name="Artist 2", tags={}, availability=100)
artist3 = Artist(id=2, name="Artist 3", tags={}, availability=100)

shot1 = Shot(id=0, name="Shot 1", duration=datetime.timedelta(hours=3), tags={})
shot2 = Shot(id=1, name="Shot 2", duration=datetime.timedelta(hours=4), tags={})
shot3 = Shot(id=2, name="Shot 3", duration=datetime.timedelta(hours=5), tags={})
shot4 = Shot(id=3, name="Shot 4", duration=datetime.timedelta(hours=1), tags={})

assignment1 = ArtistAssignment(artist=artist1, shot=shot1)
assignment2 = ArtistAssignment(artist=artist1, shot=shot2)
assignment3 = ArtistAssignment(artist=artist1, shot=shot3)
assignment4 = ArtistAssignment(artist=artist1, shot=shot4)

artist_model = ArtistsModel([artist1, artist2, artist3])
assignment_model = ShotAssignmentModel(
    None, [assignment1, assignment2, assignment3, assignment4]
)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        wid = QtQuickWidgets.QQuickWidget()
        wid.rootContext().setContextProperty("artists", artist_model)
        wid.rootContext().setContextProperty("assignments", assignment_model)
        wid.setSource(QtCore.QUrl(_QML))

        self.setCentralWidget(wid)


def main():
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
