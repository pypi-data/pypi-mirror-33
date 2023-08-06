# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

import logging
import time
import unittest

import numpy
from PyMca5 import spslut

from silx.image.colormap import dataToRGBAColormap

_logger = logging.getLogger(__name__)

# TODOs:
# what to do with max < min: as SPS LUT or also invert outside boundaries?
# test usedMin and usedMax
# benchmark


# common ######################################################################

class _TestColormap(unittest.TestCase):
    # Array data types to test
    FLOATING_DTYPES = numpy.float16, numpy.float32, numpy.float64
    SIGNED_DTYPES = FLOATING_DTYPES + (numpy.int8, numpy.int16,
                                       numpy.int32, numpy.int64)
    UNSIGNED_DTYPES = numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64
    DTYPES = SIGNED_DTYPES + UNSIGNED_DTYPES

    # Array sizes to test
    SIZES = 2, 10, 256, 1024  # , 2048, 4096

    # Colormaps definitions
    _LUT_RED_256 = numpy.zeros((256, 4), dtype=numpy.uint8)
    _LUT_RED_256[:, 0] = numpy.arange(256, dtype=numpy.uint8)
    _LUT_RED_256[:, 3] = 255

    _LUT_RGB_3 = numpy.array(((255, 0, 0, 255),
                              (0, 255, 0, 255),
                              (0, 0, 255, 255)), dtype=numpy.uint8)

    _LUT_RGB_768 = numpy.zeros((768, 4), dtype=numpy.uint8)
    _LUT_RGB_768[0:256, 0] = numpy.arange(256, dtype=numpy.uint8)
    _LUT_RGB_768[256:512, 1] = numpy.arange(256, dtype=numpy.uint8)
    _LUT_RGB_768[512:768, 1] = numpy.arange(256, dtype=numpy.uint8)
    _LUT_RGB_768[:, 3] = 255

    COLORMAPS = {
        'red 256': _LUT_RED_256,
        'rgb 3': _LUT_RGB_3,
        'rgb 768': _LUT_RGB_768,
    }

    @staticmethod
    def _log(*args):
        """Logging used by test for debugging."""
        _logger.debug(str(args))

    @staticmethod
    def buildControlPixmap(data, colormap, start=None, end=None,
                           isLog10=False):
        """Generate a pixmap used to test C pixmap."""
        if isLog10:  # Convert to log
            if start is None:
                posValue = data[numpy.nonzero(data > 0)]
                if posValue.size != 0:
                    start = numpy.nanmin(posValue)
                else:
                    start = 0.

            if end is None:
                end = numpy.nanmax(data)

            start = 0. if start <= 0. else numpy.log10(start,
                                                       dtype=numpy.float64)
            end = 0. if end <= 0. else numpy.log10(end,
                                                   dtype=numpy.float64)

            data = numpy.log10(data, dtype=numpy.float64)
        else:
            if start is None:
                start = numpy.nanmin(data)
            if end is None:
                end = numpy.nanmax(data)

        start, end = float(start), float(end)
        min_, max_ = min(start, end), max(start, end)

        if start == end:
            indices = numpy.asarray((len(colormap) - 1) * (data >= max_),
                                    dtype=numpy.int)
        else:
            clipData = numpy.clip(data, min_, max_)  # Clip first avoid overflow
            scale = len(colormap) / (end - start)
            normData = scale * (numpy.asarray(clipData, numpy.float64) - start)

            # Clip again to makes sure <= len(colormap) - 1
            indices = numpy.asarray(numpy.clip(normData,
                                               0, len(colormap) - 1),
                                    dtype=numpy.uint32)

        pixmap = numpy.take(colormap, indices, axis=0)
        pixmap.shape = data.shape + (4,)
        return numpy.ascontiguousarray(pixmap)

    @staticmethod
    def buildSPSLUTRedPixmap(data, start=None, end=None, isLog10=False):
        """Generate a pixmap with SPS LUT.
        Only supports red colormap with 256 colors.
        """
        colormap = spslut.RED
        mapping = spslut.LOG if isLog10 else spslut.LINEAR

        if start is None and end is None:
            autoScale = 1
            start, end = 0, 1
        else:
            autoScale = 0
            if start is None:
                start = data.min()
            if end is None:
                end = data.max()

        pixmap, size, minMax = spslut.transform(data,
                                                (1, 0),
                                                (mapping, 3.0),
                                                'RGBX',
                                                colormap,
                                                autoScale,
                                                (start, end),
                                                (0, 255),
                                                1)
        pixmap.shape = data.shape[0], data.shape[1], 4

        return pixmap

    def _testColormap(self, data, colormap, start, end, control=None,
                      isLog10=False, nanColor=None):
        """Test pixmap built with C code against SPS LUT if possible,
        else against Python control code."""
        startTime = time.time()
        pixmap = dataToRGBAColormap(data,
                                    colormap,
                                    start,
                                    end,
                                    isLog10,
                                    nanColor)
        duration = time.time() - startTime

        # Compare with result
        controlType = 'array'
        if control is None:
            startTime = time.time()

            # Compare with SPS LUT if possible
            if (colormap.shape == self.COLORMAPS['red 256'].shape and
                    numpy.all(numpy.equal(colormap, self.COLORMAPS['red 256'])) and
                    data.size % 2 == 0 and
                    data.dtype in (numpy.float32, numpy.float64)):
                # Only works with red colormap and even size
                # as it needs 2D data
                if len(data.shape) == 1:
                    data.shape = data.size // 2, -1
                    pixmap.shape = data.shape + (4,)
                control = self.buildSPSLUTRedPixmap(data, start, end, isLog10)
                controlType = 'SPS LUT'

            # Compare with python test implementation
            else:
                control = self.buildControlPixmap(data, colormap, start, end,
                                                  isLog10)
                controlType = 'Python control code'

            controlDuration = time.time() - startTime
            if duration >= controlDuration:
                self._log('duration', duration, 'control', controlDuration)
            # Allows duration to be 20% over SPS LUT duration
            # self.assertTrue(duration < 1.2 * controlDuration)

        difference = numpy.fabs(numpy.asarray(pixmap, dtype=numpy.float64) -
                                numpy.asarray(control, dtype=numpy.float64))
        if numpy.any(difference != 0.0):
            self._log('control', controlType)
            self._log('data', data)
            self._log('pixmap', pixmap)
            self._log('control', control)
            self._log('errors', numpy.ravel(difference))
            self._log('errors', difference[difference != 0])
            self._log('in pixmap', pixmap[difference != 0])
            self._log('in control', control[difference != 0])
            self._log('Max error', difference.max())

        # Allows a difference of 1 per channel
        self.assertTrue(numpy.all(difference <= 1.0))

        return duration


