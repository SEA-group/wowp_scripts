# Embedded file name: scripts/common/GameEventsCommon/helpers/core.py
import types
import sys
import functools
import weakref

def fastDeepCopy(obj):
    import msgpack
    return msgpack.unpackb(msgpack.packb(obj))


def weakRefProxy(obj):
    if obj is None:
        return obj
    elif type(obj) in weakref.ProxyTypes:
        return obj
    else:
        return weakref.proxy(obj)


def objToDict(obj):
    """
    Recursively replace all instances with dicts.
    :param obj: instance to convert
    :rtype: dict
    """
    if isinstance(obj, dict):
        return {k:objToDict(v) for k, v in obj.iteritems()}
    elif isinstance(obj, (list, tuple, set)):
        return type(obj)((objToDict(v) for v in obj))
    elif hasattr(obj, '__dict__'):
        return objToDict(obj.__dict__)
    elif hasattr(obj, '__slots__'):
        return {k:objToDict(getattr(obj, k)) for k in obj.__slots__}
    else:
        return obj


class _Dummy(object):
    pass


def dictToObj(dict_):
    """
    Recursively replaces all dicts with objects.
    :type dict_: dict
    :rtype: object
    """
    if isinstance(dict_, dict):
        obj = _Dummy()
        obj.__dict__ = {k:dictToObj(v) for k, v in dict_.iteritems()}
        return obj
    if isinstance(dict_, (list, tuple, set)):
        return type(dict_)((dictToObj(v) for v in dict_))
    return dict_


def convertObjToDict(obj, attrs = (), default = None):
    """Convert object to dict by given attrs, and if not finded deault value"""
    if not obj:
        return
    return {key:getattr(obj, key, default) for key in attrs}


def convertObjToDictIncludeContext(obj, name = '', listOnly = (), asDicts = (), level = 0):
    name = name.strip('_')
    level += 1
    if isinstance(obj, (types.InstanceType, _Dummy)):
        value = None
        for innerName, item in obj.__dict__.iteritems():
            innerName = innerName.strip('_')
            item = convertObjToDictIncludeContext(item, innerName, listOnly, asDicts, level)
            if isinstance(item, list) and not item:
                continue
            if innerName in asDicts and level > 2:
                if value is None:
                    value = []
                item = [item] if not isinstance(item, list) else item
                if item:
                    value = item + value
            else:
                if value is None:
                    value = {}
                value[innerName] = item
                if 'value' in value and 'context' in value:
                    value.update({'context': value.pop('context'),
                     'value': value.pop('value')})

        obj = value
    elif isinstance(obj, (list, tuple)):
        value = []
        for index, item in enumerate(obj):
            item = convertObjToDictIncludeContext(item, name, listOnly, asDicts, level)
            if item is not None:
                if name in asDicts and level > 2:
                    value.append({name: item})
                elif level >= 2:
                    value.append(item)

        if len(value) == 1 and name not in listOnly:
            value = value[0]
        obj = value
    elif isinstance(obj, str) and name == 'context':
        obj = '.{}'.format(obj)
    return obj


def incrementCountInNestedDict(current, diff):
    """Increments all values in current dict by provided diff"""
    for key, value in diff.iteritems():
        if isinstance(value, dict):
            incrementCountInNestedDict(current.setdefault(key, {}), value)
        else:
            current[key] = current.get(key, 0) + value


def updateNestedDict(current, diff):
    """Updates nested dict"""
    for key, value in diff.iteritems():
        if isinstance(value, dict):
            if key not in current or current[key] is None:
                current[key] = {}
            updateNestedDict(current[key], value)
        else:
            current[key] = value

    return


def getItemByPath(result, path, default = None):
    for key in path:
        if key is None:
            continue
        result = result.get(key, None)
        if result is None:
            return default

    return result


def getattrByPath(result, path, default = None):
    for key in path:
        if key is None:
            continue
        result = getattr(result, key, None)
        if result is None:
            return default

    return result


def setItemByPath(result, path, value, overwrite = True):
    path = [ key for key in path if key is not None ]
    lastIndex = len(path) - 1
    for index, key in enumerate(path):
        if index != lastIndex:
            result = result.setdefault(key, {})
        elif overwrite:
            result[key] = value
            result = value
        else:
            result = result.setdefault(key, value)

    return result