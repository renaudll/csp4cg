# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
        MainWindow.resize(1477, 743)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Vertical)

        self.verticalLayout_3.addWidget(self.splitter)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.widget_gantt = QQuickWidget(self.centralwidget)
        self.widget_gantt.setObjectName(u"widget_gantt")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_gantt.sizePolicy().hasHeightForWidth())
        self.widget_gantt.setSizePolicy(sizePolicy1)
        self.widget_gantt.setResizeMode(QQuickWidget.SizeRootObjectToView)

        self.verticalLayout_2.addWidget(self.widget_gantt)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_play = QPushButton(self.centralwidget)
        self.button_play.setObjectName(u"button_play")

        self.horizontalLayout.addWidget(self.button_play)

        self.button_stop = QPushButton(self.centralwidget)
        self.button_stop.setObjectName(u"button_stop")

        self.horizontalLayout.addWidget(self.button_stop)

        self.label_progress = QLabel(self.centralwidget)
        self.label_progress.setObjectName(u"label_progress")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_progress.sizePolicy().hasHeightForWidth())
        self.label_progress.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.label_progress)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(-1)

        self.horizontalLayout.addWidget(self.progressBar)

        self.horizontalSpacer_progress = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_progress)

        self.button_export_assignments = QPushButton(self.centralwidget)
        self.button_export_assignments.setObjectName(u"button_export_assignments")

        self.horizontalLayout.addWidget(self.button_export_assignments)

        self.checkBox_live = QCheckBox(self.centralwidget)
        self.checkBox_live.setObjectName(u"checkBox_live")
        self.checkBox_live.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_live)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1477, 27))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_artists = QLabel(self.dockWidgetContents)
        self.label_artists.setObjectName(u"label_artists")

        self.verticalLayout.addWidget(self.label_artists)

        self.lineEdit_search_artists = QLineEdit(self.dockWidgetContents)
        self.lineEdit_search_artists.setObjectName(u"lineEdit_search_artists")

        self.verticalLayout.addWidget(self.lineEdit_search_artists)

        self.table_artists = QTableView(self.dockWidgetContents)
        self.table_artists.setObjectName(u"table_artists")
        sizePolicy1.setHeightForWidth(self.table_artists.sizePolicy().hasHeightForWidth())
        self.table_artists.setSizePolicy(sizePolicy1)
        self.table_artists.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_artists.horizontalHeader().setVisible(True)
        self.table_artists.horizontalHeader().setStretchLastSection(True)
        self.table_artists.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.table_artists)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.button_add_artist = QPushButton(self.dockWidgetContents)
        self.button_add_artist.setObjectName(u"button_add_artist")

        self.horizontalLayout_2.addWidget(self.button_add_artist)

        self.button_remove_artists = QPushButton(self.dockWidgetContents)
        self.button_remove_artists.setObjectName(u"button_remove_artists")

        self.horizontalLayout_2.addWidget(self.button_remove_artists)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.button_import_artists = QPushButton(self.dockWidgetContents)
        self.button_import_artists.setObjectName(u"button_import_artists")

        self.horizontalLayout_2.addWidget(self.button_import_artists)

        self.button_export_artists = QPushButton(self.dockWidgetContents)
        self.button_export_artists.setObjectName(u"button_export_artists")

        self.horizontalLayout_2.addWidget(self.button_export_artists)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)
        self.dockWidget_2 = QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_shots = QLabel(self.dockWidgetContents_2)
        self.label_shots.setObjectName(u"label_shots")

        self.verticalLayout_4.addWidget(self.label_shots)

        self.lineEdit_search_shots = QLineEdit(self.dockWidgetContents_2)
        self.lineEdit_search_shots.setObjectName(u"lineEdit_search_shots")

        self.verticalLayout_4.addWidget(self.lineEdit_search_shots)

        self.table_shots = QTableView(self.dockWidgetContents_2)
        self.table_shots.setObjectName(u"table_shots")
        sizePolicy1.setHeightForWidth(self.table_shots.sizePolicy().hasHeightForWidth())
        self.table_shots.setSizePolicy(sizePolicy1)
        self.table_shots.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_shots.horizontalHeader().setVisible(True)
        self.table_shots.horizontalHeader().setStretchLastSection(True)
        self.table_shots.verticalHeader().setVisible(False)

        self.verticalLayout_4.addWidget(self.table_shots)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.button_add_shot = QPushButton(self.dockWidgetContents_2)
        self.button_add_shot.setObjectName(u"button_add_shot")

        self.horizontalLayout_4.addWidget(self.button_add_shot)

        self.button_remove_shots = QPushButton(self.dockWidgetContents_2)
        self.button_remove_shots.setObjectName(u"button_remove_shots")

        self.horizontalLayout_4.addWidget(self.button_remove_shots)

        self.horizontalSpacer_3 = QSpacerItem(490, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.button_import_shots = QPushButton(self.dockWidgetContents_2)
        self.button_import_shots.setObjectName(u"button_import_shots")

        self.horizontalLayout_4.addWidget(self.button_import_shots)

        self.button_export_shots = QPushButton(self.dockWidgetContents_2)
        self.button_export_shots.setObjectName(u"button_export_shots")

        self.horizontalLayout_4.addWidget(self.button_export_shots)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_2)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Assignments", None))
        self.button_play.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.button_stop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.label_progress.setText("")
        self.progressBar.setFormat(QCoreApplication.translate("MainWindow", u"%p%", None))
        self.button_export_assignments.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.checkBox_live.setText(QCoreApplication.translate("MainWindow", u"Live", None))
        self.label_artists.setText(QCoreApplication.translate("MainWindow", u"Artists", None))
        self.button_add_artist.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.button_remove_artists.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.button_import_artists.setText(QCoreApplication.translate("MainWindow", u"Import", None))
        self.button_export_artists.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.label_shots.setText(QCoreApplication.translate("MainWindow", u"Shots", None))
        self.button_add_shot.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.button_remove_shots.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.button_import_shots.setText(QCoreApplication.translate("MainWindow", u"Import", None))
        self.button_export_shots.setText(QCoreApplication.translate("MainWindow", u"Export", None))
    # retranslateUi

