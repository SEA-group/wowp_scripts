# Embedded file name: scripts/client/CameraStatesEffectsSettings.py
from CameraStates import CameraState
EFFECTS_MAP = {'SPEED_BLUR': (CameraState.MouseCombat,
                CameraState.JoystickCombat,
                CameraState.GamepadCombat,
                CameraState.Sniper),
 'HEIGHT_BLUR': (CameraState.MouseCombat,
                 CameraState.JoystickCombat,
                 CameraState.GamepadCombat,
                 CameraState.Sniper),
 'AIRCRAFT_IDLE_VIBRATION': (CameraState.MouseCombat,
                             CameraState.JoystickCombat,
                             CameraState.GamepadCombat,
                             CameraState.Gunner,
                             CameraState.Sniper)}