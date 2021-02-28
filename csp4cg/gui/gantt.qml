import QtQuick 2.0
import QtQml.Models 2.2

// TODO: Position text in the middle of bars
// TODO: Resize text when bar width is smaller

Item {
    readonly property int gantBarPadding: 2  // padding between gant tasks
    readonly property int gantBarHeight: 42
    readonly property int verticalHeaderWidth: 200
    readonly property int horizontalZoom: 20

    readonly property string colorHeaderFg: "#444"
    readonly property string colorHeaderFgSelected: "red"
    readonly property string colorHeaderBg: "#292929"
    readonly property string colorBg: "#222"
    readonly property string colorText: "#CCC"
    readonly property string colorBarBg: "#222"
    readonly property string colorBarBgSelected: "#666"
    readonly property string colorBarBorder: "#999"

    Rectangle {
        anchors.fill: parent
        color: colorBg

        // Artists
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.top: parent.top
            width: verticalHeaderWidth
            color: colorHeaderBg
            Column {
                Repeater {
                    model: DelegateModel {
                        model: artists
                        delegate: Rectangle {
                            id: item
                            width: verticalHeaderWidth
                            height: gantBarHeight
                            color: artistsSelectionModel.isRowSelected(index) ? colorHeaderFgSelected : colorHeaderFg
                            Text {
                                text: model.display
                                color: colorText
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    artistsSelectionModel.select(artists.index(index, 0), ItemSelectionModel.Select | ItemSelectionModel.Current | ItemSelectionModel.Rows)
                                }
                            }
                        }
                    }
                }
            }
        }

        // Shots
        Repeater {
            model: DelegateModel {
                model: assignments
                delegate: Rectangle {
                    id: item
                    x: verticalHeaderWidth + coordX * horizontalZoom + gantBarPadding
                    y: coordY * gantBarHeight + gantBarPadding
                    width: gantBarWidth * horizontalZoom - gantBarPadding
                    height: gantBarHeight - gantBarPadding
    //                color: colorBarBgSelected
                    color: highlight ? colorBarBgSelected : colorBarBg
                    border.width: 1
                    border.color: colorBarBorder
                    Text {
                        text: shot
                        color: colorText
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            console.log(item)
//                            shotsSelectionModel.select(shots.index(index, 0), ItemSelectionModel.Select | ItemSelectionModel.Current)
//                            console.log(shotsSelectionModel.selectedIndexes)
//                            console.log(shotsSelectionModel.hasSelection)
                        }
                    }
                }
            }
        }

        ItemSelectionModel {
            id: shotsSelectionModel
            model: shots
        }
    }

}
