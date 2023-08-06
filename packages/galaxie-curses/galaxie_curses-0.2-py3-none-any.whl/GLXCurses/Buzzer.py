#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

# http://www.tonalsoft.com/pub/news/pitch-bend.aspx
# http://musicmasterworks.com/WhereMathMeetsMusic.html
# http://www.tonalsoft.com/enc/number/12edo.aspx

try:
    # noinspection PyUnresolvedReferences
    import winsound

    def play_sound(frequency, duration):
        winsound.Beep(frequency, duration)

except ImportError:
    import os


    def play_sound(frequency, duration):
        """
        Play a sound via the Buzzer of the computer

        :param frequency: frequence in Hertz (HZ) of the note to play
        :type frequency: int
        :param duration: how many time we play the note in Millisecond (ms)
        :type duration: int
        """
        # apt-get install beep
        os.system('beep -f %s -l %s' % (frequency, duration))


class Buzzer(object):
    """
    :Description:

    The famous buzzer class, why not implement a wireless protocol with the buzzer ?

    .. py:attribute:: tempo

           Beats per minute (bpm) is a unit typically used as a measure of tempo

              :Type: :py:data:`float`
              :Flags: Read / Write
              :Default value: 110.0
    """
    def __init__(self):
        #
        self.tempo = 110.0

        # Set Notes
        self.midi_notes = list()
        # Octave -5
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([-5, 0, 'C',       8.1757989156, -6.9000000])
        self.midi_notes.append([-5, 1, 'C#/Db',   8.6619572180, -6.9000000])
        self.midi_notes.append([-5, 2, 'D',       9.1770239974, -6.9000000])
        self.midi_notes.append([-5, 3, 'D#/Eb',   9.7227182413, -6.9000000])
        self.midi_notes.append([-5, 4, 'E',       10.3008611535, -6.9000000])
        self.midi_notes.append([-5, 5, 'F',       10.9133822323, -6.9000000])
        self.midi_notes.append([-5, 6, 'F#/Gb',   11.5623257097, -6.9000000])
        self.midi_notes.append([-5, 7, 'G',       12.2498573744, -6.9000000])
        self.midi_notes.append([-5, 8, 'G#/Ab',   12.9782717994, -6.9000000])
        self.midi_notes.append([-5, 9, 'A',       13.7500000000, -6.9000000])
        self.midi_notes.append([-5, 10, 'A#/Bb',  14.5676175474, -5.9000000])
        self.midi_notes.append([-5, 11, 'B',      15.4338531643, -5.8000000])

        # Octave -4
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([-4, 12, 'C',      16.3515978313, -5.700])
        self.midi_notes.append([-4, 13, 'C#/Db',  17.3239144361, -5.600])
        self.midi_notes.append([-4, 14, 'D',      18.3540479948, -5.500])
        self.midi_notes.append([-4, 15, 'D#/Eb',  19.4454364826, -6.9000000])
        self.midi_notes.append([-4, 16, 'E',      20.6017223071, -6.9000000])
        self.midi_notes.append([-4, 17, 'F',      21.8267644646, -6.9000000])
        self.midi_notes.append([-4, 18, 'F#/Gb',  23.1246514195, -6.9000000])
        self.midi_notes.append([-4, 19, 'G',      24.4997147489, -6.9000000])
        self.midi_notes.append([-4, 20, 'G#/Ab',  25.9565435987, -6.9000000])
        self.midi_notes.append([-4, 21, 'A',      27.5000000000, -6.9000000])
        self.midi_notes.append([-4, 22, 'A#/Bb',  29.1352350949, -5.9000000])
        self.midi_notes.append([-4, 23, 'B',      30.8677063285, -5.8000000])

        # Octave -3
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([-3, 24, 'C',      32.7031956626, -5.700])
        self.midi_notes.append([-3, 25, 'C#/Db',  34.6478288721, -5.600])
        self.midi_notes.append([-3, 26, 'D',      36.7080959897, -5.500])
        self.midi_notes.append([-3, 27, 'D#/Eb',  38.8908729653, -6.9000000])
        self.midi_notes.append([-3, 28, 'E',      41.2034446141, -6.9000000])
        self.midi_notes.append([-3, 29, 'F',      43.6535289291, -6.9000000])
        self.midi_notes.append([-3, 30, 'F#/Gb',  46.2493028390, -6.9000000])
        self.midi_notes.append([-3, 31, 'G',      48.9994294977, -6.9000000])
        self.midi_notes.append([-3, 32, 'G#/Ab',  51.9130871975, -6.9000000])
        self.midi_notes.append([-3, 33, 'A',      55.0000000000, -6.9000000])
        self.midi_notes.append([-3, 34, 'A#/Bb',  58.2704701898, -5.9000000])
        self.midi_notes.append([-3, 35, 'B',      61.7354126570, -5.8000000])

        # Octave -2
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([-2, 36, 'C',      65.4063913251, -5.700])
        self.midi_notes.append([-2, 37, 'C#/Db',  69.2956577442, -5.600])
        self.midi_notes.append([-2, 38, 'D',      73.4161919794, -5.500])
        self.midi_notes.append([-2, 39, 'D#/Eb',  77.7817459305, -6.9000000])
        self.midi_notes.append([-2, 40, 'E',      82.4068892282, -6.9000000])
        self.midi_notes.append([-2, 41, 'F',      87.3070578583, -6.9000000])
        self.midi_notes.append([-2, 42, 'F#/Gb',  92.4986056779, -6.9000000])
        self.midi_notes.append([-2, 43, 'G',      97.9988589954, -6.9000000])
        self.midi_notes.append([-2, 44, 'G#/Ab',  103.8261743950, -6.9000000])
        self.midi_notes.append([-2, 45, 'A',      110.0000000000, -6.9000000])
        self.midi_notes.append([-2, 46, 'A#/Bb',  116.5409403795, -5.9000000])
        self.midi_notes.append([-2, 47, 'B',      123.4708253140, -5.8000000])

        # Octave -1
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([-1, 48, 'C',      130.8127826503, -5.700])
        self.midi_notes.append([-1, 49, 'C#/Db',  138.5913154884, -5.600])
        self.midi_notes.append([-1, 50, 'D',      146.8323839587, -5.500])
        self.midi_notes.append([-1, 51, 'D#/Eb',  155.5634918610, -6.9000000])
        self.midi_notes.append([-1, 52, 'E',      164.8137784564, -6.9000000])
        self.midi_notes.append([-1, 53, 'F',      174.6141157165, -6.9000000])
        self.midi_notes.append([-1, 54, 'F#/Gb',  184.9972113558, -6.9000000])
        self.midi_notes.append([-1, 55, 'G',      195.9977179909, -6.9000000])
        self.midi_notes.append([-1, 56, 'G#/Ab',  207.6523487900, -6.9000000])
        self.midi_notes.append([-1, 57, 'A',      220.0000000000, -6.9000000])
        self.midi_notes.append([-1, 58, 'A#/Bb',  233.0818807590, -5.9000000])
        self.midi_notes.append([-1, 59, 'B',      246.9416506281, -5.8000000])

        # Octave 0
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([0,  60, 'C',      261.6255653006, -5.700])
        self.midi_notes.append([0,  61, 'C#/Db',  277.1826309769, -5.600])
        self.midi_notes.append([0,  62, 'D',      293.6647679174, -5.500])
        self.midi_notes.append([0,  63, 'D#/Eb',  311.1269837221, -6.9000000])
        self.midi_notes.append([0,  64, 'E',      329.6275569129, -6.9000000])
        self.midi_notes.append([0,  65, 'F',      349.2282314330, -6.9000000])
        self.midi_notes.append([0,  66, 'F#/Gb',  369.9944227116, -6.9000000])
        self.midi_notes.append([0,  67, 'G',      391.9954359817, -6.9000000])
        self.midi_notes.append([0,  68, 'G#/Ab',  415.3046975799, -6.9000000])
        self.midi_notes.append([0,  69, 'A',      440.0000000000, -6.9000000])
        self.midi_notes.append([0,  70, 'A#/Bb',  466.1637615181, -5.9000000])
        self.midi_notes.append([0,  71, 'B',      493.8833012561, -5.8000000])

        # Octave 1
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([1,  72, 'C',      523.2511306012, -5.700])
        self.midi_notes.append([1,  73, 'C#/Db',  554.3652619537, -5.600])
        self.midi_notes.append([1,  74, 'D',      587.3295358348, -5.500])
        self.midi_notes.append([1,  75, 'D#/Eb',  622.2539674442, -6.9000000])
        self.midi_notes.append([1,  76, 'E',      659.2551138257, -6.9000000])
        self.midi_notes.append([1,  77, 'F',      698.4564628660, -6.9000000])
        self.midi_notes.append([1,  78, 'F#/Gb',  739.9888454233, -6.9000000])
        self.midi_notes.append([1,  79, 'G',      783.9908719635, -6.9000000])
        self.midi_notes.append([1,  80, 'G#/Ab',  830.6093951599, -6.9000000])
        self.midi_notes.append([1,  81, 'A', 	  880.0000000000, -6.9000000])
        self.midi_notes.append([1,  82, 'A#/Bb',  932.3275230362, -5.9000000])
        self.midi_notes.append([1,  83, 'B',      987.7666025122, -5.8000000])

        # Octave 2
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([2,  84, 'C',      1046.5022612024, -5.700])
        self.midi_notes.append([2,  85, 'C#/Db',  1108.7305239075, -5.600])
        self.midi_notes.append([2,  86, 'D',      1174.6590716696, -5.500])
        self.midi_notes.append([2,  87, 'D#/Eb',  1244.5079348883, -6.9000000])
        self.midi_notes.append([2,  88, 'E', 	  1318.5102276515, -6.9000000])
        self.midi_notes.append([2,  89, 'F',      1396.9129257320, -6.9000000])
        self.midi_notes.append([2,  90, 'F#/Gb',  1479.9776908465, -6.9000000])
        self.midi_notes.append([2,  91, 'G',      1567.9817439270, -6.9000000])
        self.midi_notes.append([2,  92, 'G#/Ab',  1661.2187903198, -6.9000000])
        self.midi_notes.append([2,  93, 'A', 	  1760.0000000000, -6.9000000])
        self.midi_notes.append([2,  94, 'A#/Bb',  1864.6550460724, -5.9000000])
        self.midi_notes.append([2,  95, 'B',      1975.5332050245, -5.8000000])

        # Octave 3
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([3,  96,  'C',     2093.0045224048,  -5.700])
        self.midi_notes.append([3,  97,  'C#/Db', 2217.4610478150,  -5.600])
        self.midi_notes.append([3,  98,  'D',     2349.3181433393,  -5.500])
        self.midi_notes.append([3,  99,  'D#/Eb', 2489.0158697766,  -6.9000000])
        self.midi_notes.append([3,  100, 'E',     2637.02045530305, -6.9000000])
        self.midi_notes.append([3,  101, 'F',     2793.8258514640,  -6.9000000])
        self.midi_notes.append([3,  102, 'F#/Gb', 2959.9553816931,  -6.9000000])
        self.midi_notes.append([3,  103, 'G',     3135.9634878540,  -6.9000000])
        self.midi_notes.append([3,  104, 'G#/Ab', 3322.4375806396,  -6.9000000])
        self.midi_notes.append([3,  105, 'A', 	  3520.0000000000,  -6.9000000])
        self.midi_notes.append([3,  106, 'A#/Bb', 3729.3100921447,  -5.9000000])
        self.midi_notes.append([3,  107, 'B',     3951.0664100490,  -5.8000000])

        # Octave 4
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([4,  108, 'C',     4186.0090448096,  -5.700])
        self.midi_notes.append([4,  109, 'C#/Db', 4434.9220956300,  -5.600])
        self.midi_notes.append([4,  110, 'D',     4698.6362866785,  -5.500])
        self.midi_notes.append([4,  111, 'D#/Eb', 4978.0317395533,  -6.9000000])
        self.midi_notes.append([4,  112, 'E',     5274.0409106059, -6.9000000])
        self.midi_notes.append([4,  113, 'F',     5587.6517029281,  -6.9000000])
        self.midi_notes.append([4,  114, 'F#/Gb', 5919.9107633862,  -6.9000000])
        self.midi_notes.append([4,  115, 'G',     6271.92697571,  -6.9000000])
        self.midi_notes.append([4,  116, 'G#/Ab', 6644.8751612791,  -6.9000000])
        self.midi_notes.append([4,  117, 'A', 	  7040.0000000000,  -6.9000000])
        self.midi_notes.append([4,  118, 'A#/Bb', 7458.6201842894,  -5.9000000])
        self.midi_notes.append([4,  119, 'B',     7902.1328200980,  -5.8000000])

        # Octave 5
        # Midi Ocatave, Midi Note Number, Note Name, Frequency Hz, Absolute Cents
        self.midi_notes.append([5,  120, 'C',     8372.0180896192,  -5.700])
        self.midi_notes.append([5,  121, 'C#/Db', 8869.8441912599,  -5.600])
        self.midi_notes.append([5,  122, 'D',     9397.2725733570,  -5.500])
        self.midi_notes.append([5,  123, 'D#/Eb', 9956.0634791066,  -6.9000000])
        self.midi_notes.append([5,  124, 'E',     10548.0818212118, -6.9000000])
        self.midi_notes.append([5,  125, 'F',     11175.3034058561,  -6.9000000])
        self.midi_notes.append([5,  126, 'F#/Gb', 11839.8215267723,  -6.9000000])
        self.midi_notes.append([5,  127, 'G',     12543.8539514160,  -6.9000000])

    def get_tempo(self):
        """
        Get the tempo attribute

        :return: tempo attribute value is in BPM
        :rtype: float
        """
        return float(self.tempo)

    def set_tempo(self, tempo=110.0):
        """
        Set the tempo attribute

        :param tempo: tempo value in BPM
        :type tempo: float
        """
        self.tempo = float(tempo)

    def get_tempo_to_ms(self):
        """
        Get actual tempo value in Millisecond (ms)

        :return: tempo value in ms
        :rtype: int
        """
        return int(60000 / self.get_tempo())

    def get_croche(self):
        """
        Get the **Croche** it consist to devise the tempo by 2

        :return: tempo value div by 2 in Millisecond (ms)
        :rtype: int
        """
        return int(self.get_tempo_to_ms() / 2)

    def get_double_croche(self):
        """
        Get the **Double Croche** it consist to devise the tempo by 4

        :return: tempo value div by 4 in Millisecond (ms)
        :rtype: int
        """
        return int(self.get_tempo_to_ms() / 4)

    def get_triple_croche(self):
        """
        Get the **Triple Croche** it consist to devise the tempo by 8

        :return: tempo value div by 8 in Millisecond (ms)
        :rtype: int
        """
        return self.get_tempo_to_ms() / 8

    def get_blanche(self):
        """
        Get the **Blanche** it consist to multiply the tempo by 2

        :return: tempo value div by 2 in Millisecond (ms)
        :rtype: int
        """
        return int(self.get_tempo_to_ms() * 2)

    def get_triolet(self):
        """
        Get the **Triolet** it consist to multiply the tempo by 3

        :return: tempo value div by 3 in Millisecond (ms)
        :rtype: int
        """
        return int(self.get_tempo_to_ms() / 3)

    def get_notes(self):
        """
        Get MIDI notes list , each item contain a list as container

        **Notes Structure:**
        list(Octave, Midi_Note_Number, Note_Name, Frequency_Hz, Absolute_Cents)

        .. code: python

           self.midi_notes = list()
           self.midi_notes.append([1,  72, 'C',      523.2511306012, -5.700])

        :return: the entrie midi note list
        :rtype: list(list(),list(),list())
        """
        return self.midi_notes

    @staticmethod
    def get_ms_to_tempo(ms):
        """
        Get the conversion of a ms value to a tempo value

        :param ms: tempo value in Millisecond (ms)
        :type ms: int
        :return: 60000 divised by Millisecond (ms) value
        :rtype: float
        """
        return float(60000 / ms)

    def get_tempo_to_hertz(self):
        """
        Get the conversion of the tempo in BPM to the frequency in Hz

        :return: tempo divised by 60
        :rtype: int
        """
        return int(self.get_tempo() / 60)

    @staticmethod
    def get_hertz_to_ms(hz):
        """
        Get the conversion of a **Hz** value to a **ms** value

        :param hz: frequence in Hertz (**Hz**)
        :type hz: int
        :return: the duration of the period frequency in ms (**ms**)
        :rtype: int
        """
        return int((1 / hz) * 1000)

if __name__ == '__main__':
    buzzer = Buzzer()
    buzzer.set_tempo(110)
    for i in range(100):
        for note in buzzer.get_notes():
            if note[3] > 50:
                line = ''
                line += 'Midi Note:'
                line += ' '
                line += str(note[1])
                print (line)
                play_sound(int(note[3]), buzzer.get_triple_croche())

        for note in reversed(buzzer.get_notes()):
            if note[3] > 50:
                line = ''
                line += 'Midi Note:'
                line += ' '
                line += str(note[1])
                print (line)
                play_sound(int(note[3]), buzzer.get_triple_croche())
