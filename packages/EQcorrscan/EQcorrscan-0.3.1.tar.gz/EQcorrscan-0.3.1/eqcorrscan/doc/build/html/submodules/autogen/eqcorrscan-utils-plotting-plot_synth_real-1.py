from eqcorrscan.utils.plotting import plot_synth_real
from obspy import read, Stream, Trace
from eqcorrscan.utils.synth_seis import seis_sim
import os
real = read()
synth = Stream(Trace(seis_sim(sp=100, flength=200)))
synth[0].stats.station = 'RJOB'
synth[0].stats.channel = 'EHZ'
synth[0].stats.sampling_rate = 100
synth.filter('bandpass', freqmin=2, freqmax=8)
real = real.select(station='RJOB', channel='EHZ').detrend('simple').            filter('bandpass', freqmin=2, freqmax=8)
real.trim(starttime=real[0].stats.starttime + 4.9,
          endtime=real[0].stats.starttime + 6.9).detrend('simple')
plot_synth_real(real_template=real, synthetic=synth, size=(7, 4))