from wedo.distance import interpolate_distance_data
from nose.tools import assert_equals
def test_interpolation():
    yield assert_equals, interpolate_distance_data(210), 0.46
    yield assert_equals, interpolate_distance_data(68), 0
    yield assert_equals, interpolate_distance_data(50), 0
    yield assert_equals, interpolate_distance_data(175), 0.14
