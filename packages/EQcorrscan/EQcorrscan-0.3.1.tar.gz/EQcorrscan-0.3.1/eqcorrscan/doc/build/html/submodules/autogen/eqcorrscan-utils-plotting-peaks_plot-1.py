import matplotlib.pyplot as plt
import numpy as np
from eqcorrscan.utils import findpeaks
from eqcorrscan.utils.plotting import peaks_plot
from obspy import UTCDateTime
data = np.random.randn(200)
data[30]=100
data[60]=40
threshold = 10
peaks = findpeaks.find_peaks2_short(data, threshold, 3)
peaks_plot(data=data, starttime=UTCDateTime("2008001"),
           samp_rate=10, peaks=peaks)