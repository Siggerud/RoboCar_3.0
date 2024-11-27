import unittest
from roboCarHelper import map_value_to_new_scale, round_nearest

class TestRoboCarHelper(unittest.TestCase):

    def test_round_nearest(self):
        interval = 0.05
        valueToBeRounded = 0.63

        result = round_nearest(valueToBeRounded, interval)

        self.assertEqual(0.65, result)

    def test_map_value_to_new_scale(self):
        inputvalue = 11
        newScaleMinvalue = 0
        newScaleMaxValue = 11
        oldScaleMinValue = 0
        oldScaleMaxValue = 22
        precision = 1

        result = map_value_to_new_scale(
            inputvalue,
            newScaleMinvalue,
            newScaleMaxValue,
            precision,
            oldScaleMinValue,
            oldScaleMaxValue
        )

        self.assertEqual(5.5, result)


if __name__ == '__main__':
    unittest.main()