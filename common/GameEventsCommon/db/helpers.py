# Embedded file name: scripts/common/GameEventsCommon/db/helpers.py


class Dummy:
    pass


NO_CACHED_VALUE = -9999999999999999989L

def filterByAttrsAndValues(objects, attrs):
    """Yield object only if attributes equal to given values"""
    for obj in objects:
        valid = True
        for prop, value in attrs.iteritems():
            try:
                if value == getattr(obj, prop):
                    continue
            except AttributeError:
                pass

            valid = False

        if valid:
            yield obj


def findInindex(indexes, attrs):
    """Find objects by searching in indexes dict"""
    return set((obj for prop, value in attrs.iteritems() for obj in indexes.get(prop, {}).get(value, ())))


def findHasAttrs(indexes, items, attrs):
    for attr in attrs:
        indexItems = indexes.get(attr, [])
        if isinstance(indexItems, dict):
            indexItems = indexItems.itervalues()
        for result in indexItems:
            for item in result:
                yield item

        if not indexItems:
            filteredItems = set((item for item in items if hasattr(item, attr)))
            for item in filteredItems:
                yield item


def setInDummyInstance(obj, header):
    """Set objects by given header"""
    for name, toMerge in header.__dict__.iteritems():
        if isinstance(toMerge, (list, tuple)):
            if not toMerge:
                continue
            if not hasattr(obj, name):
                continue
            obj = getattr(obj, name)
            for item in toMerge:
                if hasattr(item, '__dict__'):
                    for inerItem in obj:
                        setInDummyInstance(inerItem, item)

                elif item not in obj:
                    obj.append(item)

        elif hasattr(toMerge, '__dict__'):
            if not hasattr(obj, name):
                setattr(obj, name, toMerge)
            else:
                setInDummyInstance(getattr(obj, name), toMerge)
        elif not hasattr(obj, name):
            setattr(obj, name, toMerge)


def addToDummyInstance(obj, header, skipName):
    """Add obj objects by given header"""
    for name, toAdd in header.__dict__.iteritems():
        if isinstance(toAdd, (list, tuple)):
            if not toAdd:
                continue
            if not hasattr(obj, name):
                setattr(obj, name, [])
            newobj = getattr(obj, name)
            for innerItem in toAdd:
                newobj.append(innerItem)

        elif hasattr(toAdd, '__dict__'):
            if skipName in toAdd.__dict__:
                item = getattr(toAdd, skipName)[0]
                for inObj in getattr(getattr(obj, name), skipName):
                    addToDummyInstance(inObj, item, skipName)

            elif not hasattr(obj, name):
                setattr(obj, name, toAdd)