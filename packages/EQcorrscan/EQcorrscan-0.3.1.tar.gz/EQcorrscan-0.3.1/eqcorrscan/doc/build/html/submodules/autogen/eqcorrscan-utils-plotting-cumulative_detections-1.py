import datetime as dt
import numpy as np
from eqcorrscan.utils.plotting import cumulative_detections
dates = []
for i in range(3):
    dates.append([dt.datetime(2012, 3, 26) + dt.timedelta(n)
                  for n in np.random.randn(100)])
cumulative_detections(dates, ['a', 'b', 'c'], show=True)