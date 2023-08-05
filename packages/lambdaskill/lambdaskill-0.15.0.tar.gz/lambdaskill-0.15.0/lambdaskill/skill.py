import enum
import logging

from lambdaskill.ssml import SSML


class PLAYER_ACTIVITY(enum.Enum):
    IDLE = "IDLE"
    PAUSED = "PAUSED"
    PLAYING = "PLAYING"
    BUFFER_UNDERRUN = "BUFFER_UNDERRUN"
    FINISHED = "FINISHED"
    STOPPED = "STOPPED"


class DIALOG_STATE(enum.Enum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    
    
logger = logging.getLogger('lambdaskill')
logger.addHandler(logging.StreamHandler())
if logger.level == logging.NOTSET:
    logger.setLevel(logging.WARNING)


class Directive(object):

    directive_type = None

    def prepare(self):
        return {'type': self.directive_type}


class DialogDelegateDirective(Directive):

    directive_type = 'Dialog.Delegate'


class Card(object):

    def __init__(self, title, content=None, text=None, small_image_url=None, large_image_url=None):
        self.title = title
        self.content = content
        self.text = text
        self.small_image_url = small_image_url
        self.large_image_url = large_image_url

    def prepare(self):
        if self.text is not None:
            card = {
                'type': 'Standard',
                'title': self.title,
                'text': self.text
            }
            if any([self.small_image_url, self.large_image_url]):
                image = {k: v for k, v in zip(['smallImageUrl', 'largeImageUrl'],
                                              [self.small_image_url, self.large_image_url]) if v is not None}
                card['image'] = image
            return card
        return {
            'type': 'Simple',
            'title': self.title,
            'content': self.content
        }


class Response(object):

    def __init__(self, output=None, reprompt_text=None, should_end_session=None):
        self.output = output
        self.reprompt_text = reprompt_text
        self.should_end_session = should_end_session
        self.card = None
        self.directives = []

    def add_card(self, title, content=None):
        if content is None:
            content = self.output
        self.card = Card(title=title, content=content)
        return self

    def with_card(self, card):
        self.card = card
        return self

    def add_reprompt(self, reprompt_text=None):
        if reprompt_text is None:
            reprompt_text = self.output
        self.reprompt_text = reprompt_text
        return self

    def add_directive(self, directive):
        self.directives.append(directive)
        return self

    def prepare(self, session_attributes=None):
        response = {}
        if self.output is not None:
            if isinstance(self.output, SSML):
                response['outputSpeech'] = {
                    'type': 'SSML',
                    'ssml': self.output.content
                }
            else:
                response['outputSpeech'] = {
                    'type': 'PlainText',
                    'text': self.output
                }
        if self.reprompt_text is not None:
            if isinstance(self.reprompt_text, SSML):
                response['reprompt'] = {
                    'outputSpeech': {
                        'type': 'SSML',
                        'ssml': self.reprompt_text.content
                    }
                }
            else:
                response['reprompt'] = {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': self.reprompt_text
                    }
                }
        if self.should_end_session is not None:
            response['shouldEndSession'] = self.should_end_session

        if self.directives:
            response['directives'] = [d.prepare() for d in self.directives]

        if self.card is not None:
            response['card'] = self.card.prepare()

        container = {
            'version': '1.0',
            'response': response
        }
        if session_attributes:
            container['sessionAttributes'] = session_attributes

        return container

    @staticmethod
    def respond(output):
        return Response(output=output, should_end_session=False)

    @staticmethod
    def finish(output):
        return Response(output=output, should_end_session=True)

    @staticmethod
    def direct(directive, output=None):
        return Response(output=output, should_end_session=True).add_directive(directive=directive)


class AudioPlayer(object):

    def __init__(self, request_json):
        try:
            ap = request_json['context']['AudioPlayer']
            self.__token = ap.get('token', None)
            self.__offset_in_milliseconds = ap.get('offsetInMilliseconds', None)
            self.__player_activity = PLAYER_ACTIVITY(ap.get('playerActivity', None))
        except KeyError:
            raise ValueError('No AudioPlayer information in Request.')

    @property
    def token(self):
        return self.__token

    @property
    def offset_in_milliseconds(self):
        return self.__offset_in_milliseconds

    @property
    def player_activity(self):
        return self.__player_activity


class Request(object):

    def __init__(self, request_json):
        self.j = request_json
        try:
            self.__audio_player = AudioPlayer(request_json)
        except ValueError:
            self.__audio_player = None

    @property
    def new_session(self):
        try:
            return self.j['session']['new']
        except KeyError:
            pass
        return False

    @property
    def session_attributes(self):
        try:
            return self.j['session']['attributes']
        except KeyError:
            if 'session' in self.j:
                self.j['session']['attributes'] = {}
                return self.j['session']['attributes']
        return None

    @property
    def audio_player(self):
        return self.__audio_player

    @property
    def request_type(self):
        return self.j['request']['type']

    @staticmethod
    def wrap(request_json):
        try:
            request_type = request_json['request']['type']
            for sc in Request.__subclasses__():
                if sc.__name__ == request_type:
                    return sc(request_json)
        except KeyError:
            pass
        return Request(request_json=request_json)


class IntentRequest(Request):

    def __init__(self, request_json):
        super(IntentRequest, self).__init__(request_json=request_json)

    @property
    def intent_name(self):
        return self.j['request']['intent']['name']

    def get_slots(self):
        try:
            raw_slots = self.j['request']['intent']['slots']
            return {k: v['value'] for k, v in raw_slots.items() if 'value' in v}
        except KeyError:
            pass
        return {}


class Skill(object):

    def __init__(self):
        self._app_id = None

    def on_session_start(self, request):
        logger.info('Starting new session.')

    def on_launch_request(self, request):
        logger.info('Received Launch Request.')
        return Response.respond("Welcome")

    def on_session_ended_request(self, request):
        logger.info('Received Session Ended Request.')

    def on_default_intent_request(self, request):
        logger.info('Received un-handled IntentRequest: {}'.format(request.intent_name))
        return Response.respond("I'm afraid that I didn't understand that request, please try again.").add_reprompt()

    def dispatch(self, request):

        response = None
        if request.request_type == "SessionEndedRequest":
            self.on_session_ended_request(request=request)
        elif request.request_type == "LaunchRequest":
            response = self.on_launch_request(request=request)
        elif isinstance(request, IntentRequest):
            f = getattr(self, self.mangle(request.intent_name), self.on_default_intent_request)
            response = f(request)
        return response

    def handler(self, event, context):

        request = Request.wrap(event)

        if self._app_id is not None:
            if request.j['session']['application']['applicationId'] != self._app_id:
                raise ValueError("Invalid Application ID")

        if request.new_session:
            self.on_session_start(request)

        response = self.dispatch(request=request)

        if response:
            return response.prepare(session_attributes=request.session_attributes)
        return

    @staticmethod
    def mangle(intent_name):
        return "do_" + intent_name.lower().replace("amazon.", "AMZ_") \
            .replace("<", "_LT_") \
            .replace(">", "_GT") \
            .replace("@", "_AT_") \
            .replace("[", "_LB_") \
            .replace("]", "_RB_")

    @classmethod
    def intent(cls, intent_name):

        mangled = cls.mangle(intent_name)

        def decorator(f):
            setattr(cls, mangled, f)
            return f

        return decorator

    @classmethod
    def get_handler(cls):
        return cls().handler
