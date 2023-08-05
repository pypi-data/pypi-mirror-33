import pyloudnorm
import numpy as np
import soundfile as sf

data, rate = sf.read("../tests/data/sine_1000.wav")
print(data)
print("soundfile", data.shape)

meter = pyloudnorm.loudness.Meter(rate)
loudness = meter.measure_gated_loudness(data, 1)
print(loudness)


