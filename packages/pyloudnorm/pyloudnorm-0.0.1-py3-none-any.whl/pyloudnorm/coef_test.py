from loudness import IIRfilter
import numpy as np

hshelf = IIRfilter(4.0, 1/np.sqrt(2), 1500.0, 48000, 'high_shelf')
print(hshelf)

hpass = IIRfilter(0.0, 1/np.sqrt(2), 53.8, 48000, 'high_pass')
print(hpass)
