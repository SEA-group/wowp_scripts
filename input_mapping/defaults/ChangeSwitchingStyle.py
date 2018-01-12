# Embedded file name: scripts/input_mapping/defaults/ChangeSwitchingStyle.py
import os
from lxml import etree
from itertools import ifilter
targetCommands = ['CMD_INCREASE_FORCE',
 'CMD_USE_EQUIPMENT_1',
 'CMD_ENGINE_OFF',
 'CMD_ROLL_LEFT',
 'CMD_ROLL_RIGHT',
 'CMD_PITCH_DOWN',
 'CMD_PITCH_UP',
 'CMD_TURN_LEFT',
 'CMD_TURN_RIGHT',
 'CMD_AUTOPILOT',
 'CMD_INC_TARGET_FORCE',
 'CMD_DEC_TARGET_FORCE',
 'CMD_PRIMARY_FIRE',
 'CMD_LAUNCH_ROCKET',
 'CMD_LAUNCH_BOMB',
 'CMD_FIRE_GROUP_1',
 'CMD_FIRE_GROUP_2',
 'CMD_FIRE_GROUP_3',
 'CMD_NORMAL_CAMERA',
 'CMD_FREE_CAMERA_LOCK',
 'CMD_NEXT_TARGET',
 'CMD_LOCK_TARGET',
 'CMD_LOCK_TARGET_IN_SCREEN_CENTER',
 'CMD_INTERMISSION_MENU',
 'CMD_NEXT_TARGET_TEAM_OBJECT',
 'CMD_USE_EQUIPMENT_1',
 'CMD_USE_EQUIPMENT_2',
 'CMD_USE_EQUIPMENT_3',
 'CMD_MINIMAP_ZOOM_IN',
 'CMD_MINIMAP_ZOOM_OUT',
 'CMD_MINIMAP_SIZE_INC',
 'CMD_MINIMAP_SIZE_DEC',
 'CMD_PUSH_TO_TALK',
 'CMD_F2_CHAT_COMMAND',
 'CMD_F6_CHAT_COMMAND',
 'CMD_F3_CHAT_COMMAND',
 'CMD_F4_CHAT_COMMAND',
 'CMD_F5_CHAT_COMMAND',
 'CMD_F7_CHAT_COMMAND',
 'CMD_F8_CHAT_COMMAND']
targetMode = '-1'
files = os.listdir('.')
xmlFiles = ifilter(lambda s: s[-4:] == '.xml', files)
for fileName in xmlFiles:
    with open(fileName) as xmlFile:
        tree = etree.parse(xmlFile)
        root = tree.getroot()
        changed = False
        for cmd in targetCommands:
            for e in root.iterfind('.//' + cmd):
                switchingStyle = e.find('switchingStyle')
                if switchingStyle is not None and switchingStyle.text.strip() != targetMode:
                    switchingStyle.text = targetMode
                    changed = True

    if changed:
        xmlText = etree.tostring(root, pretty_print=True)
        with open(fileName, 'w') as xmlFile:
            xmlFile.write(xmlText)