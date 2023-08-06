#! python
# -*- coding: utf-8 -*-

"""Data manager module, non GUI.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/08/01

"""

import logging

import numpy as np

_logger = logging.getLogger(__name__)


class DataEditor():
    """Class that keep data.

    It is responsible to call update methods from main window.

    Todo:
        We need a better documentation here with examples.

    """

    _observers = []  # List of widgets

    def __init__(self):
        # These values provide different sizes and values to compare indexes
        # Default values for each one
        self.defaultShape = [0, 0, 0]
        self.defaultSize = [0, 0, 0]
        self.defaultElementSize = [0, 0, 0]
        self.defaultValues = [0, 0, 0]   # E.g. t1, t2, rho for a sample

        self.shape = self.defaultShape                 # nx, ny, nz
        self.size = self.defaultSize                   # lx, ly, lz
        self.elementSize = self.defaultElementSize     # dx, dy, dz

        self.minimumValues = [0, 0, 0]   # min_t1, min_t2, min_rho for a sample
        self.maximumValues = [0, 0, 0]   # max_t1, max_t2, max_rho for a sample

        self.valueShape = [3]            # [3]

        self.currentValuesIndex = 0      # Current index being edited, e.g [rho]
        self.currentIndexes = [0, 0, 0]  # Current index for each component, e.g [t1, t2, rho]
        self.currentOpacityIndex = -1    # Index that represents the opacity, others are colors
        self.currentPath = ""

        # Data contains X, Y, Z, VALUES - its size is nx, ny, nz, nv
        self._data = np.full(self.defaultShape + self.valueShape, self.defaultValues)

    @property
    def data(self):
        """np.array: Get data property."""
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.updateObserversData()

    def getDataItem(self, x, y, z, index=None):
        """Get value in data at given index.

        Args:
            x (int): X index of the item.
            y (int): Y index of the item.
            z (int): Z index of the item.
            index (int): Index of the type of data to be returned. If no
                index is selected, it uses the current index.

        Returns:
            float: Data value being data[x, y, z][index].

        """
        cur_index = self.currentValuesIndex

        if index:
            cur_index = index

        return self._data[x, y, z][cur_index]

    def setDataItem(self, x, y, z, value, index=None):
        """Set value in data at given index.

        Parameters:
            x (int): X index of the item.
            y (int): Y index of the item.
            z (int): Z index of the item.
            index (int): Index of the type of data to be returned. If no
                index is selected, it uses the current index.

        """
        cur_index = self.currentValuesIndex

        if index:
            cur_index = index

        min_value = self.minimumValues[cur_index]
        max_value = self.maximumValues[cur_index]
        def_value = self.defaultValues[cur_index]

        new_value = def_value

        # Check value limits
        if value >= min_value and value <= max_value:
            new_value = value
        elif value < min_value:
            new_value = min_value
        elif value > max_value:
            new_value = max_value

        _logger.debug("X Y Z: %s, Value: %s, Index: %s", (x, y, z), new_value, cur_index)

        self._data[x, y, z][cur_index] = new_value

    def setValues(self, minimum_values, default_values, maximum_values):
        """Set the minimun, maximum and default values.

        Args:
            minimum_values (list(float)): List of minimum of each type of data.
            default_values  (list(float)): List of default of each type of data.
            maximum_values (list(float)): List of maximum of each type of data.

        """
        self.minimumValues = minimum_values
        self.defaultValues = default_values
        self.maximumValues = maximum_values

    def setDimension(self, size, shape):
        """Set value on the data dimension.

        Args:
            size (list): New values of nx, ny and nz.
            shape (list): New values of sizeX, sizeY and sizeZ.

        """
        _logger.debug("Old shape: %s, New shape: %s Old size: %s, New size: %s",
                      self.shape, shape, self.size, size)
        self.shape = shape
        self.size = size
        self.elementSize = [size[i] / shape[i] for i in range(3)]
        self.resizeData()

    def setNX(self, value):
        """Set value on Nx.

        Args:
            value (int): New value of nx.

        """
        _logger.debug("Old NX: %s, New NX: %s ", self.shape[0], value)
        self.shape[0] = value
        self.elementSize[0] = self.size[0] / self.shape[0]
        self.resizeData()

    def setNY(self, value):
        """Set value on Ny.

        Args:
            value (int): New value of ny.

        """
        _logger.debug("Old NY: %s, New NY: %s ", self.shape[1], value)
        self.shape[1] = value
        self.elementSize[1] = self.size[1] / self.shape[1]
        self.resizeData()

    def setNZ(self, value):
        """Set value on Nz.

        Args:
            value (int): New value of nz.

        """
        _logger.debug("Old NZ: %s, New NZ: %s ", self.shape[2], value)
        self.shape[2] = value
        self.elementSize[2] = self.size[2] / self.shape[2]
        self.resizeData()

    def setSizeX(self, value):
        """Set value on SizeX - 0.

        Args:
            value (float): New value of SizeX.

        """
        _logger.debug("Old SizeX: %s, New SizeX: %s ", self.size[0], value)
        self.size[0] = value
        self.elementSize[0] = self.size[0] / self.shape[0]
        self.updateObserversDataSize()

    def setSizeY(self, value):
        """Set value on SizeY - 1.

        Args:
            value (float): New value of SizeY.

        """
        _logger.debug("Old SizeY: %s, New SizeY: %s ", self.size[1], value)
        self.size[1] = value
        self.elementSize[1] = self.size[1] / self.shape[1]
        self.updateObserversDataSize()

    def setSizeZ(self, value):
        """Set value on SizeZ - 2.

        Args:
            value (float): New value of SizeZ.

        """
        _logger.debug("Old SizeZ: %s, New SizeZ: %s ", self.size[2], value)
        self.size[2] = value
        self.elementSize[2] = self.size[2] / self.shape[2]
        self.updateObserversDataSize()

    def setCurrentValuesIndex(self, value):
        """Set the value index currently selected.

        Args:
            value (int): New value of index selected.

        """
        _logger.debug("Old value index: %s, New value index: %s ",
                      self.currentValuesIndex, value)
        self.currentValuesIndex = value
        self.updateObserversIndex()

    def setCurrentOpacityIndex(self, value):
        """Select the type of data responsible for adjust the opacity.

        Args:
            value (int): New value of opacity index

        """
        _logger.debug("Old opacity index: %s, New opacity index: %s ",
                      self.currentValuesIndex, value)
        self.currentOpacityIndex = value
        self.updateObserversIndex()

    def resizeData(self):
        """Resize the matrix containing data using shape."""
        data_old = self.data.copy()
        new_shape = self.shape

        for index, _ in enumerate(self.defaultElementSize):
            self.defaultElementSize[index] = self.size[index] / self.shape[index]

        self.data = np.full(new_shape + self.valueShape, self.defaultValues)

        _logger.debug("Old shape: %s, New shape: %s ", data_old.shape, self.data.shape)

        for i in range(min(data_old.shape[0], self.data.shape[0])):
            for j in range(min(data_old.shape[1], self.data.shape[1])):
                for k in range(min(data_old.shape[2], self.data.shape[2])):
                    self.data[i, j, k] = data_old[i, j, k]

        self.updateObserversDataSize()

    @classmethod
    def registerObserver(cls, observer):
        """Register observers to be updated.

        Args:
            observer (object): Object to be registered.
        """
        if observer not in cls._observers and observer is not None:
            cls._observers.append(observer)

    @classmethod
    def updateObserversIndex(cls):
        """Update the observers index."""
        for observer in cls._observers:
            try:
                observer.updateObserverIndex()
            except Exception as e:
                _logger.debug("Could not update observer index: %s!", e)
            else:
                _logger.debug("Number of observers updated: %s", len(cls._observers))

    @classmethod
    def updateObserversData(cls):
        """Update the observers data."""
        for observer in cls._observers:
            try:
                observer.updateObserverData()
            except Exception as e:
                _logger.debug("Could not update observer data: %s!", e)
            else:
                _logger.debug("Number of observers updated: %s", len(cls._observers))

    @classmethod
    def updateObserversDataSize(cls):
        """Update the observers data size - must recreate."""
        for observer in cls._observers:
            try:
                observer.updateObserverDataSize()
            except Exception as e:
                _logger.debug("Could not update observer data size: %s!", e)
            else:
                _logger.debug("Number of observers updated: %s", len(cls._observers))
