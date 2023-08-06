# TODO quick & dirty proof of concept

import numpy

from silx.gui.plot.tools.profile.ScatterProfileToolBar import _BaseProfileToolBar
from .. import items
from ...colors import cursorColorForColormap
from ....image.bilinear import BilinearImage


def _alignedPartialProfile(data, rowRange, colRange, axis):
    """Mean of a rectangular region (ROI) of a stack of images
    along a given axis.

    Returned values and all parameters are in image coordinates.

    :param numpy.ndarray data: 3D volume (stack of 2D images)
        The first dimension is the image index.
    :param rowRange: [min, max[ of ROI rows (upper bound excluded).
    :type rowRange: 2-tuple of int (min, max) with min < max
    :param colRange: [min, max[ of ROI columns (upper bound excluded).
    :type colRange: 2-tuple of int (min, max) with min < max
    :param int axis: The axis along which to take the profile of the ROI.
                     0: Sum rows along columns.
                     1: Sum columns along rows.
    :return: Profile image along the ROI as the mean of the intersection
             of the ROI and the image.
    """
    assert axis in (0, 1)
    assert len(data.shape) == 3
    assert rowRange[0] < rowRange[1]
    assert colRange[0] < colRange[1]

    nimages, height, width = data.shape

    # Range aligned with the integration direction
    profileRange = colRange if axis == 0 else rowRange

    profileLength = abs(profileRange[1] - profileRange[0])

    # Subset of the image to use as intersection of ROI and image
    rowStart = min(max(0, rowRange[0]), height)
    rowEnd = min(max(0, rowRange[1]), height)
    colStart = min(max(0, colRange[0]), width)
    colEnd = min(max(0, colRange[1]), width)

    imgProfile = numpy.mean(data[:, rowStart:rowEnd, colStart:colEnd],
                            axis=axis + 1, dtype=numpy.float32)

    # Profile including out of bound area
    profile = numpy.zeros((nimages, profileLength), dtype=numpy.float32)

    # Place imgProfile in full profile
    offset = - min(0, profileRange[0])
    profile[:, offset:offset + imgProfile.shape[1]] = imgProfile

    return profile


def createProfile(points, data, origin, scale, lineWidth):
    """Create the profile line for the the given image.

    :param points: Coords of profile end points: (x0, y0, x1, y1)
    :param numpy.ndarray data: the 2D image or the 3D stack of images
        on which we compute the profile.
    :param origin: (ox, oy) the offset from origin
    :type origin: 2-tuple of float
    :param scale: (sx, sy) the scale to use
    :type scale: 2-tuple of float
    :param int lineWidth: width of the profile line
    :return: `profile, area`, where:
        - profile is a 2D array of the profiles of the stack of images.
          For a single image, the profile is a curve, so this parameter
          has a shape *(1, len(curve))*
        - area is a tuple of two 1D arrays with 4 values each. They represent
          the effective ROI area corners in plot coords.

    :rtype: tuple(ndarray, (ndarray, ndarray), str, str)
    """
    if data is None or points is None or lineWidth is None:
        raise ValueError("createProfile called with invalid arguments")

    # force 3D data (stack of images)
    if len(data.shape) == 2:
        data3D = data.reshape((1,) + data.shape)
    elif len(data.shape) == 3:
        data3D = data

    roiWidth = max(1, lineWidth)
    x0, y0, x1, y1 = points

    # Convert start and end points in image coords as (row, col)
    startPt = ((y0 - origin[1]) / scale[1],
               (x0 - origin[0]) / scale[0])
    endPt = ((y1 - origin[1]) / scale[1],
             (x1 - origin[0]) / scale[0])

    if (int(startPt[0]) == int(endPt[0]) or
            int(startPt[1]) == int(endPt[1])):
        # Profile is aligned with one of the axes

        # Convert to int
        startPt = int(startPt[0]), int(startPt[1])
        endPt = int(endPt[0]), int(endPt[1])

        # Ensure startPt <= endPt
        if startPt[0] > endPt[0] or startPt[1] > endPt[1]:
            startPt, endPt = endPt, startPt

        if startPt[0] == endPt[0]:  # Row aligned
            rowRange = (int(startPt[0] + 0.5 - 0.5 * roiWidth),
                        int(startPt[0] + 0.5 + 0.5 * roiWidth))
            colRange = startPt[1], endPt[1] + 1
            profile = _alignedPartialProfile(data3D,
                                             rowRange, colRange,
                                             axis=0)

        else:  # Column aligned
            rowRange = startPt[0], endPt[0] + 1
            colRange = (int(startPt[1] + 0.5 - 0.5 * roiWidth),
                        int(startPt[1] + 0.5 + 0.5 * roiWidth))
            profile = _alignedPartialProfile(data3D,
                                             rowRange, colRange,
                                             axis=1)

        # Convert ranges to plot coords to draw ROI area
        area = (
            numpy.array(
                (colRange[0], colRange[1], colRange[1], colRange[0]),
                dtype=numpy.float32) * scale[0] + origin[0],
            numpy.array(
                (rowRange[0], rowRange[0], rowRange[1], rowRange[1]),
                dtype=numpy.float32) * scale[1] + origin[1])

    else:  # General case: use bilinear interpolation

        # Ensure startPt <= endPt
        if (startPt[1] > endPt[1] or (
                startPt[1] == endPt[1] and startPt[0] > endPt[0])):
            startPt, endPt = endPt, startPt

        profile = []
        for slice_idx in range(data3D.shape[0]):
            bilinear = BilinearImage(data3D[slice_idx, :, :])

            profile.append(bilinear.profile_line(
                (startPt[0] - 0.5, startPt[1] - 0.5),
                (endPt[0] - 0.5, endPt[1] - 0.5),
                roiWidth))
        profile = numpy.array(profile)

        # Extend ROI with half a pixel on each end, and
        # Convert back to plot coords (x, y)
        length = numpy.sqrt((endPt[0] - startPt[0]) ** 2 +
                            (endPt[1] - startPt[1]) ** 2)
        dRow = (endPt[0] - startPt[0]) / length
        dCol = (endPt[1] - startPt[1]) / length

        # Extend ROI with half a pixel on each end
        startPt = startPt[0] - 0.5 * dRow, startPt[1] - 0.5 * dCol
        endPt = endPt[0] + 0.5 * dRow, endPt[1] + 0.5 * dCol

        # Rotate deltas by 90 degrees to apply line width
        dRow, dCol = dCol, -dRow

        area = (
            numpy.array((startPt[1] - 0.5 * roiWidth * dCol,
                         startPt[1] + 0.5 * roiWidth * dCol,
                         endPt[1] + 0.5 * roiWidth * dCol,
                         endPt[1] - 0.5 * roiWidth * dCol),
                        dtype=numpy.float32) * scale[0] + origin[0],
            numpy.array((startPt[0] - 0.5 * roiWidth * dRow,
                         startPt[0] + 0.5 * roiWidth * dRow,
                         endPt[0] + 0.5 * roiWidth * dRow,
                         endPt[0] - 0.5 * roiWidth * dRow),
                        dtype=numpy.float32) * scale[1] + origin[1])

    xProfile = numpy.arange(len(profile[0]), dtype=numpy.float64)

    return (xProfile, profile[0]), area


