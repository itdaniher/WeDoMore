from bisect import bisect_left, bisect_right

# data from distance sensor -> real measure in meters under ideal conditions (no side object, perpendicular wall)
RAW_MEASURES = {
    210: 0.46,
    208: 0.39,
    207: 0.34,
    206: 0.32,
    205: 0.305,
    204: 0.29,
    203: 0.27,
    202: 0.26,
    201: 0.25,
    200: 0.245,
    199: 0.235,
    198: 0.225,
    197: 0.22,
    196: 0.215,
    195: 0.2,
    194: 0.195,
    193: 0.18,
    192: 0.175,
    191: 0.17,
    180: 0.15,
    170: 0.13,
    160: 0.125,
    150: 0.11,
    140: 0.105,
    130: 0.1,
    120: 0.095,
    100: 0.075,
    71: 0.065,
    70: 0.06,
    69: 0.053,
    68: 0}

RAW_MEASURES_KEYS = sorted(list(RAW_MEASURES))


def interpolate_distance_data(raw):
    left_index = bisect_left(RAW_MEASURES_KEYS, raw) - 1
    if left_index < 0:
        left_index = 0
    right_index = left_index if left_index == len(RAW_MEASURES_KEYS) - 1 else left_index + 1

    left = RAW_MEASURES_KEYS[left_index]
    if left > raw:
        return RAW_MEASURES[RAW_MEASURES_KEYS[left_index]]

    right = RAW_MEASURES_KEYS[right_index]
    mright = RAW_MEASURES[right]
    mleft = RAW_MEASURES[left]
    addup = ((raw - left) / (right - left)) * (mright - mleft) if mright != mleft else 0
    return mleft + addup