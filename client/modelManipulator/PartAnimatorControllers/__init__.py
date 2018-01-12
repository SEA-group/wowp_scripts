# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/__init__.py
"""
Contains all animation controllers for parts of compound object
"""
from ._base import *
from AileronController import *
from BrakeController import *
from ElevatorController import *
from FlapsController import *
from MixedAileronElevator import *
from PilotHeadController import *
from PropellorController import *
from RudderController import *
from SimplePropellorController import *
from SlatsController import *
from BombHatchesController import *
from TurretAnimator.TurretAnimator import TurretAnimator
CONTROLLERS = [LeftAileronController,
 RightAileronController,
 ElevatorController,
 ElevatorReversedController,
 RudderController,
 PilotHeadController,
 PilotHeadControllerIdle,
 LeftMixedRudderElevatorController,
 RightMixedRudderElevatorController,
 LeftMixedAileronElevatorController,
 RightMixedAileronElevatorController,
 FlapsController,
 FlapsControllerL,
 FlapsControllerR,
 UpperFlapsController,
 LowerFlapsController,
 UpBrakeController,
 DownBrakeController,
 LeftBrakeController,
 RightBrakeController,
 OffsetUpBrakeController,
 OffsetDownBrakeController,
 SlatsController,
 SlatsAileronController,
 TurretAnimator,
 PropellorControllerL,
 PropellorControllerR,
 SimplePropellorL,
 SimplePropellorR,
 BombHatchControllerL,
 BombHatchControllerR]