import healpy as hp
import numpy as np
import heapq
import os


class LeafNode:

    def __init__(self, symbol, weight):
        self.symbol = symbol
        self.weight = weight
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.weight < other.weight


class Huffman:

    def __init__(self, infile, nside=256):
        self.infile = infile
        self.nside = nside
        self.encoding = {}
        self.decoding = {}
        self.queue = []

    def PixellizePointing(self, write=False):
        angs_pol = np.loadtxt(self.infile)
        pixels = hp.ang2pix(self.nside, angs_pol[:,1], angs_pol[:,0])

        if write :
            fname, fext = os.path.splitext(self.infile)
            np.save(fname+"_n"+str(self.nside).zfill(4)+"_pixels.npy", pixels)

        return pixels

    def Weights(self, array):
        weight = {}
        for d in array :
            if not d in weight:
                    weight[d] = 0
            weight[d] += 1
        return weight

    def PrintCode(self, node, code=""):
        if(node.symbol != None):
            self.encoding[node.symbol] = code
            self.decoding[code] = node.symbol
            return

        self.PrintCode(node.left, code + "0")
        self.PrintCode(node.right, code + "1")


    def byteCode(self, array):
        text_bin = "".join(self.encoding[d] for d in array)
        padding = 8 - len(text_bin) % 8
        text_bin += padding*"0"
        text_bin = "{0:08b}".format(padding) + text_bin

        b = bytearray()
        for i in range(0, len(text_bin), 8):
            byte = text_bin[i:i+8]
            b.append(int(byte, 2))
        return b


    def GenerateCode(self, array, write=False):
        delta = np.diff(array)
        delta = np.insert(delta, 0, array[0])

        weight = self.Weights(delta)

        for d in weight:
            node = LeafNode(d, weight[d])
            heapq.heappush(self.queue, node)

        while(len(self.queue)>1):
            left_child = heapq.heappop(self.queue)
            right_child = heapq.heappop(self.queue)

            collapsed = LeafNode(None, left_child.weight + right_child.weight)
            collapsed.left = left_child
            collapsed.right = right_child
            heapq.heappush(self.queue, collapsed)

        node = heapq.heappop(self.queue)
        self.PrintCode(node)

        b = self.byteCode(delta)

        if write :
            fname, fext = os.path.splitext(self.infile)
            np.save(fname+"_n"+str(self.nside).zfill(4)+"_diffpix.npy", delta)
            outfile = fname + "_n"+str(self.nside).zfill(4)+"_diffpix.bin"
            with open(outfile, 'wb') as f_out :
                f_out.write(bytes(b))
            return bytes(b), outfile
        else :
            return bytes(b)

    def Decoder(self, bytarr, write=False):
        binary_txt = ''.join(bin(i)[2:].rjust(8,'0') for i in bytarr)
        padding = int(binary_txt[:8], 2)
        binary_txt = binary_txt[8:-1*padding]

        decoded_arr = []
        code = ""

        for b in binary_txt:
            code += b
            if code in self.decoding:
                d = self.decoding[code]
                decoded_arr.append(d)
                code = ""

        decoded_arr = np.cumsum(decoded_arr)

        if write:
            fname, fext = os.path.splitext(self.infile)
            file_out = fname + "_n"+str(self.nside).zfill(4)+"_decoded_pixels.npy"
            np.save(file_out, decoded_arr)
            return decoded_arr, file_out
        else:
            return decoded_arr


