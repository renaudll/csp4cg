import QtQuick 2.0
import QtQml.Models 2.2
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


// TODO: Position text in the middle of bars
// TODO: Resize text when bar width is smaller

Item {
    readonly property int gantBarPadding: 0  // padding between gant tasks
    readonly property int gantBarHeight: 42
    readonly property int verticalHeaderWidth: 200
    property int horizontalZoom: 20
    property int horizontalZoomMin: 5

    readonly property string colorHeaderFg: "#444"
    readonly property string colorHeaderFgSelected: "#666666"
    readonly property string colorHeaderBg: "#292929"
    readonly property string gridColor: "#444"
    readonly property string colorBg: "#222"
    readonly property string colorText: "#CCC"
    readonly property string colorBarBg: "#222"
    readonly property string colorBarBgSelected: "#666"
    readonly property string colorBarBorder: "#999"
    readonly property string colorBarDragSelected: "#C66"

    onHorizontalZoomChanged: grid.requestPaint()


    // Any click outside will reset the selection
    MouseArea {
        anchors.fill: parent
        onClicked: {
            artistsSelectionModel.clear()
            tasksSelectionModel.clear()
        }
        onWheel: {
            horizontalZoom = Math.max(horizontalZoomMin, horizontalZoom + (wheel.angleDelta.y / 20));
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Ruler
        RowLayout {
            spacing: 0
            Rectangle {
                color: colorHeaderBg
                width: verticalHeaderWidth
                height: 30
            }
            Ruler {
                color: colorHeaderBg
                Layout.fillWidth: true
                height: 30
                stepSize: horizontalZoom
            }
        }


        RowLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true
            spacing: 0

            // Artists
            Rectangle {
                Layout.fillHeight: true
                width: verticalHeaderWidth
                color: colorHeaderBg
                Column {
                    Repeater {
                        model: DelegateModel {
                            model: artists
                            delegate: Rectangle {
                                id: artist
                                property bool highlighted: true

                                width: verticalHeaderWidth
                                height: gantBarHeight
                                color: highlighted ? colorHeaderFgSelected : colorHeaderFg
                                Text {
                                    text: name
                                    color: colorText
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        artistsSelectionModel.select(artists.index(index, 0), ItemSelectionModel.Select | ItemSelectionModel.Current | ItemSelectionModel.Rows)
                                    }
                                }

                                // Since isRowSelected is not a property, we cannot subscribe to its change.
                                // Using a connection we can subscribe to selectionChanged to update a property.
                                Connections {
                                    target: artistsSelectionModel
                                    function onSelectionChanged() {
                                        artist.highlighted = !artistsSelectionModel.hasSelection | artistsSelectionModel.isRowSelected(index)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillHeight: true
                Layout.fillWidth: true
                color: colorBg

                GantGrid {
                    id: grid
                    anchors.fill: parent
                    wgrid: horizontalZoom
                }



                // Gant bars
                Repeater {
                    model: DelegateModel {
                        model: tasks
                        delegate: Rectangle {
                            id: task
                            property bool highlighted: true

                            x: coordX * horizontalZoom + gantBarPadding
                            y: coordY * gantBarHeight + gantBarPadding
                            width: gantBarWidth * horizontalZoom - gantBarPadding
                            height: gantBarHeight - gantBarPadding
                            color: highlighted ? colorBarBgSelected : colorBarBg
                            border.width: 1
                            border.color: colorBarBorder

                            Image {
                                source: locked ? "stripes.png" : ""
                                fillMode: Image.Tile
                                anchors.fill: parent
                                opacity: 0.5
                            }

                            Text {
                                text: name
                                color: colorText
                                anchors.verticalCenter: parent.verticalCenter
                                x: 4
                            }

                            // Drag proxy
                            Rectangle {
                                property int taskIndex: index
                                id: dragProxy
                                width: task.width
                                height: task.height
                                opacity: 0
                                Drag.active: dragArea.drag.active
                                MouseArea {
                                    id: dragArea
                                    anchors.fill: parent
                                    drag.target: dragProxy

                                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                                    onClicked: {
                                        if (mouse.button === Qt.RightButton)
                                            contextMenu.popup()
                                        tasksSelectionModel.select(tasks.index(index, 0), ItemSelectionModel.Select | ItemSelectionModel.Rows | ItemSelectionModel.Current)
                                    }
                                    onPressed: {
                                        task.opacity = 0.5
                                        dragProxy.opacity = 1
                                    }

                                    onReleased: {
                                        task.opacity = 1
                                        dragProxy.x = 0
                                        dragProxy.y = 0
                                        dragProxy.opacity = 0
                                        if (dragProxy.Drag.target)
                                            manager.onTaskDroppedOnArtist(dragProxy.taskIndex, dragProxy.Drag.target.artistIndex)
                                    }

                                    Menu {
                                        id: contextMenu
                                        MenuItem {
                                            text: "Lock"
                                            onTriggered: {
                                                locked = true
                                            }
                                        }
                                        MenuItem {
                                            text: "Unlock"
                                            onTriggered: {
                                                locked = false
                                            }
                                        }
                                    }
                                }
                            }

                            // Since isRowSelected is not a property, we cannot subscribe to its change.
                            // Using a connection we can subscribe to selectionChanged to update a property.
                            Connections {
                                target: tasksSelectionModel
                                function onSelectionChanged() {
                                    task.highlighted = !tasksSelectionModel.hasSelection || tasksSelectionModel.isRowSelected(index)
                                }
                            }
                        }
                    }
                }

                // Background rows (drop area)
                // Created after the gant bars so they appear on top.
                Column {
                    anchors.fill: parent
                    Repeater {
                        model: DelegateModel {
                            model: artists
                            delegate: DropArea {
                                property string colorKey: colorBg
                                property int artistIndex: index

                                id: dragTarget
                                anchors.left: parent.left
                                anchors.right: parent.right
                                height: gantBarHeight

                                states: [
                                    State {
                                        when: dragTarget.containsDrag
                                        PropertyChanges {
                                            target: backgroundItem
                                            color: colorBarDragSelected
                                            opacity: 0.5
                                        }
                                    }
                                ]

                                Rectangle {
                                    id: backgroundItem
                                    anchors.fill: parent
                                    color: colorBg
                                    opacity: 0
                                }
                            }
                        }
                    }
                }
            }
        }
    }

}
