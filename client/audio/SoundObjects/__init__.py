# Embedded file name: scripts/client/audio/SoundObjects/__init__.py
from consts import IS_EDITOR, IS_CLIENT
if IS_EDITOR:
    from Stubs import AircraftEngineSound
    from Stubs import AircraftReverseEngineSound
    from Stubs import AircraftSFX
    from Stubs import AirshowSound
    from Stubs import EffectSound
    from Stubs import MusicSound
    from Stubs import ShellSound
    from Stubs import TurretSound
    from Stubs import CameraSoundObject
    from Stubs import UI
    from Stubs import VoiceoversSoundObject
    from Stubs import WeaponSound
    from Stubs import WindSound
    from Stubs import WwiseGameObject
    from Stubs import AircraftEngineSoundFactory
    from Stubs import AircraftReverseEngineSoundFactory
    from Stubs import AircraftSFXFactory
    from Stubs import AirshowSoundFactory
    from Stubs import TurretSoundFactory
    from Stubs import WeaponSoundFactory
    from Stubs import WindSoundFactory
elif IS_CLIENT:
    from AircraftEngineSound import AircraftEngineSound
    from AircraftReverseEngineSound import AircraftReverseEngineSound
    from AircraftSFX import AircraftSFX
    from AirshowSound import AirshowSound
    from EffectSound import EffectSound
    from MusicSound import MusicSound
    from ShellSound import ShellSound
    from TurretSound import TurretSound
    from CameraSound import CameraSoundObject
    from UI import UI
    from Voiceover import VoiceoversSoundObject
    from WeaponSound import WeaponSound
    from WindSound import WindSound
    from WwiseGameObject import WwiseGameObject
    from AircraftEngineSound import AircraftEngineSoundFactory
    from AircraftReverseEngineSound import AircraftReverseEngineSoundFactory
    from AircraftSFX import AircraftSFXFactory
    from AirshowSound import AirshowSoundFactory
    from TurretSound import TurretSoundFactory
    from WeaponSound import WeaponSoundFactory
    from WindSound import WindSoundFactory
AircraftSoundObjectsFactories = [AircraftEngineSoundFactory,
 AircraftReverseEngineSoundFactory,
 AircraftSFXFactory,
 AirshowSoundFactory,
 WeaponSoundFactory,
 WindSoundFactory]
TurretSoundObjectsFactories = [TurretSoundFactory]