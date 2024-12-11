def map_value_to_new_scale(inputValue, newScaleMinValue, newScaleMaxValue, valuePrecision, oldScaleMinValue=-1, oldScaleMaxValue=1):
    newScaleSpan = newScaleMaxValue - newScaleMinValue
    oldScaleSpan = oldScaleMaxValue - oldScaleMinValue

    valueScaled = float(inputValue - oldScaleMinValue) / float(oldScaleSpan)
    valueMapped = round(newScaleMinValue + (valueScaled * newScaleSpan), valuePrecision)

    return valueMapped


def chain_together_dict_keys(dicts: list[dict]) -> list[str]:
    combinedKeys: list = []
    for dict in dicts:
        combinedKeys.extend(list(dict.keys()))

    return combinedKeys

def print_startup_error(error):
    print("Something went wrong during startup. Exiting...")
    print(error)

def round_nearest(x, a):
    return round(x / a) * a

def convert_from_board_number_to_bcm_number(boardNumber):
    gpioNumbering = {
        3: 2,
        5: 3,
        7: 4,
        11: 17,
        12: 18,
        13: 27,
        15: 22,
        16: 23,
        18: 24,
        19: 10,
        21: 9,
        22: 25,
        23: 11,
        24: 8,
        26: 7,
        29: 5,
        31: 6,
        32: 12,
        33: 13,
        35: 19,
        36: 16,
        37: 26,
        38: 20,
        40: 21}

    # TODO: throw an exception if boardNumber is not in dict keys
    bcmNumber = gpioNumbering[boardNumber]

    return bcmNumber

number_to_word = {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
            "10": "ten",
            "11": "eleven",
            "12": "twelve",
            "13": "thirteen",
            "14": "fourteen",
            "15": "fifteen",
            "16": "sixteen",
            "17": "seventeen",
            "18": "eighteen",
            "19": "nineteen",
            "20": "twenty"
        }