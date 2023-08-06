from eqcorrscan.core import subspace
from eqcorrscan.utils.plotting import subspace_detector_plot
import os
print('running subspace plot')
detector = subspace.Detector()
detector.read(os.path.join('..', '..', '..', 'tests', 'test_data',
                           'subspace', 'stat_test_detector.h5'))
subspace_detector_plot(detector=detector, stachans='all', size=(10, 7),
                       show=True)