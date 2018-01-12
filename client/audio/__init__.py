# Embedded file name: scripts/client/audio/__init__.py
from consts import IS_EDITOR, IS_CLIENT
if IS_EDITOR:
    from GameSoundImplStub import GameSound
elif IS_CLIENT:
    from GameSoundImpl import GameSound
from SoundObjects import AircraftEngineSound
from SoundObjects import AircraftReverseEngineSound
from SoundObjects import AircraftSFX
from SoundObjects import AirshowSound
from SoundObjects import EffectSound
from SoundObjects import MusicSound
from SoundObjects import ShellSound
from SoundObjects import CameraSoundObject
from SoundObjects import UI
from SoundObjects import VoiceoversSoundObject
from SoundObjects import WeaponSound
from SoundObjects import WindSound
from SoundObjects import WwiseGameObject