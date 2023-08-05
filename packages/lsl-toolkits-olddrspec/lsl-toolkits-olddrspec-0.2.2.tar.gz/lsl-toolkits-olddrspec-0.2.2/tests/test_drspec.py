# -*- coding: utf-8 -*-

import os
import unittest

from lsl_toolkits import OldDRSpec as drspec
from lsl.reader import errors

__revision__ = "$ Revision: 2 $"
__version__  = "0.1"
__author__    = "Jayce Dowell"

drspecFile = os.path.join(os.path.dirname(__file__), 'data', 'drspec-test.dat')


class drspec_tests(unittest.TestCase):
    """A unittest.TestCase collection of unit tests for the lsl_toolkits.OldDRSpec
    module."""

    def test_drspec_read(self):
        """Test reading in a frame from a DR spectrometer file."""

        fh = open(drspecFile, 'rb')
        # First frame is really DR spectrometer and stores the IDs
        frame1 = drspec.readFrame(fh)
        beam = frame1.parseID()
        self.assertEqual(beam, 3)

        # Second frame
        frame2 = drspec.readFrame(fh)
        beam = frame2.parseID()
        self.assertEqual(beam, 3)
        fh.close()

    def test_drspec_errors(self):
        """Test reading in all frames from a truncated DR spectrometer file."""

        fh = open(drspecFile, 'rb')
        # Frames 1 through 8
        for i in range(1,8):
            frame = drspec.readFrame(fh)

        # Last frame should be an error (errors.eofError)
        self.assertRaises(errors.eofError, drspec.readFrame, fh)
        fh.close()
        
        # If we offset in the file by 1 byte, we should be a 
        # sync error (errors.syncError).
        fh = open(drspecFile, 'rb')
        fh.seek(1)
        self.assertRaises(errors.syncError, drspec.readFrame, fh)
        fh.close()
        
    def test_drspec_metadata(self):
        """Test finding out the DR spectrometer metadata."""
        
        fh = open(drspecFile, 'rb')
        cFrame = drspec.readFrame(fh)
        fh.seek(0)
        
        # Beam
        self.assertEqual(cFrame.parseID(), 3)
        
        # Sample rate
        self.assertAlmostEqual(cFrame.getSampleRate(), 19.6e6, 1)
        self.assertAlmostEqual(cFrame.getSampleRate(), drspec.getSampleRate(fh), 1)
        
        # Filter code
        self.assertEqual(cFrame.getFilterCode(), 7)
        self.assertEqual(cFrame.getFilterCode(), drspec.getSampleRate(fh, FilterCode=True))
        
        # FFTs per integration
        self.assertEqual(cFrame.getFFTsPerIntegration(), 6144)
        self.assertEqual(cFrame.getFFTsPerIntegration(), drspec.getFFTsPerIntegration(fh))
        
        # Transform size
        self.assertEqual(cFrame.getTransformSize(), 32)
        self.assertEqual(cFrame.getTransformSize(), drspec.getTransformSize(fh))
        
        # Integration time
        self.assertAlmostEqual(cFrame.getIntegrationTime(), 0.01003102, 8)
        self.assertAlmostEqual(cFrame.getIntegrationTime(), drspec.getIntegrationTime(fh))
        
        fh.close()

    def test_drspec_comps(self):
        """Test the DR spectrometer frame comparison operators (>, <, etc.) for time tags."""

        fh = open(drspecFile, 'rb')
        # Frames 1 through 7
        frames = []
        for i in range(1,8):
            frames.append(drspec.readFrame(fh))
        fh.close()

        self.assertTrue(0 < frames[0])
        self.assertFalse(0 > frames[0])
        self.assertTrue(frames[-1] >= frames[0])
        self.assertFalse(frames[-1] <= frames[0])
        self.assertTrue(frames[0] == frames[0])
        self.assertFalse(frames[0] == frames[-1])
        self.assertFalse(frames[0] != frames[0])
        
    def test_drspec_sort(self):
        """Test sorting DR spectrometer frames by time tags."""
        
        fh = open(drspecFile, 'rb')
        # Frames 1 through 7
        frames = []
        for i in range(1,8):
            frames.append(drspec.readFrame(fh))
        
        frames.sort()
        frames = frames[::-1]
        
        for i in xrange(1,len(frames)):
            self.assertTrue( frames[i-1] >= frames[i] )
        fh.close()

    def test_drspec_math(self):
        """Test mathematical operations on DR spectrometer frame data via frames."""

        fh = open(drspecFile, 'rb')
        # Frames 1 through 7
        frames = []
        for i in range(1,8):
            frames.append(drspec.readFrame(fh))
        fh.close()

        nPts = frames[0].data.X0.size

        # Multiplication
        frameT = frames[0] * 2.0
        for i in xrange(nPts):
            self.assertAlmostEqual(frameT.data.X0[i], 2*frames[0].data.X0[i], 6)
        frameT *= 2.0
        for i in xrange(nPts):
            self.assertAlmostEqual(frameT.data.X1[i], 4*frames[0].data.X1[i], 6)
        frameT = frames[0] * frames[1]
        for i in xrange(nPts):
            self.assertAlmostEqual(frameT.data.Y0[i], frames[0].data.Y0[i]*frames[1].data.Y0[i], 6)
        
        # Addition
        frameA = frames[0] + 2.0
        for i in xrange(nPts):
            self.assertAlmostEqual(frameA.data.X0[i], 2+frames[0].data.X0[i], 6)
        frameA += 2.0
        for i in xrange(nPts):
            self.assertAlmostEqual(frameA.data.X1[i], 4+frames[0].data.X1[i], 6)
        frameA = frames[0] + frames[1]
        for i in xrange(nPts):
            self.assertAlmostEqual(frameA.data.Y0[i], frames[0].data.Y0[i]+frames[1].data.Y0[i], 6)

class drspec_test_suite(unittest.TestSuite):
    """A unittest.TestSuite class which contains all of the lsl_toolkits.OldDRSpec 
reader units tests."""
    
    def __init__(self):
        unittest.TestSuite.__init__(self)
        
        loader = unittest.TestLoader()
        self.addTests(loader.loadTestsFromTestCase(drspec_tests)) 


if __name__ == '__main__':
    unittest.main()
