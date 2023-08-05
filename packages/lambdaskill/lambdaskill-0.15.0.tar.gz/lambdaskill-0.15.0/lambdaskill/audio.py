import enum
import lambdaskill.skill as skill


class PLAY_BEHAVIOR(enum.Enum):
    ENQUEUE = "ENQUEUE"
    REPLACE_ALL = "REPLACE_ALL"
    REPLACE_ENQUEUED = "REPLACE_ENQUEUED"


class CLEAR_BEHAVIOR(enum.Enum):
    CLEAR_ENQUEUED = "CLEAR_ENQUEUED"
    CLEAR_ALL = "CLEAR_ALL"


class StopDirective(skill.Directive):

    directive_type = 'AudioPlayer.Stop'


class ClearQueueDirective(skill.Directive):

    directive_type = 'AudioPlayer.ClearQueue'

    def __init__(self, clear_behavior):
        super(ClearQueueDirective, self).__init__()
        self.clear_behavior = CLEAR_BEHAVIOR(clear_behavior)

    def prepare(self):
        return {
            'type': type(self).directive_type,
            'clearBehavior': self.clear_behavior.value
        }


class PlayDirective(skill.Directive):

    directive_type = 'AudioPlayer.Play'

    def __init__(self, audio_item, play_behavior):
        super(PlayDirective, self).__init__()
        self.audio_item = audio_item
        self.play_behavior = PLAY_BEHAVIOR(play_behavior)

    def prepare(self):
        return {
            'type': type(self).directive_type,
            'audioItem': self.audio_item.prepare(),
            'playBehavior': self.play_behavior.value
        }


class AudioMetaData(object):

    def __init__(self, title=None, subtitle=None, art=None, background=None):
        self.title = title
        self.subtitle = subtitle
        self.art = art
        self.background = background

    def prepare(self):
        metadata = {
            'title': self.title,
            'subtitle': self.subtitle
        }
        metadata = {k: v for k, v in metadata.items() if v}
        if self.art:
            metadata['art'] = self.art.prepare()
        if self.background:
            metadata['backgroundImage'] = self.background.prepare()


class AudioItem(object):

    def __init__(self, url, token, expected_previous_token=None, offset=0, metadata=None):
        self.url = url
        self.token = token
        self.expected_previous_token = expected_previous_token
        self.offset = offset
        self.metadata = metadata

    def add_metadata(self, title=None, subtitle=None, art=None, background=None):
        self.metadata = AudioMetaData(title=title, subtitle=subtitle,
                                      art=art, background=background)
        return self

    def with_metadata(self, metadata):
        self.metadata = metadata
        return self

    def prepare(self):
        audioitem = {
            'stream': {
                'url': self.url,
                'token': self.token,
                'expectedPreviousToken': self.expected_previous_token,
                'offsetInMilliseconds': self.offset
            }
        }

        if self.metadata:
            audioitem['metadata'] = self.metadata.prepare()

        return audioitem


class AudioSkill(skill.Skill):

    def __init__(self):
        super(AudioSkill, self).__init__()

    def on_audioplayer_playback_started(self, request):
        return

    def on_audioplayer_playback_finished(self, request):
        return

    def on_audioplayer_playback_stopped(self, request):
        return

    def on_audioplayer_playback_nearly_finished(self, request):
        return

    def on_audioplayer_playback_failed(self, request):
        return

    def do_AMZ_pauseintent(self, request):
        raise NotImplementedError()
    
    def do_AMZ_resumeintent(self, request):
        raise NotImplementedError()
    
    def do_AMZ_cancelintent(self, request):
        return NotImplementedError()
    
    def do_AMZ_nextintent(self, request):
        return skill.Response.finish('Track skipping is not implemented for this skill.')
    
    def do_AMZ_previousintent(self, request):
        return skill.Response.finish('Track skipping is not implemented for this skill.')

    def do_AMZ_startoverintent(self, request):
        return skill.Response.finish('Restarting a track is not implemented for this skill.')

    def do_AMZ_shuffleoffintent(self, request):
        return skill.Response.finish('Shuffling is not implemented for this skill.')
    
    def do_AMZ_shuffleonintent(self, request):
        return skill.Response.finish('Shuffling is not implemented for this skill.')
    
    def do_AMZ_repeatintent(self, request):
        return skill.Response.finish('Repeating is not implemented for this skill.')
    
    def do_AMZ_loopoffintent(self, request):
        return skill.Response.finish('Looping is not implemented for this skill.')

    def do_AMZ_looponintent(self, request):
        return skill.Response.finish('Looping is not implemented for this skill.')

    def dispatch(self, request):
        request_handlers = {
            'AudioPlayer.PlaybackStarted': self.on_audioplayer_playback_started,
            'AudioPlayer.PlaybackFinished': self.on_audioplayer_playback_finished,
            'AudioPlayer.PlaybackStopped': self.on_audioplayer_playback_stopped,
            'AudioPlayer.PlaybackNearlyFinished': self.on_audioplayer_playback_nearly_finished,
            'AudioPlayer.PlaybackFailed': self.on_audioplayer_playback_failed
        }
        handler = request_handlers.get(request.request_type, None)
        if handler:
            return handler(request=request)
        return super(AudioSkill, self).dispatch(request=request)
