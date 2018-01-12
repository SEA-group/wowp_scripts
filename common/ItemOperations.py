# Embedded file name: scripts/common/ItemOperations.py


class Dummy(object):
    """ Description for bundled Dummy object """
    dictItem = ()
    idType = ()
    item = ()


def toDict(dummyDict):
    """ Convert Dummy object bundled from list of <dictItem> XML tags to dict object.
        For tag discription look for itemOperations.xsd.
    """
    return {item.dictKey:item.dictValue for item in dummyDict.dictItem}


def buildIdTypeList(dummyIdTypeList):
    """ Convert Dummy object bundled from <idTypeList> XML tags to list object.
        For tag discription look for itemOperations.xsd.
    """
    return [ [getattr(i, 'itemId', None), i.itemType] for i in dummyIdTypeList.idType ]


def buildItems(dummyItems):
    """ Convert Dummy object bundled from list of <idType> XML tags to list object.
        For tag discription look for itemOperations.xsd.
    """
    res = []
    for item in dummyItems.item:
        ikw = {'type': item.type,
         'idTypeList': buildIdTypeList(item.idTypeList)}
        if hasattr(item, 'count'):
            ikw['count'] = item.count
        if hasattr(item, 'kwargs'):
            ikw['kwargs'] = toDict(item.kwargs)
        if hasattr(item, 'related'):
            ikw['related'] = buildItems(item.related)
        res.append(ikw)

    return res