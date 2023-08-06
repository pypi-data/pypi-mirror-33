from obspy import read
from eqcorrscan.utils.plotting import spec_trace
st = read()
spec_trace(st, trc='white')