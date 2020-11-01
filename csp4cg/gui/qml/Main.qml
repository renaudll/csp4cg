import QtQuick.Layouts 1.15
import QtQuick 2.15
import QtQuick.Controls 2.5
import Qt.labs.qmlmodels 1.0

ApplicationWindow {
    id: window
    visible: true

    ColumnLayout {

        anchors.fill: parent

        RowLayout {
            Assignations {}
            ColumnLayout {
                Artists {}
                Shots {}
            }
        }

        Rectangle {
            id: footer
            Layout.fillWidth: true
            color: "grey"
            height: 42

            RowLayout {
                anchors.top: parent.top
                anchors.bottom: parent.bottom

                Button {
                    text: "Play"
                    Layout.fillHeight: true
                    onClicked: api.play()
                }
                Button {
                    text: "Stop"
                    Layout.fillHeight: true
                }
            }
        }
    }
    Connections {
        target: api
    }
}