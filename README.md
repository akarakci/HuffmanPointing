# HuffmanPointing

Huffman coding of a pixellized pointing matrix (in ascii).

Usage :

        h = Huffman("pointing.dat", nside)
        
        pixarr = h.PixellizePointing([write=True])  ##retruns pixellized pointing int array
        
        b = h.GenerateCode(pixarr[, write=True])    ##returns encoded byte array (or tuple (bytarr, outfile) if write=True)
        
        decarr = h.Decoder(b[, write=True])         ##returns decoded int array
        
