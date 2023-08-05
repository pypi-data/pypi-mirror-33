# -*- coding: utf-8 -*-

"""Unit test for lsl_toolkit.S60 module"""

import os
import unittest

from lsl_toolkits import S60 as s60
from lsl_toolkits.S60 import sim as sim60
from lsl_toolkits.S60 import errors


__revision__ = "$ Revision: 2 $"
__version__  = "0.2"
__author__    = "Jayce Dowell"


s60File = os.path.join(os.path.dirname(__file__), 'data', 's60-test.dat')


class s60_tests(unittest.TestCase):
    """A unittest.TestCase collection of unit tests for the lsl_toolkits.S60
    module."""

    def test_s60_read(self):
        """Test reading in a frame from a S60 file."""

        fh = open(s60File, 'rb')
        # First frame makes it in with the correct number of elements
        frame1 = s60.readFrame(fh)
        self.assertEqual(frame1.shape[0], 734)

        # Next try a chunk that is equivalent to 3 frames
        chunk1 = s60.readChunk(fh, Chunk=2202)
        self.assertEqual(chunk1.shape[0], 2202)
        fh.close()

    def test_s60_errors(self):
        """Test reading in all frames from a truncated S60 file."""

        fh = open(s60File, 'rb')
        # Frames 1 through 6
        for i in range(1,7):
            frame = s60.readFrame(fh)

        # Last frame should be an error (errors.numpyError)
        self.assertRaises(errors.numpyError, s60.readFrame, fh)
        fh.close()

    def test_s60_bandpass_model(self):
        """Test that the S60 bandpass function runs."""
        
        junk = s60.getBandpassModel()

    def test_frame2frame(self):
        """Test the S60 simulator's frame2frame function."""

        fh = open(s60File, 'rb')
        frame1 = s60.readFrame(fh)
        
        # Convert
        frame2 = sim60.frame2frame(frame1)


class s60_test_suite(unittest.TestSuite):
    """A unittest.TestSuite class which contains all of the lsl_toolkits.S60 units 
    tests."""
    
    def __init__(self):
        unittest.TestSuite.__init__(self)
        
        loader = unittest.TestLoader()
        self.addTests(loader.loadTestsFromTestCase(s60_tests)) 


if __name__ == '__main__':
    unittest.main()
