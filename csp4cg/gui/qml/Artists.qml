import QtQuick.Layouts 1.15
import QtQuick 2.15
import QtQuick.Controls 2.5
import Qt.labs.qmlmodels 1.0

ColumnLayout {
    Label {text: "Artists"}

    // QtQuick.Controls2 TableView Header...
    Row {
        id: listArtistsHeader
        height: 40
        Repeater {
            model: listArtists.model.columnCount()
            Rectangle {
                width: 100  // TODO: Set width from model?
                height: parent.height
                border.color: "grey"
                border.width: 1
                color: "grey"
                Text {
                    text: listArtists.model.headerData(index, Qt.Horizontal)
                }
            }
        }
    }
    TableView {
        id: listArtists
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: artistsModel

        delegate: Rectangle {
            implicitWidth: 100
            implicitHeight: 50
            TextField { text: display }
        }
    }
    Row {
        Button {
            text: "Add"
        }
        Button {
            text: "Remove"
        }
    }
}
