import datetime as dt
import numpy as np

from silx.gui import qt
from silx.gui.plot import Plot1D, TickMode


app = qt.QApplication([])

base = dt.datetime.today()
dates = [base - dt.timedelta(days=x) for x in range(0, 50)]

x = np.array([d.timestamp() for d in dates], dtype=np.uint64)

np.random.seed(seed=1)
y = np.random.random(x.shape) * 12 - 3

plot1D = Plot1D(backend='gl')
xAxis = plot1D.getXAxis()
xAxis.setTickMode(TickMode.TIME_SERIES)
xAxis.setTimeZone('UTC')

def later():
    xAxis.setTimeZone(dt.timezone(dt.timedelta(hours=12)))
    print('set time zone', xAxis.getTimeZone())

qt.QTimer.singleShot(4000, later)

curve = plot1D.addCurve(x=x, y=y, legend='curve')  
plot1D.show()

app.exec_()

