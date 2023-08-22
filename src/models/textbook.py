from enum import Enum


class TextbookNames(str, Enum):
    MACRO_ECON = "macroeconomics-2e"
    THINK_PYTHON = "think-python-2e"

if __name__ == "__main__":
    test = TextbookNames.MACRO_ECON
    print(test.value)