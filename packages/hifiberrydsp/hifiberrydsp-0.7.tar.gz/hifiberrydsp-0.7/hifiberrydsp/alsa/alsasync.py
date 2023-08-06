'''
Copyright (c) 2018 Modul 9/HiFiBerry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import time
import logging

from threading import Thread

from hifiberrydsp.hardware.sigmatcp import SpiHandler
from hifiberrydsp.hardware.adau145x import Adau145x
from hifiberrydsp.filtering.volume import percent2amplification, amplification2percent


class AlsaSync(Thread):
    '''
    Synchronises a dummy ALSA mixer control with a volume control 
    register of the DSP.
    '''

    def __init__(self, alsa_control, volume_register):
        from alsaaudio import Mixer

        self.alsa_control = alsa_control
        self.volume_register = volume_register
        self.dsp = Adau145x
        self.volume_register_length = self.dsp.REGISTER_WORD_LENGTH
        self.finished = False
        self.pollinterval = 0.1
        self.spi = SpiHandler
        self.paused = False
        self.mixer = Mixer(alsa_control)
        self.dspvol = 0
        self.alsavol = 0

        if self.mixer == None:
            logging.error("ALSA mixer %s not found", alsa_control)

    def set_volume_register(self, volume_register):
        self.volume_register = volume_register

    def update_alsa(self, value):
        from alsaaudio import MIXER_CHANNEL_ALL
        self.mixer.setvolume(int(value), MIXER_CHANNEL_ALL)

    def update_dsp(self, value):
        # convert percent to multiplier
        volume = percent2amplification(value)

        # write multiplier to DSP
        dspdata = self.dsp.decimal_repr(volume)
        self.spi.write(self.volume_register, dspdata)

    def read_data(self):
        self.read_dsp_data()
        self.read_alsa_data()

    def read_alsa_data(self):
        volumes = self.mixer.getvolume()
        channels = 0
        vol = 0
        for i in range(len(volumes)):
            channels += 1
            vol += volumes[i]

        if channels > 0:
            vol = vol / channels

        if vol != self.alsavol:
            logging.debug("ALSA volume changed to {}%".format(vol))
            self.alsavol = vol

    def read_dsp_data(self):
        dspdata = self.spi.read(
            self.volume_register, self.volume_register_length)

        # Convert to percent and round to full percent
        vol = int(amplification2percent(self.dsp.decimal_val(dspdata)))
        if vol != self.dspvol:
            logging.debug("DSP volume changed to {}%".format(vol))
            self.alsavol = vol

    def check_sync(self):
        self.alsavol_prev = self.alsavol
        self.dspvol_prev = self.dspvol
        self.read_data()

        # Check if one of the control has changed and update the other
        # one. If both have changed, ALSA takes precedence
        if self.alsavol != self.alsavol_prev:
            logging.debug("Updating DSP volume from ALSA")
            self.update_dsp(self.alsavol)
        elif self.dspvol != self.dspvol_prev:
            logging.debug("Updating ALSA volume from DSP")
            self.update_alsa(self.dspvol)
        elif self.dspvol != self.alsavol:
            logging.debug("Updating DSP volume from ALSA")
            self.update_dsp(self.alsavol)

    def run(self):
        if self.mixer is None:
            logging.info("ALSA mixer not defined, stopping")

        if self.volume_register is None:
            logging.info("DSP volume register not defined, stopping")

        while not(self.finished):
            if not(self.paused):
                self.check_sync()
            time.sleep(self.pollinterval)
