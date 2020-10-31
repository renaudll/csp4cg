// https://github.com/csuft/VideoTimeline/blob/master/v2/resource/qml/Ruler.qml
import QtQuick 2.0
import QtQuick.Controls 1.0

Rectangle {
    property int stepSize: 10

    id: rulerTop
    height: 30

    Repeater {
        model: parent.width / stepSize
        Rectangle {
            anchors.bottom: rulerTop.bottom
            height: 14
            width: 1
            x: index * stepSize
            color: "#999"
            Label {
                anchors.bottom: parent.top
                color: "#999"
                text: index
                font.pointSize: 7
            }
        }
    }
}