# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import json
import datetime
import random
import concurrent.futures
from num2words import num2words
from urllib3 import PoolManager, Retry
from urllib3.exceptions import MaxRetryError
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.canfulfill import can_fulfill_intent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "It's five PM somewhere. Ask me where!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class FivePMCheckIntentHandler(AbstractRequestHandler):
    """Handler for 5 PM Check Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FivePMCheck")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        retries = Retry(connect=2, read=2, status=2)
        http = PoolManager(retries=retries)
        
        def get_time(timezone):
            time_object = json.loads(http.request("GET", "http://worldtimeapi.org/api/timezone/" + timezone).data)
            dt_in_tz = datetime.datetime.strptime(time_object["datetime"][:-6], "%Y-%m-%dT%H:%M:%S.%f")
            return dt_in_tz
        
        try:
            zonelist = json.loads(http.request("GET", "http://worldtimeapi.org/api/timezone").data)
            zonelist = [zone for zone in zonelist if "etc" not in zone.lower() and "/" in zone.lower()]

            times = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                # Start the load operations and mark each future with its URL
                future_to_zone = {executor.submit(get_time, zone): zone for zone in zonelist}
                for future in concurrent.futures.as_completed(future_to_zone):
                    zone = future_to_zone[future]
                    try:
                        time = future.result()
                    except Exception as exc:
                        print('%r generated an exception: %s' % (url, exc))
                    else:
                        if time.hour == 17:
                            place = zone
                            place_pieces = zone.split("/")
                            if len(place_pieces) > 1:
                                place = place_pieces[-1]
                            
                            min_string = num2words(time.minute)
                            if time.minute < 10:
                                min_string = "o " + min_string
                            if time.minute == 0:
                                min_string = "o clock"
                            times.append({"place": place, "time": "five {}".format(min_string)})
                    
            if times:
                chosen = random.choice(times)
                toast = random.choice(["Cheers", "Bottoms up", "Prost", "Skol", "Salud"])
                speak_output = "It's {} in {}. {}!".format(chosen["time"], chosen["place"].replace("_", " "), toast)
        except MaxRetryError:
            logging.error("Error connecting to World Time API", exc_info=1)
            speak_output = "I'm having trouble finding the time around the world, but it's five PM somewhere! Try again later."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CanFulfillIntentHandler(AbstractRequestHandler):
    """Handler for CanFulfillIntentRequest."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("CanFulfillIntentRequest")(handler_input)

    def handle(self, handler_input):
        if ask_utils.is_intent_name("FivePMCheck"):
            fulfillintent = can_fulfill_intent.CanFulfillIntent("YES")
        else:
            fulfillintent = can_fulfill_intent.CanFulfillIntent("NO")
        handler_input.response_builder.set_can_fulfill_intent(fulfillintent)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Ask me where it's five PM!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(CanFulfillIntentHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(FivePMCheckIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()