# -*- coding: utf-8 -*-

"""
Provides hypothesis strategies for ROS std_msgs which are usable
in both, ROS1 and ROS2 (`ROS1 std_msgs`_, `ROS2 std_msgs`_).

.. _ROS1 std_msgs:
   URL

.. _ROS2 std_msgs:
   URL
"""

from collections import namedtuple
from hypothesis.strategies import composite

from hypothesis_ros.ros1.builtin_msg_field_types import uint32 # floats, time, 

_Header = namedtuple('Header', 'seq') # 'seq stamp frame_id'

@composite
def header(draw, seq=uint32()):
    """
    Generate value for ROS standard message type "header".

    Parameters
    ----------
    seq : hypothesis_ros.ros1.uint32()
        Strategy to generate seq value. (Default: Default hypothesis_ros strategy.)
    stamp : hypothesis_ros.ros1.time()
        Strategy to generate stamp value. (Default: Default hypothesis_ros strategy.)
    frame_id : hypothesis_ros.ros1.floats()
        Strategy to generate frame_id value. (Default: Default hypothesis_ros strategy.)

    """
    seq_value = draw(seq)
    assert isinstance(seq_value, uint32), 'drew invalid x={seq_value} from {seq} for uint32 field'.format(seq_value, seq)
    #assert isinstance(y_value, float), 'drew invalid y={y_value} from {y} for float64 field'.format(y_value, y)
    #assert isinstance(z_value, float), 'drew invalid y={z_value} from {z} for float64 field'.format(z_value, z)
    return _Header(seq_value)