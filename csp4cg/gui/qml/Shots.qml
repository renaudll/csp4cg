import QtQuick.Layouts 1.15
import QtQuick 2.15
import QtQuick.Controls 2.5
import Qt.labs.qmlmodels 1.0

ColumnLayout {
    Label { text: "Shots"}

    TableView {
        id: listShots
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: shotsModel

        delegate: Rectangle {
            implicitWidth: 100
            implicitHeight: 50
            Text { text: display }
        }
    }
}
