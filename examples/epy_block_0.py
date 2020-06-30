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


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def handler_msg(self, msg):
        event = pmt.to_long(msg);
        distance = (event>>1)-(self.previous>>1)
        if (event & 1) == 0:		# State changed to zero, we got lenght of on
            self.onvector[self.eventcount_on & 1023] = [distance]
            self.eventcount_on += 1
        else:
            self.offvector[self.eventcount_off & 1023] = [distance]
            self.eventcount_off += 1
        if (self.eventcount+1) % 64000 == 0:
            self.kmeans_dd.fit(self.onvector)
            y_kmeans = self.kmeans_dd.predict(self.onvector)
            centers = self.kmeans_dd.cluster_centers_
            dot, dash = (centers[0][0], centers[1][0]) if centers[0][0] < centers[1][0] else (centers[1][0], centers[0][0])
            self.middle = (dot+dash)/2
            diff = dash-dot
            self.low = dot-diff
            self.high = dash+diff
            print('low: {:f} dot: {:f} middle: {:f} dash: {:f} high: {:f}'.format(self.low, dot, self.middle, dash, self.high))
            self.kmeans_space.fit(self.offvector)
            y_kmeans = self.kmeans_space.predict(self.offvector)
            centers = self.kmeans_space.cluster_centers_
            spaces = []
            for i in centers:
                spaces.append(i[0])
            print('spaces: ', sorted(spaces))
        self.previous = event
        self.eventcount += 1

    def __init__(self, example_param=1.0):  # only default arguments here
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
        self.example_param = example_param
        self.eventcount = 0
        self.eventcount_on = 0
        self.eventcount_off = 0
        self.previous = 0
        self.onvector = [None]*1024
        self.offvector = [None]*1024
        self.kmeans_dd = KMeans(n_clusters=2)  # dash or dot
        self.kmeans_space = KMeans(n_clusters=3)  # letter space, word space, transmission space
        

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        #output_items[0][:] = input_items[0] * self.example_param
        return len(output_items[0])
