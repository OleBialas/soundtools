import slab
import numpy


def test_properties():
    slab.calibrate(intensity=80, make_permanent=False)
    sound = slab.Sound(numpy.ones([10, 2]), samplerate=10)
    sound = sound.repeat(n=5)
    assert sound.samplerate == 10
    assert sound.nsamples == 50
    assert sound.duration == 5.0
    assert sound.nchannels == 2


def test_tone():
    sound = slab.Sound.multitone_masker()
    sound = slab.Sound.clicktrain()
    # sound = slab.Sound.dynamicripple() --> does not work
    sound = slab.Sound.chirp()
    sound = slab.Sound.tone()
    sound = slab.Sound.harmoniccomplex(f0=200, amplitude=[0, -10, -20, -30])
    sound.level = 80


def test_vowel():
    vowel = slab.Sound.vowel(vowel='a', duration=.5, samplerate=8000)
    vowel.ramp()
    vowel.spectrogram(dyn_range=50, show=False)
    vowel.spectrum(low=100, high=4000, log_power=True, show=False)
    vowel.waveform(start=0, end=.1, show=False)
    vowel.cochleagram(show=False)
    vowel.vocode()


def test_noise():
    sound = slab.Sound.erb_noise()
    sound = slab.Sound.powerlawnoise()
    sound = slab.Sound.irn()
    sound = slab.Sound.whitenoise(normalise=True)
    assert max(sound) <= 1
    assert min(sound) >= -1


def test_manipulations():
    sound1 = slab.Sound.pinknoise()
    sound2 = slab.Sound.pinknoise()
    sound1.pulse()
    sound1.am()
    sound2.aweight()
    sound = slab.Sound.crossfade(sound1, sound2, overlap=0.01)
    for feat in ['centroid', 'fwhm', 'flux', 'rolloff', 'flatness']:
        sound.spectral_feature(feature=feat)
    sound.crest_factor()
    sound.onset_slope()
