import pathlib

from PySide2.QtCore import Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtWidgets import \
    QApplication, \
    QDataWidgetMapper, \
    QGridLayout, \
    QLabel, \
    QLineEdit, \
    QMainWindow, \
    QSpinBox, \
    QSplitter, \
    QTableView, \
    QTreeView, \
    QWidget

QML_VIEW_SOURCE = str(pathlib.Path(__file__).parent / "qmlview.qml")

app = QApplication()

win = QMainWindow()

# Define model and item role names

START_DATE_ROLE = Qt.UserRole
END_DATE_ROLE = Qt.UserRole+1

model = QStandardItemModel(win)

# We setItemRoleNames so the values can be accessed by names in Qml
model.setItemRoleNames({
    Qt.DisplayRole: b"name",
    START_DATE_ROLE: b"startDate",
    END_DATE_ROLE: b"endDate"
})

# Artist A

artist = QStandardItem("Artist A")

shot = QStandardItem("ShotA")
shot.setData(0, START_DATE_ROLE)
shot.setData(100, END_DATE_ROLE)
artist.appendRow(shot)

shot = QStandardItem("ShotB")
shot.setData(110, START_DATE_ROLE)
shot.setData(150, END_DATE_ROLE)
artist.appendRow(shot)

model.appendRow(artist)

# Artist B

artist = QStandardItem("Artist B")

shot = QStandardItem("ShotC")
shot.setData(20, START_DATE_ROLE)
shot.setData(110, END_DATE_ROLE)
artist.appendRow(shot)

shot = QStandardItem("ShotD")
shot.setData(120, START_DATE_ROLE)
shot.setData(160, END_DATE_ROLE)
artist.appendRow(shot)

model.appendRow(artist)

# UI

vsplit = QSplitter(win)

treeView = QTreeView(vsplit)
treeView.setModel(model)

vsplit.addWidget(treeView)

# Expose model to Qml

qmlView = QQuickWidget(vsplit)
qmlView.engine().rootContext().setContextProperty("artists", model)
qmlView.setSource(QML_VIEW_SOURCE)
qmlView.show()

win.setCentralWidget(vsplit)
win.show()
app.exec_()
