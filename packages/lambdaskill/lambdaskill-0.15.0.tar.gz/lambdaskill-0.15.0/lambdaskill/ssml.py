from enum import Enum
import re


class StrEnum(Enum):

    def __str__(self):
        return str(self.value)


class AMAZON_EFFECTS(StrEnum):
    WHISPERED = "whispered"


class BREAK_STRENGTH(StrEnum):
    NONE = "none"
    X_WEAK = "x-weak"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    X_STRONG = "x-strong"


class EMPHASIS_LEVEL(StrEnum):
    REDUCED = "reduced"
    MODERATE = "moderate"
    STRONG = "strong"


class PHONEME_ALPHABET(StrEnum):
    IPA = "ipa"
    X_SAMPA = "x-sampa"


class PROSODY_RATE(StrEnum):
    X_SLOW = 'x-slow'
    SLOW = 'slow'
    MEDIUM = 'medium'
    FAST = 'fast'
    X_FAST = 'x-fast'


class PROSODY_PITCH(StrEnum):
    X_LOW = 'x-low'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    X_HIGH = 'x-high'


class PROSODY_VOLUME(StrEnum):
    SILENT = 'silent'
    X_SOFT = 'x-soft'
    SOFT = 'soft'
    MEDIUM = 'medium'
    LOUD = 'loud'
    X_LOUD = 'x-loud'


class SAY_AS_INTERPRETATIONS(StrEnum):
    ADDRESS = 'address'
    CARDINAL = 'cardinal'
    CHARACTERS = 'characters'
    DATE = 'date'
    DIGITS = 'digits'
    EXPLETIVE = 'expletive'
    FRACTION = 'fraction'
    INTERJECTION = 'interjection'
    NUMBER = 'number'
    ORDINAL = 'ordinal'
    SPELL_OUT = 'spell-out'
    TELEPHONE = 'telephone'
    TIME = 'time'
    UNIT = 'unit'


class WORD_ROLES(StrEnum):
    VERB_PRESENT = 'amazon:VB'
    VERB_PAST = 'amazon:VBD'
    NOUN = 'amazon:NN'
    SENSE_1 = 'amazon:SENSE_1'


class Element(object):

    def __init__(self, tag, attributes=None, children=None):
        self.__tag = tag
        self.__attributes = attributes or {}
        self.children = children or []
        if isinstance(self.children, str):
            self.children = [self.children, ]

    def __getitem__(self, item):
        return self.__attributes[item]

    def __setitem__(self, key, value):
        self.__attributes[key] = value

    def __str__(self):
        result = []
        tag_parts = [self.__tag]
        tag_parts.extend(["{}='{}'".format(k, str(v)) for k, v in self.__attributes.items() if v])
        tag = ' '.join(tag_parts)
        if len(self.children) == 0:
            return "<{} />".format(tag)
        result.append("<{}>".format(tag))
        for child in self.children:
            result.append(str(child))
        result.append("</{}>".format(self.__tag))
        return ''.join(result)

    def add_child(self, child):
        if child:
            self.children.append(child)


class AmazonEffect(Element):

    def __init__(self, name=AMAZON_EFFECTS.WHISPERED, children=None):
        name = AMAZON_EFFECTS(name)
        super(AmazonEffect, self).__init__('amazon:effect', {'name': name}, children=children)


class Audio(Element):

    def __init__(self, src):
        if not src:
            raise ValueError('A URL must be specified for src.')
        super(Audio, self).__init__('audio', {'src': src})


class Break(Element):

    def __init__(self, strength=None, time=None):
        if strength and time:
            raise ValueError('Specify either strength or time but not both.')
        if strength:
            strength = BREAK_STRENGTH(strength)
        super(Break, self).__init__('break', {'strength': strength, 'time': time})


class Emphasis(Element):

    def __init__(self, level, children=None):
        level = EMPHASIS_LEVEL(level)
        super(Emphasis, self).__init__('emphasis', {'level': level}, children=children)


class Paragraph(Element):

    def __init__(self, children=None):
        super(Paragraph, self).__init__('p', children=children)

    def __str__(self):
        return ''.join([super(Paragraph, self).__str__(), '\n'])


class Phoneme(Element):

    def __init__(self, ph, alphabet=PHONEME_ALPHABET.X_SAMPA, children=None):
        super(Phoneme, self).__init__('phoneme',
                                      {'alphabet': alphabet, 'ph': ph},
                                      children=children)


