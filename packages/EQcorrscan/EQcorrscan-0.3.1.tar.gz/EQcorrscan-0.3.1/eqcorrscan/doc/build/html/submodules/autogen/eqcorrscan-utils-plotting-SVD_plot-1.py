from obspy import read
import glob, os
from eqcorrscan.utils.plotting import SVD_plot
from eqcorrscan.utils.clustering import svd, SVD_2_stream
wavefiles = glob.glob(os.path.realpath('../../..') +
                     '/tests/test_data/WAV/TEST_/*')
streams = [read(w) for w in wavefiles[1:10]]
stream_list = []
for st in streams:
    tr = st.select(station='GCSZ', channel='EHZ')
    st.detrend('simple').resample(100).filter('bandpass', freqmin=5,
                                              freqmax=40)
    stream_list.append(tr)
svec, sval, uvec, stachans = svd(stream_list=stream_list)
SVstreams = SVD_2_stream(uvectors=uvec, stachans=stachans, k=3,
                         sampling_rate=100)
SVD_plot(SVStreams=SVstreams, SValues=sval,
         stachans=stachans)