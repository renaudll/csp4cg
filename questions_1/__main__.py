import os
from PySide2 import QtCore, QtGui, QtWidgets, QtQuickWidgets

_QML_SRC = os.path.join(os.path.dirname(__file__), "qmlview.qml")

app = QtWidgets.QApplication()
win = QtWidgets.QMainWindow()

model = QtGui.QStandardItemModel()
model.appendRow(QtGui.QStandardItem("A"))
model.appendRow(QtGui.QStandardItem("B"))
model.appendRow(QtGui.QStandardItem("C"))

# Create selection model to share between both views
selectionModel = QtCore.QItemSelectionModel()
selectionModel.setModel(model)
selectionModel.select(model.index(1, 0), QtCore.QItemSelectionModel.Select)

centralWidget = QtWidgets.QWidget()

layout = QtWidgets.QHBoxLayout()
listView = QtWidgets.QListView(win)
listView.setModel(model)
listView.setSelectionModel(selectionModel)
layout.addWidget(listView)

qmlView = QtQuickWidgets.QQuickWidget(win)
qmlView.engine().rootContext().setContextProperty("myModel", model)
qmlView.engine().rootContext().setContextProperty("mySelectionModel", selectionModel)
qmlView.setSource(QtCore.QUrl(_QML_SRC))
layout.addWidget(qmlView)

centralWidget.setLayout(layout)
win.setCentralWidget(centralWidget)
win.show()
app.exec_()
