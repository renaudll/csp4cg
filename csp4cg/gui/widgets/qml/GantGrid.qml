// Inspired from https://stackoverflow.com/a/46649475
import QtQuick 2.0

Canvas {
    property int wgrid: 10

    anchors.fill : parent
    onPaint: {
        var ctx = getContext("2d")

        ctx.clearRect(0, 0, width, height)

        ctx.lineWidth = 1
        ctx.strokeStyle = gridColor
        ctx.beginPath()

        var ncols = width/wgrid
        for(var j=0; j < ncols+1; j++){
            ctx.moveTo(wgrid*j, 0);
            ctx.lineTo(wgrid*j, height);
        }
        ctx.closePath()
        ctx.stroke()
    }
}