class Prosody(Element):

    def __init__(self, rate=None, pitch=None, volume=None, children=None):
        rate = self._validate_rate(rate)
        pitch = self._validate_pitch(pitch)
        volume = self._validate_volume(volume)
        super(Prosody, self).__init__('prosody',
                                      {'rate': rate,
                                       'pitch': pitch,
                                       'volume': volume},
                                      children=children)

    @staticmethod
    def _validate_rate(rate):
        if not rate:
            return rate
        try:
            return PROSODY_RATE(rate)
        except ValueError:
            pass
        if re.search('[0-9]{1,3}%', rate):
            return rate
        raise ValueError('Invalid value for rate.')

    @staticmethod
    def _validate_pitch(pitch):
        if not pitch:
            return pitch
        try:
            return PROSODY_PITCH(pitch)
        except ValueError:
            pass
        if re.search('[+-][0-9]{1,2}%', pitch):
            return pitch
        raise ValueError('Invalid value for pitch.')

    @staticmethod
    def _validate_volume(volume):
        if not volume:
            return volume
        try:
            return PROSODY_VOLUME(volume)
        except ValueError:
            pass
        if re.search('[+-][0-9]+(\.[0-9]+)?dB', volume):
            return volume
        raise ValueError('Invalid value for volume.')


class Sentence(Element):

    def __init__(self, children=None):
        super(Sentence, self).__init__('s', children=children)

    def __str__(self):
        return ''.join([super(Sentence, self).__str__(), ' '])


class SayAs(Element):

    def __init__(self, interpret_as, format=None, children=None):
        interpret_as = SAY_AS_INTERPRETATIONS(interpret_as)
        super(SayAs, self).__init__('say-as',
                                    {'interpret-as': interpret_as,
                                     'format': format},
                                    children=children)


class Speak(Element):

    def __init__(self, children=None):
        super(Speak, self).__init__('speak', children=children)


class Sub(Element):

    def __init__(self, alias, children=None):
        super(Sub, self).__init__('sub', {'alias': alias}, children=children)


class Word(Element):

    def __init__(self, role, children=None):
        role = WORD_ROLES(role)
        super(Word, self).__init__('w', {'role': role}, children=children)


class SSML(object):

    def __init__(self):
        self.__speach = Speak()
        self.__stack = [self.__speach]

    @property
    def content(self):
        return str(self.__speach)

    def sentence(self, children=None):
        element = Sentence(children=children)
        self.__stack[-1].add_child(element)
        self.__stack.append(element)
        return self

    def paragraph(self, children=None):
        element = Paragraph(children=children)
        self.__stack[-1].add_child(element)
        self.__stack.append(element)
        return self

    def word(self, text, role):
        element = Word(role=role, children=[text])
        self.__stack[-1].add_child(element)
        return self

    def amazon_effect(self, name=AMAZON_EFFECTS.WHISPERED, children=None):
        element = AmazonEffect(name=name, children=children)
        self.__stack[-1].add_child(element)
        self.__stack.append(element)
        return self

    def audio(self, src):
        element = Audio(src=src)
        self.__stack[-1].add_child(element)
        return self

    def break_element(self, strength=None, time=None):
        element = Break(strength=strength, time=time)
        self.__stack[-1].add_child(element)
        return self

    def emphasis(self, level, children=None):
        element = Emphasis(level=level, children=children)
        self.__stack[-1].add_child(element)
        self.__stack.append(element)
        return self

    def phoneme(self, text, ph, alphabet=PHONEME_ALPHABET.X_SAMPA):
        element = Phoneme(ph, alphabet=alphabet, children=[text])
        self.__stack[-1].add_child(element)
        return self

    def prosody(self, rate=None, pitch=None, volume=None, children=None):
        element = Prosody(rate=rate, pitch=pitch, volume=volume, children=children)
        self.__stack[-1].add_child(element)
        self.__stack.append(element)
        return

    def say_as(self, text, interpret_as, format=None):
        element = SayAs(interpret_as=interpret_as, format=format, children=[text])
        self.__stack[-1].add_child(element)
        return self

    def sub(self, text, alias):
        element = Sub(alias=alias, children=[text])
        self.__stack[-1].add_child(element)
        return self

    def add_text(self, text):
        self.__stack[-1].add_child(text)
        return self

    def end_tag(self):
        self.__stack.pop(-1)
        return self