# TestColormap ################################################################

class TestColormap(_TestColormap):
    """Test common limit case for colormap in C with both linear and log mode.

    Test with different: data types, sizes, colormaps (with different sizes),
    mapping range.
    """

    def testNoData(self):
        """Test pixmap generation with empty data."""
        self._log("TestColormap.testNoData")
        cmapName = 'red 256'
        colormap = self.COLORMAPS[cmapName]

        for dtype in self.DTYPES:
            for isLog10 in (False, True):
                data = numpy.array((), dtype=dtype)
                result = numpy.array((), dtype=numpy.uint8)
                result.shape = 0, 4
                duration = self._testColormap(data, colormap,
                                              None, None, result, isLog10)
                self._log('No data', 'red 256', dtype, len(data), (None, None),
                          'isLog10:', isLog10, duration)

    def testNaN(self):
        """Test pixmap generation with NaN values and no NaN color."""
        self._log("TestColormap.testNaN")
        cmapName = 'red 256'
        colormap = self.COLORMAPS[cmapName]

        for dtype in self.FLOATING_DTYPES:
            for isLog10 in (False, True):
                # All NaNs
                data = numpy.array((float('nan'),) * 4, dtype=dtype)
                result = numpy.array(((0, 0, 0, 255),
                                      (0, 0, 0, 255),
                                      (0, 0, 0, 255),
                                      (0, 0, 0, 255)), dtype=numpy.uint8)
                duration = self._testColormap(data, colormap,
                                              None, None, result, isLog10)
                self._log('All NaNs', 'red 256', dtype, len(data),
                          (None, None), 'isLog10:', isLog10, duration)

                # Some NaNs
                data = numpy.array((1., float('nan'), 0., float('nan')),
                                   dtype=dtype)
                result = numpy.array(((255, 0, 0, 255),
                                      (0, 0, 0, 255),
                                      (0, 0, 0, 255),
                                      (0, 0, 0, 255)), dtype=numpy.uint8)
                duration = self._testColormap(data, colormap,
                                              None, None, result, isLog10)
                self._log('Some NaNs', 'red 256', dtype, len(data),
                          (None, None), 'isLog10:', isLog10, duration)

    def testNaNWithColor(self):
        """Test pixmap generation with NaN values with a NaN color."""
        self._log("TestColormap.testNaNWithColor")
        cmapName = 'red 256'
        colormap = self.COLORMAPS[cmapName]

        for dtype in self.FLOATING_DTYPES:
            for isLog10 in (False, True):
                # All NaNs
                data = numpy.array((float('nan'),) * 4, dtype=dtype)
                result = numpy.array(((128, 128, 128, 255),
                                      (128, 128, 128, 255),
                                      (128, 128, 128, 255),
                                      (128, 128, 128, 255)), dtype=numpy.uint8)
                duration = self._testColormap(data, colormap,
                                              None, None, result, isLog10,
                                              nanColor=(128, 128, 128, 255))
                self._log('All NaNs', 'red 256', dtype, len(data),
                          (None, None), 'isLog10:', isLog10, duration)

                # Some NaNs
                data = numpy.array((1., float('nan'), 0., float('nan')),
                                   dtype=dtype)
                result = numpy.array(((255, 0, 0, 255),
                                      (128, 128, 128, 255),
                                      (0, 0, 0, 255),
                                      (128, 128, 128, 255)), dtype=numpy.uint8)
                duration = self._testColormap(data, colormap,
                                              None, None, result, isLog10,
                                              nanColor=(128, 128, 128, 255))
                self._log('Some NaNs', 'red 256', dtype, len(data),
                          (None, None), 'isLog10:', isLog10, duration)


