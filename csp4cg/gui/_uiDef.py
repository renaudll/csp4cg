# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file '_uiDef.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from PySide2.QtQuickWidgets import QQuickWidget



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(812, 604)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.widget_gantt = QQuickWidget(self.centralwidget)
        self.widget_gantt.setObjectName(u"widget_gantt")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_gantt.sizePolicy().hasHeightForWidth())
        self.widget_gantt.setSizePolicy(sizePolicy)
        self.widget_gantt.setResizeMode(QQuickWidget.SizeRootObjectToView)

        self.verticalLayout_2.addWidget(self.widget_gantt)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_artists = QLabel(self.centralwidget)
        self.label_artists.setObjectName(u"label_artists")

        self.verticalLayout.addWidget(self.label_artists)

        self.table_artists = QTableView(self.centralwidget)
        self.table_artists.setObjectName(u"table_artists")
        self.table_artists.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_artists.horizontalHeader().setVisible(True)
        self.table_artists.horizontalHeader().setStretchLastSection(True)
        self.table_artists.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.table_artists)

        self.label_shots = QLabel(self.centralwidget)
        self.label_shots.setObjectName(u"label_shots")

        self.verticalLayout.addWidget(self.label_shots)

        self.table_shots = QTableView(self.centralwidget)
        self.table_shots.setObjectName(u"table_shots")
        self.table_shots.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_shots.horizontalHeader().setVisible(True)
        self.table_shots.horizontalHeader().setStretchLastSection(True)
        self.table_shots.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.table_shots)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_play = QPushButton(self.centralwidget)
        self.button_play.setObjectName(u"button_play")

        self.horizontalLayout.addWidget(self.button_play)

        self.button_stop = QPushButton(self.centralwidget)
        self.button_stop.setObjectName(u"button_stop")

        self.horizontalLayout.addWidget(self.button_stop)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 812, 27))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Assignments", None))
        self.label_artists.setText(QCoreApplication.translate("MainWindow", u"Artists", None))
        self.label_shots.setText(QCoreApplication.translate("MainWindow", u"Shots", None))
        self.button_play.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.button_stop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
    # retranslateUi

