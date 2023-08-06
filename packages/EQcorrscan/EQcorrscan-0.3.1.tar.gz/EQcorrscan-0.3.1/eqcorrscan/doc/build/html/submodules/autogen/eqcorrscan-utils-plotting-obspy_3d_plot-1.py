from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from eqcorrscan.utils.plotting import obspy_3d_plot
client = Client('IRIS')
t1 = UTCDateTime(2012, 3, 26)
t2 = t1 + 86400
catalog = client.get_events(starttime=t1, endtime=t2, latitude=-43,
                            longitude=170, maxradius=5)
inventory = client.get_stations(starttime=t1, endtime=t2, latitude=-43,
                                longitude=170, maxradius=10)
obspy_3d_plot(inventory=inventory, catalog=catalog)