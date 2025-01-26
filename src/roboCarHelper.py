class RobocarHelper:
    def __init__(self):
        pass

    @staticmethod
    def low_pass_filter(currentValue: float, previousValue: float, confidenceFactor:float=0.1) -> float:
        return previousValue * (1 - confidenceFactor) + currentValue * confidenceFactor

    @staticmethod
    def map_value_to_new_scale(inputValue, newScaleMinValue, newScaleMaxValue, valuePrecision, oldScaleMinValue=-1,
                               oldScaleMaxValue=1) -> float:
        newScaleSpan = newScaleMaxValue - newScaleMinValue
        oldScaleSpan = oldScaleMaxValue - oldScaleMinValue

        valueScaled = float(inputValue - oldScaleMinValue) / float(oldScaleSpan)
        valueMapped = round(newScaleMinValue + (valueScaled * newScaleSpan), valuePrecision)

        return valueMapped

    @staticmethod
    def chain_together_dict_keys(dicts: list[dict]) -> list[str]:
        combinedKeys: list = []
        for dict in dicts:
            combinedKeys.extend(list(dict.keys()))

        return combinedKeys

    @staticmethod
    def print_startup_error(error) -> None:
        print("Something went wrong during startup. Exiting...")
        print(error)

    @staticmethod
    def round_nearest(x, a) -> float:
        return round(x / a) * a