class ImageProfileToolBar(_BaseProfileToolBar):

    def __init__(self, parent=None, plot=None, title='Image Profile'):
        super(ImageProfileToolBar, self).__init__(parent, plot, title)
        plot.sigActiveImageChanged.connect(self.__activeImageChanged)

        roiManager = self._getRoiManager()
        if roiManager is None:
            _logger.error(
                "Error during scatter profile toolbar initialisation")
        else:
            roiManager.sigInteractiveModeStarted.connect(
                self.__interactionStarted)
            roiManager.sigInteractiveModeFinished.connect(
                self.__interactionFinished)
            if roiManager.isStarted():
                self.__interactionStarted(roiManager.getRegionOfInterestKind())

    def __interactionStarted(self, kind):
        """Handle start of ROI interaction"""
        plot = self.getPlotWidget()
        if plot is None:
            return

        plot.sigActiveImageChanged.connect(self.__activeImageChanged)

        image = plot.getActiveImage()
        legend = None if image is None else image.getLegend()
        self.__activeImageChanged(None, legend)

    def __interactionFinished(self, rois):
        """Handle end of ROI interaction"""
        plot = self.getPlotWidget()
        if plot is None:
            return

        plot.sigActiveImageChanged.disconnect(self.__activeImageChanged)

        image = plot.getActiveImage()
        legend = None if image is None else image.getLegend()
        self.__activeImageChanged(legend, None)

    def __activeImageChanged(self, previous, legend):
        """Handle active image change: toggle enabled toolbar, update curve"""
        plot = self.getPlotWidget()
        if plot is None:
            return

        activeImage = plot.getActiveImage()
        if activeImage is None:
            self.setEnabled(False)
        else:
            # Disable for empty image
            self.setEnabled(activeImage.getData(copy=False).size > 0)

        # Update default profile color
        if isinstance(activeImage, items.ColormapMixIn):
            self.setColor(cursorColorForColormap(
                activeImage.getColormap()['name']))  # TODO change thsi
        else:
            self.setColor('black')

        self.updateProfile()

    def computeProfile(self, x0, y0, x1, y1):
        """Compute corresponding profile

        :param float x0: Profile start point X coord
        :param float y0: Profile start point Y coord
        :param float x1: Profile end point X coord
        :param float y1: Profile end point Y coord
        :return: (x, y) profile data or None
        """
        plot = self.getPlotWidget()
        if plot is None:
            return None

        image = plot.getActiveImage()
        if image is None:
            return None

        profile, area = createProfile(
            points=(x0, y0, x1, y1),
            data=image.getData(copy=False),
            origin=image.getOrigin(),
            scale=image.getScale(),
            lineWidth=1)  # TODO

        return profile