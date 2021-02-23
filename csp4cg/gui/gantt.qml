import QtQuick 2.0

Item {
    readonly property int gantBarPadding: 2  // padding between gant tasks
    readonly property int gantBarHeight: 42 // gant bar height
    readonly property int verticalHeaderWidth: 200
    readonly property int horizontalZoom: 20

    Column {
        Repeater {
            model: artists
            Rectangle {
                width: verticalHeaderWidth
                height: gantBarHeight
                color: "#333"
                Text {
                    color: "#DDD"
                    text: model.display
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }
    }
    Repeater {
        model: assignments
        Rectangle {
            x: verticalHeaderWidth + coordX * horizontalZoom + gantBarPadding
            y: coordY * gantBarHeight + gantBarPadding
            width: gantBarWidth * horizontalZoom - gantBarPadding
            height: gantBarHeight - gantBarPadding
            border.width: 1
            border.color: "#888"
            color: "#DDD"
            Text {
                text: shot
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
