import QtQuick 2.0
import QtQml.Models 2.2

Item {
  width: 640
  height: 480

  Column {
    id: columns

    anchors.fill: parent

    Repeater {
      model: DelegateModel {
        model: myModel
        delegate: Rectangle {
          height: childrenRect.height
          width: columns.width
          color: mySelectionModel.isRowSelected(index) ? "lightblue" : "white"  // DOES NOT WORK

          Text {
            text: display
          }

          MouseArea {
            anchors.fill: parent
            onClicked: {
              console.log("Before: " + mySelectionModel.isRowSelected(index))
              mySelectionModel.select(myModel.index(index, 0), ItemSelectionModel.Select | ItemSelectionModel.Current)
              console.log("After: " + mySelectionModel.isRowSelected(index))
            }
          }
        }
      }
    }
  }
}
