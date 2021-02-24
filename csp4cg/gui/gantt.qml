import QtQuick 2.0

// TODO: Position text in the middle of bars
// TODO: Resize text when bar width is smaller

Item {
    readonly property int gantBarPadding: 2  // padding between gant tasks
    readonly property int gantBarHeight: 42
    readonly property int verticalHeaderWidth: 200
    readonly property int horizontalZoom: 20

    readonly property string colorHeaderFb: "#444"
    readonly property string colorHeaderBg: "#292929"
    readonly property string colorBg: "#222"
    readonly property string colorText: "#CCC"
    readonly property string colorBarBg: "#666"
    readonly property string colorBarBorder: "#999"

    Rectangle {
        anchors.fill: parent
        color: colorBg

        Rectangle {
            anchors.bottom: parent.bottom
            anchors.top: parent.top
            width: verticalHeaderWidth
            color: colorHeaderBg
            Column {
                Repeater {
                    model: artists
                    Rectangle {
                        width: verticalHeaderWidth
                        height: gantBarHeight
                        color: colorHeaderFb
                        Text {
                            text: model.display
                            color: colorText
                            anchors.verticalCenter: parent.verticalCenter
                        }
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
                color: colorBarBg
                border.width: 1
                border.color: colorBarBorder
                Text {
                    text: shot
                    color: colorText
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }
    }

}
