import datetime as dt
import numpy as np

from PyQt5.QtWidgets import QApplication
from silx.gui.plot import Plot1D

if 1:
    BACKEND = 'gl'  # this gives incorrect results
else:
    BACKEND = 'mpl'  # this works

def makePlot1D():

    # Make large value with a relatively small range by creating POSIX time stamps.
    base = dt.datetime.today()
    dates = [base - dt.timedelta(seconds=x) for x in range(0, 2500, 20)]

    x = np.array([d.timestamp() for d in dates], dtype=np.float64)
    np.random.seed(seed=1)
    y = np.random.random(x.shape) * 12 - 3

    print('x range', np.nanmin(x), np.nanmax(x))
    print('y range', np.nanmin(y), np.nanmax(y))

    plot1D = Plot1D(backend=BACKEND)
    xAxis = plot1D.getXAxis()

    curve = plot1D.addCurve(x=x, y=y, legend='curve', symbol='o', fill=True)

    plot1D.addMarker(x=x[0], y=y[0], legend='marker', text='the marker', draggable=True)
    plot1D.addYMarker(y[0], legend='hmarker', text='the H marker', draggable=True)
    plot1D.addXMarker(x[0], legend='vmarker', text='the V marker', draggable=True)

    plot1D.show()

    return plot1D


def main():
    global app, plot
    app = QApplication([])
    plot = makePlot1D()
    app.exec_()

if __name__ == "__main__":
    main()
