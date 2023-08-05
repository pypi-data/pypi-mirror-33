lambdaskill
===========

A simple Python 3 toolkit to build `Alexa
Skills <https://developer.amazon.com/alexa-skills-kit>`__ using `AWS
Lambda <https://aws.amazon.com/lambda/>`__.

``lambdaskill`` itself has no external dependencies beyond the Python
standard library. However, the included utilties package requires the
aniso8601 package.

The interface is pretty straight-forward. Just subclass the Skill class
to create your own skill. Add methods named like ``do_yourintent()`` to
handle an intent named 'yourintent'. Use the ``Response`` object to
prepare a response. ``Card``\ s can be attached to the response if
desired. The lambda function handler is obtained by calling the
``get_handler()`` class method on your new class.

The following is a simple demo that would respond to an intent called
'hellointent' that has a slot named 'NAME':

.. code:: python

    from lambdaskill import *

    class DemoSkill(Skill):

        def do_hellointent(self, request):
            slots = request.get_slots()
            name = slots['NAME']
            return Response.respond('Hello, {}'.format(name))

    handler = DemoSkill.get_handler()

Note that intents that include characters not permitted in Python method
names (such as the Amazon built-in intents, ex:
AMAZON.SearchAction\ object@WeatherForecast%5Btemperature%5D) can be
handled as follows (extending the example above):

.. code:: python

    @DemoSkill.intent('AMAZON.SearchAction<object@WeatherForecast[temperature]>')
    def weather_intent_handler(self, request):
        return Response.respond('You asked about the weather.')

Which will add the intent handler to the class definition with an
appropriately mangled name. Obviously, you would include these lines
before the call to ``get_hander()``, as the ``get_handler()`` call
creates an instance of the class and returns the handler method of that
instance.
