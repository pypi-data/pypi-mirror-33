from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from eqcorrscan.utils.plotting import interev_mag
client = Client('IRIS')
t1 = UTCDateTime('2012-03-26T00:00:00')
t2 = t1 + (3 * 86400)
catalog = client.get_events(starttime=t1, endtime=t2, minmagnitude=3)
magnitudes = [event.preferred_magnitude().mag for event in catalog]
times = [event.preferred_origin().time for event in catalog]
interev_mag(times, magnitudes)