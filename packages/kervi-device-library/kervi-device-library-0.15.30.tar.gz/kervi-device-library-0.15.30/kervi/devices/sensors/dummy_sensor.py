from kervi.hal import SensorDeviceDriver

class DummySensorDeviceDriver(SensorDeviceDriver):
    def __init__(self, **kwargs):
        SensorDeviceDriver.__init__(self)

        self.value = 0
        self.delta = kwargs.get("delta", 4)
        self._min = kwargs.get("min", 0)
        self._max = kwargs.get("max", 100)
        self._interval = kwargs.get("interval", 1)
        self._unit = kwargs.get("unit", "C")
        self._type = kwargs.get("type", "temperature")

    def read_value(self):
        self.value += self.delta
        if self.value > self._max:
            self.delta *= -1
            self.value = self._max
        if self.value < self._min:
            self.delta *= -1
            self.value = self._min
        return self.value

    @property
    def type(self):
        return self._type

    @property
    def unit(self):
        return self._unit

    @property
    def max(self):
        return self._max

    @property
    def min(self):
        return self._min


class DummyMultiDimSensorDeviceDriver(SensorDeviceDriver):
    def __init__(self):
        self.value = 0
        self.delta = 4

    def read_value(self):
        self.value += self.delta
        if self.value == 100:
            self.delta *= -1
        if self.value == 0:
            self.delta *= -1
        return [self.value, self.value + 1, self.value +2]

    @property
    def dimensions(self):
        return 3

    @property
    def dimension_labels(self):
        return ["heading", "pitch", "roll"]

    @property
    def type(self):
        return "position"

    @property
    def unit(self):
        return "degree"