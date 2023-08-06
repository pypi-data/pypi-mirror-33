import numpy as np
from pyquaternion import Quaternion

from pye57 import libe57
from pye57.utils import get_fields, get_node


class ScanHeader:
    def __init__(self, scan_node):
        self.node = scan_node
        points = self.node["points"]
        self.point_fields = get_fields(libe57.StructureNode(points.prototype()))
        self.scan_fields = get_fields(self.node)

    @classmethod
    def from_data3d(cls, data3d):
        return [cls(scan) for scan in data3d]

    def _assert_pose(self):
        if not self.node.isDefined("pose"):
            raise ValueError("Scan header doesn't contain a pose")

    @property
    def point_count(self):
        return self.points.childCount()

    @property
    def rotation_matrix(self) -> np.array:
        self._assert_pose()
        q = Quaternion([e.value() for e in self.node["pose"]["rotation"]])
        return q.rotation_matrix

    @property
    def rotation(self) -> np.array:
        self._assert_pose()
        q = Quaternion([e.value() for e in self.node["pose"]["rotation"]])
        return q.elements

    @property
    def translation(self):
        self._assert_pose()
        return np.array([e.value() for e in self.node["pose"]["translation"]])

    def pretty_print(self, node=None, indent=""):
        if node is None:
            node = self.node
        lines = []
        for field in get_fields(node):
            child_node = node[field]
            value = ""
            if hasattr(child_node, "value"):
                value = ": %s" % child_node.value()
            lines.append(indent + str(child_node) + value)
            if isinstance(child_node, libe57.StructureNode):
                lines += self.pretty_print(child_node, indent + "    ")
        return lines

    def __getitem__(self, item):
        return self.node[item]

    @property
    def guid(self):
        return self["guid"].value()

    @property
    def temperature(self):
        return self["temperature"].value()

    @property
    def relativeHumidity(self):
        return self["relativeHumidity"].value()

    @property
    def atmosphericPressure(self):
        return self["atmosphericPressure"].value()

    @property
    def indexBounds(self):
        return self["indexBounds"]

    @property
    def rowMinimum(self):
        return self.indexBounds["rowMinimum"].value()

    @property
    def rowMaximum(self):
        return self.indexBounds["rowMaximum"].value()

    @property
    def columnMinimum(self):
        return self.indexBounds["columnMinimum"].value()

    @property
    def columnMaximum(self):
        return self.indexBounds["columnMaximum"].value()

    @property
    def returnMinimum(self):
        return self.indexBounds["returnMinimum"].value()

    @property
    def returnMaximum(self):
        return self.indexBounds["returnMaximum"].value()

    @property
    def intensityLimits(self):
        return self["intensityLimits"]

    @property
    def intensityMinimum(self):
        return self.intensityLimits["intensityMinimum"].value()

    @property
    def intensityMaximum(self):
        return self.intensityLimits["intensityMaximum"].value()

    @property
    def cartesianBounds(self):
        return self["cartesianBounds"]

    @property
    def xMinimum(self):
        return self.cartesianBounds["xMinimum"].value()

    @property
    def xMaximum(self):
        return self.cartesianBounds["xMaximum"].value()

    @property
    def yMinimum(self):
        return self.cartesianBounds["yMinimum"].value()

    @property
    def yMaximum(self):
        return self.cartesianBounds["yMaximum"].value()

    @property
    def zMinimum(self):
        return self.cartesianBounds["zMinimum"].value()

    @property
    def zMaximum(self):
        return self.cartesianBounds["zMaximum"].value()

    @property
    def pose(self):
        return self["pose"]

    @property
    def acquisitionStart(self):
        return self["acquisitionStart"]

    @property
    def acquisitionStart_dateTimeValue(self):
        return self.acquisitionStart["dateTimeValue"].value()

    @property
    def acquisitionStart_isAtomicClockReferenced(self):
        return self.acquisitionStart["isAtomicClockReferenced"].value()

    @property
    def acquisitionEnd(self):
        return self["acquisitionEnd"]

    @property
    def acquisitionEnd_dateTimeValue(self):
        return self.acquisitionEnd["dateTimeValue"].value()

    @property
    def acquisitionEnd_isAtomicClockReferenced(self):
        return self.acquisitionEnd["isAtomicClockReferenced"].value()

    @property
    def pointGroupingSchemes(self):
        return self["pointGroupingSchemes"]

    @property
    def points(self):
        return self["points"]
