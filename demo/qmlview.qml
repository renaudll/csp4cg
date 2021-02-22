import QtQuick 2.0
import QtQml.Models 2.2

Item {
  width: 640
  height: 480

  Column {
    id: columns

    anchors.fill: parent

    Repeater {
      model: artists
      delegate: Item {
        height: childrenRect.height
        width: columns.width

        Text {
          text: name
        }

        // This repeater does not have a delegate: a DelegateModel
        // has its own delegate
        Repeater {

          // DelegateModel is the trick to allow accessing nested rows on a model
          // It holds the model (artists), set the rootIndex (the current artist row)
          // and has a delegate to draw the Shots rectangles

          model: DelegateModel {
            model: artists

            // here the value index is an integer: it's the current row number
            // We call QAbstractItemModel.index(row, column) to get an actual
            // QModelIndex to become the rootIndex of the DelegateModel
            rootIndex: artists.index(index, 0)

            delegate: Rectangle {
              x: 100 + startDate  // starts at 100 to not draw over the artist name
              width: endDate - startDate
              height: 10
              color: "green"

              Text {
                text: name
              }
            }
          }
        }
      }
    }
  }
}
