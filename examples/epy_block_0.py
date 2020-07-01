"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import pmt
from gnuradio import gr
from sklearn.cluster import KMeans

morse ={
    # codes from https://de.wikipedia.org/wiki/Morsezeichen
    # Letters
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    # Figures
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    # Accented
    "À": ".--.-",
    "Ä": ".-.-",
    "È": ".-..-",
    "É": "..-..",
    "Ö": "---.",
    "Ü": "..--",
    "ß": "...--..",
    "CH": "----",
    "~N": "--.--",   # correct that
    # Special characters
    ".": ".-.-.-",   # (AAA) dot
    ",": "--..--",   # (MIM) comma
    ":": "---...",   # (OS)  colon
    ";": "-.-.-.",   # (NNN) semicolon
    "?": "..--..",   # (IMI) question
    "!": "-.-.--",   #       exclamation
    "-": "-....-",   # (BA)  dash
    "_": "..--.-",   # (UK)  underscore
    "(": "-.--.",    # (KN)  bracket open
    ")": "-.--.-",   # (KK)  bracket close
    "'": ".----.",   # (JN)  single quote
    "\"": ".-..-.",  #       double quote
    "=": "-...-",    # (BT)  equals
    "+": ".-.-.",    # (AR)  plus
    "/": "-..-.",    # (DN)  slash
    "@": ".--.-.",   # (AC)  at
    # Signals
    "<KA>": "-.-.-",  # Spruchnfang
    "<BT>": "-...-",  # Pause
    "<AR>": ".-.-.",  # Spruchende
    "<VE>": "...-.",  # verstanden
    "<SK>": "...-.-", # Verkehrsende
    "<SOS>": "...---...", # internationater (See-)Notruf
    "<HH>": "........"    # Fehler, Wiederholung ab letztem vollständigen Wort"
}
 
morse_inv = dict((v,k) for (k,v) in morse.items())

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block CW Decoder"""

    def handler_msg(self, msg):
        event = pmt.to_long(msg);
        distance = (event>>1)-(self.previous>>1)
        if (event & 1) == 0:		# State changed to zero, we got lenght of on
            self.onvector[self.eventcount_on % self.learning_vector] = [distance]
            self.eventcount_on += 1
            if distance < self.middle:
                self.letter += '.'
            else:
                self.letter += '-'
        else:
            self.offvector[self.eventcount_off % self.learning_vector] = [distance]
            self.eventcount_off += 1
            if distance > self.middle_space_letter:
                decoded_letter = morse_inv.get(self.letter, '<?>')
                print(decoded_letter, self.letter)
                self.word += decoded_letter
                self.letter = ''
            if distance > self.middle_space_word:
                print('Word: ' + self.word)
                self.word = ''
        if (self.eventcount+1) % 20 == 0:
            #print(self.onvector)
            self.kmeans_dd.fit(self.onvector)
            y_kmeans = self.kmeans_dd.predict(self.onvector)
            centers = self.kmeans_dd.cluster_centers_
            dot, dash = (centers[0][0], centers[1][0]) if centers[0][0] < centers[1][0] else (centers[1][0], centers[0][0])
            self.middle = (dot+dash)/2
            diff = dash-dot
            self.low = dot-diff
            self.high = dash+diff
            print('low: {:f} dot: {:f} middle: {:f} dash: {:f} high: {:f}'.format(self.low, dot, self.middle, dash, self.high))
            #print(self.offvector)
            self.kmeans_space.fit(self.offvector)
            y_kmeans = self.kmeans_space.predict(self.offvector)
            centers = self.kmeans_space.cluster_centers_
            spaces = []
            for i in centers:
                spaces.append(i[0])
            sorted_spaces = sorted(spaces)
            print('spaces: ', sorted_spaces)
            self.middle_space_letter = (sorted_spaces[0]+sorted_spaces[1]) / 2
            self.middle_space_word = (sorted_spaces[1]+sorted_spaces[2]) / 2
        self.previous = event
        self.eventcount += 1

    def __init__(self, learning_vector=1000, initial_dit_length_samples=50):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Signal cluster analysis',   # will show up in GRC
            in_sig=[np.float32],
            out_sig=[np.complex64]
        )
        self.message_port_register_in(pmt.intern("cwevent"))
        self.set_msg_handler(pmt.intern("cwevent"), self.handler_msg)

        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.learning_vector = learning_vector
        self.eventcount = 0
        self.eventcount_on = 0
        self.eventcount_off = 0
        self.previous = 0
        self.kmeans_dd = KMeans(n_clusters=2)  # dash or dot
        self.kmeans_space = KMeans(n_clusters=3)  # letter space, word space, transmission space
        self.letter = ''
        self.word = ''
        self.middle = 0
        self.middle_space_letter = 0
        self.middle_space_word = 0
        if False:
            self.onvector = [[0]]*self.learning_vector
            self.offvector = [[0]]*self.learning_vector
        else:
            self.onvector = []
            self.offvector = []
            for i in range(0, self.learning_vector):
                if i % 1 == 0:
                    # initial length of dot
                    self.onvector.append([initial_dit_length_samples])
                else:
                    # initial lenghth of dash
                    self.onvector.append([initial_dit_length_samples*2])
                if i % 3 == 0:
                    # initial length of signal spacing
                    self.offvector.append([initial_dit_length_samples])
                elif i % 3 == 1:
                    # initial length of letter spacing
                    self.offvector.append([initial_dit_length_samples*3])
                else:
                    # initial length of word spacing
                    self.offvector.append([initial_dit_length_samples*7])
                
                

        

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        #output_items[0][:] = input_items[0] * self.example_param
        return len(output_items[0])
