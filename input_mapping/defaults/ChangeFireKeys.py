# Embedded file name: scripts/input_mapping/defaults/ChangeFireKeys.py
import os
from lxml import etree
from itertools import ifilter, izip_longest
targetCommand = 'CMD_TOGGLE_ARENA_VOICE_CHANNEL'
targetKeys = ['KEY_L']
deleteExtraKeysInCommand = False
files = os.listdir('.')
xmlFiles = ifilter(lambda s: s[-4:] == '.xml', files)

def loadXmlFile(fileName):
    root = etree.parse(fileName).getroot()
    return root


def saveXmlFile(xmlRoot, fileName):
    xmlText = etree.tostring(xmlRoot, pretty_print=True)
    with open(fileName, 'w') as f:
        f.write(xmlText)


class eChain(object):

    def __init__(self, elem):
        self.elem = elem

    def append(self, tag):
        self.elem = etree.SubElement(self.elem, tag)
        return self


def main():
    for fileName in xmlFiles:
        root = loadXmlFile(fileName)
        changed = False
        for eCmd in root.iterfind('.//' + targetCommand):
            for eKey, tKey in list(izip_longest(eCmd.iterfind('.//fireKeyName'), targetKeys)):
                if eKey is None:
                    addFireKeyToCommand(eCmd, tKey)
                    changed = True
                    continue
                if tKey is None:
                    if deleteExtraKeysInCommand:
                        removeKeyFromCommand(eCmd, eKey)
                        changed = True
                    continue
                if eKey.text.strip() != tKey:
                    eKey.text = tKey
                    changed = True

        if changed:
            saveXmlFile(root, fileName)

    return


def removeKeyFromCommand(cmdElem, keyElem):
    cmdElem.find('FIRE_KEYS').remove(keyElem.getparent())


def addFireKeyToCommand(cmdElem, keyText):
    eKey = eChain(cmdElem).append('FIRE_KEYS').append('FIRE_KEY').append('fireKeyName').elem
    eKey.text = keyText
    etree.SubElement(eKey.getparent(), 'fireKeyDevice').text = '0'


if __name__ == '__main__':
    main()