# TestLinearColormap ##########################################################

class TestLinearColormap(_TestColormap):
    """Test fill pixmap with colormap in C with linear mode.

    Test with different: data types, sizes, colormaps (with different sizes),
    mapping range.
    """

    # Colormap ranges to map
    RANGES = (None, None), (1, 10)

    def test1DData(self):
        """Test pixmap generation for 1D data of different size and types."""
        self._log("TestLinearColormap.test1DData")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.DTYPES:
                    for start, end in self.RANGES:
                        # Increasing values
                        data = numpy.arange(size, dtype=dtype)
                        duration = self._testColormap(data, colormap,
                                                      start, end)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

                        # Reverse order
                        data = data[::-1]
                        duration = self._testColormap(data, colormap,
                                                      start, end)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

    def test2DData(self):
        """Test pixmap generation for 2D data of different size and types."""
        self._log("TestLinearColormap.test2DData")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.DTYPES:
                    for start, end in self.RANGES:
                        # Increasing values
                        data = numpy.arange(size * size, dtype=dtype)
                        data = numpy.nan_to_num(data)
                        data.shape = size, size
                        duration = self._testColormap(data, colormap,
                                                      start, end)

                        self._log('2D', cmapName, dtype, size, (start, end),
                                  duration)

                        # Reverse order
                        data = data[::-1, ::-1]
                        duration = self._testColormap(data, colormap,
                                                      start, end)

                        self._log('2D', cmapName, dtype, size, (start, end),
                                  duration)

    def testInf(self):
        """Test pixmap generation with Inf values."""
        self._log("TestLinearColormap.testInf")

        for dtype in self.FLOATING_DTYPES:
            # All positive Inf
            data = numpy.array((float('inf'),) * 4, dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (255, 0, 0, 255),
                                  (255, 0, 0, 255),
                                  (255, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result)
            self._log('All +Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

            # All negative Inf
            data = numpy.array((float('-inf'),) * 4, dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (255, 0, 0, 255),
                                  (255, 0, 0, 255),
                                  (255, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result)
            self._log('All -Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

            # All +/-Inf
            data = numpy.array((float('inf'), float('-inf'),
                                float('-inf'), float('inf')), dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (255, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result)
            self._log('All +/-Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

            # Some +/-Inf
            data = numpy.array((float('inf'), 0., float('-inf'), -10.),
                               dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None,
                                          result)  # Seg Fault with SPS
            self._log('Some +/-Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

    @unittest.skip("Not for reproductible tests")
    def test1DDataRandom(self):
        """Test pixmap generation for 1D data of different size and types."""
        self._log("TestLinearColormap.test1DDataRandom")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.DTYPES:
                    for start, end in self.RANGES:
                        try:
                            dtypeMax = numpy.iinfo(dtype).max
                        except ValueError:
                            dtypeMax = numpy.finfo(dtype).max
                        data = numpy.asarray(numpy.random.rand(size) * dtypeMax,
                                             dtype=dtype)
                        duration = self._testColormap(data, colormap,
                                                      start, end)

                        self._log('1D Random', cmapName, dtype, size,
                                  (start, end), duration)


# TestLog10Colormap ###########################################################

class TestLog10Colormap(_TestColormap):
    """Test fill pixmap with colormap in C with log mode.

    Test with different: data types, sizes, colormaps (with different sizes),
    mapping range.
    """
    # Colormap ranges to map
    RANGES = (None, None), (1, 10)  # , (10, 1)

    def test1DDataAllPositive(self):
        """Test pixmap generation for all positive 1D data."""
        self._log("TestLog10Colormap.test1DDataAllPositive")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.DTYPES:
                    for start, end in self.RANGES:
                        # Increasing values
                        data = numpy.arange(size, dtype=dtype) + 1
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

                        # Reverse order
                        data = data[::-1]
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

    def test2DDataAllPositive(self):
        """Test pixmap generation for all positive 2D data."""
        self._log("TestLog10Colormap.test2DDataAllPositive")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.DTYPES:
                    for start, end in self.RANGES:
                        # Increasing values
                        data = numpy.arange(size * size, dtype=dtype) + 1
                        data = numpy.nan_to_num(data)
                        data.shape = size, size
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('2D', cmapName, dtype, size, (start, end),
                                  duration)

                        # Reverse order
                        data = data[::-1, ::-1]
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('2D', cmapName, dtype, size, (start, end),
                                  duration)

    def testAllNegative(self):
        """Test pixmap generation for all negative 1D data."""
        self._log("TestLog10Colormap.testAllNegative")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.SIGNED_DTYPES:
                    for start, end in self.RANGES:
                        # Increasing values
                        data = numpy.arange(-size, 0, dtype=dtype)
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

                        # Reverse order
                        data = data[::-1]
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

    def testCrossingZero(self):
        """Test pixmap generation for 1D data with negative and zero."""
        self._log("TestLog10Colormap.testCrossingZero")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.SIGNED_DTYPES:
                    for start, end in self.RANGES:
                        # Increasing values
                        data = numpy.arange(-size/2, size/2 + 1, dtype=dtype)
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

                        # Reverse order
                        data = data[::-1]
                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D', cmapName, dtype, size, (start, end),
                                  duration)

    @unittest.skip("Not for reproductible tests")
    def test1DDataRandom(self):
        """Test pixmap generation for 1D data of different size and types."""
        self._log("TestLog10Colormap.test1DDataRandom")
        for cmapName, colormap in self.COLORMAPS.items():
            for size in self.SIZES:
                for dtype in self.DTYPES:
                    for start, end in self.RANGES:
                        try:
                            dtypeMax = numpy.iinfo(dtype).max
                            dtypeMin = numpy.iinfo(dtype).min
                        except ValueError:
                            dtypeMax = numpy.finfo(dtype).max
                            dtypeMin = numpy.finfo(dtype).min
                        if dtypeMin < 0:
                            data = numpy.asarray(-dtypeMax/2. +
                                                 numpy.random.rand(size) * dtypeMax,
                                                 dtype=dtype)
                        else:
                            data = numpy.asarray(numpy.random.rand(size) * dtypeMax,
                                                 dtype=dtype)

                        duration = self._testColormap(data, colormap,
                                                      start, end,
                                                      isLog10=True)

                        self._log('1D Random', cmapName, dtype, size,
                                  (start, end), duration)

    def testInf(self):
        """Test pixmap generation with Inf values."""
        self._log("TestLog10Colormap.testInf")

        for dtype in self.FLOATING_DTYPES:
            # All positive Inf
            data = numpy.array((float('inf'),) * 4, dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (255, 0, 0, 255),
                                  (255, 0, 0, 255),
                                  (255, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result, isLog10=True)
            self._log('All +Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

            # All negative Inf
            data = numpy.array((float('-inf'),) * 4, dtype=dtype)
            result = numpy.array(((0, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result, isLog10=True)
            self._log('All -Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

            # All +/-Inf
            data = numpy.array((float('inf'), float('-inf'),
                                float('-inf'), float('inf')), dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (255, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result, isLog10=True)
            self._log('All +/-Inf', 'red 256', dtype, len(data), (None, None),
                      duration)

            # Some +/-Inf
            data = numpy.array((float('inf'), 0., float('-inf'), -10.),
                               dtype=dtype)
            result = numpy.array(((255, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255),
                                  (0, 0, 0, 255)), dtype=numpy.uint8)
            duration = self._testColormap(data, self.COLORMAPS['red 256'],
                                          None, None, result, isLog10=True)
            self._log('Some +/-Inf', 'red 256', dtype, len(data), (None, None),
                      duration)


def suite():
    testSuite = unittest.TestSuite()
    for testClass in (TestColormap, TestLinearColormap):  # , TestLog10Colormap):
        testSuite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(testClass))
    return testSuite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
