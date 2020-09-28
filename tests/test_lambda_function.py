import pytest
from skill.lambda import lambda_function

five_pm_check = lambda_function.FivePMCheckIntentHandler().handle

class FakeInputHandler:
    class FakeResponseBuilder:
        def __init__(self):
            self.response = ""
            

        def speak(self, output):
            self.response = output
            return self


    def __init__(self):
        self.response_builder = FakeResponseBuilder()


def test_lambda_function_normal():
    assert five_pm_check(FakeInputHandler)