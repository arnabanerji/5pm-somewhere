# 5pm-somewhere
"It's 5 PM somewhere!"

Is it really? Now, Alexa can tell you.

## Overview
The skill is based on the simple Hello World example skill and defines a single custom intent (`FivePMCheck`) that pulls all timezones with specific locations from http://worldtimeapi.org/. It then randomly chooses one of the locations where it is between 1700 and 1800 hours and announces the location and time with a randomly selected toast.

This skill also provides an example of a basic Python implementation of the `CanFulfillIntentRequest` interface without slots. See the `CanFulfillIntentHandler` class in [lambda_function.py](skill/lambda/lambda_function.py).

## Planned changes
* Allow querying for other times
  * If not, automatically query on launch
* An icon not generated using the built-in tool (as helpful as that was!)
