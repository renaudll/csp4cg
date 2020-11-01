import QtQuick.Layouts 1.15
import QtQuick 2.15
import QtQuick.Controls 2.5
import Qt.labs.qmlmodels 1.0

ColumnLayout {
    Label { text: "Assignations" }

    TableView {
        id: assignationView
        Layout.fillWidth: true
        Layout.fillHeight: true
        columnWidthProvider: function (column) { return 100; }

        model: artistAssignationModel
        delegate: Rectangle {
            implicitWidth: 100
            implicitHeight: 50
            Text {
                text: display
            }
        }
    }
}