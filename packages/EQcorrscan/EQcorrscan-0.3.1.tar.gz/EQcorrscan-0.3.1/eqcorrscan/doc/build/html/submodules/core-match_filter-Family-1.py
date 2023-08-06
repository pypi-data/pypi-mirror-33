from eqcorrscan.core.match_filter import Family, Template
from eqcorrscan.core.match_filter import Detection
from obspy import UTCDateTime
family = Family(
    template=Template(name='a'), detections=[
    Detection(template_name='a', detect_time=UTCDateTime(0) + 200,
              no_chans=8, detect_val=4.2, threshold=1.2,
              typeofdet='corr', threshold_type='MAD',
              threshold_input=8.0),
    Detection(template_name='a', detect_time=UTCDateTime(0),
              no_chans=8, detect_val=4.5, threshold=1.2,
              typeofdet='corr', threshold_type='MAD',
              threshold_input=8.0),
    Detection(template_name='a', detect_time=UTCDateTime(0) + 10,
              no_chans=8, detect_val=4.5, threshold=1.2,
              typeofdet='corr', threshold_type='MAD',
              threshold_input=8.0)])
family.plot(plot_grouped=True)