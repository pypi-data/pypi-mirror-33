import copy


def append_to_list(lList, item):
    try:
        lList.append(item)
    except AttributeError:
        lList = [item]
    return lList


class base_list():

    def __init__(self):
        self.lItems = None

    def add_item(self, oItem):
        self.lItems = append_to_list(self.lItems, oItem)

    def get_item(self, sItemName):
        for oItem in self.lItems:
            if oItem.name == sItemName:
                return oItem
        return None


class node_list(base_list):

    def __init__(self):
        base_list.__init__(self)

    def get_subnodes_of_node(self, sSubNodeName):
        lNodes = None
        for oNode in self.lItems:
            if oNode.subNode == sSubNodeName:
                lNodes = append_to_list(lNodes, oNode)
        return lNodes


class node():

    def __init__(self, name=None, subNode=None):
        self.name = name
        self.subNode = subNode


class edge():

    def __init__(self, source=None, target=None, name=None, sInterface=None):
        self.source = source
        self.target = target
        self.name = name
        self.interface = sInterface


class edge_list(base_list):

    def __init__(self):
        base_list.__init__(self)

    def get_edges_of_node(self, sNodeName):
        lEdges = None
        for oEdge in self.lItems:
            if oEdge.source == sNodeName:
                lEdges = append_to_list(lEdges, oEdge)
        return lEdges


class trace():

    def __init__(self, sName):
        self.name = sName
        self.path = None

    def add_to_path(self, oEdge):
        self.path = append_to_list(self.path, oEdge)

    def get_expanded_path(self):

        lExpandedPath = []

        for oPath in self.path:
            if isinstance(oPath, edge):
                lExpandedPath.append(oPath)
            elif isinstance(oPath, trace):
                lTracePath = oPath.get_expanded_path()
                lExpandedPath.extend(lTracePath)

        return lExpandedPath


def merge_two_edges(oEdge1, oEdge2):
    if oEdge1.target == oEdge2.source:
        oNewEdge = copy.deepcopy(oEdge1)
        oNewEdge.target = oEdge2.target
        return oNewEdge
    return Edge1


def remove_expanded_nodes_from_path(lTracePath, lExpandNodes, oNodeList):
    lNewPath = []

    for oEdge in lTracePath:
#        print oEdge.source + ':' + oEdge.target + ':' + oEdge.
        if oEdge.target in lExpandNodes:
            if oEdge.target == oEdge.subNode:
                print 'Modify this edge'
            else:
                print 'Remove this edge'
        else:
            print 'Keep this edge'


#def remove_expanded_nodes_from_path(lTracePath, lExpandNodes, oNodeList):
#
#    lNewPath = []
#    fSkipIndex = False
#    for iIndex in range(0, len(lTracePath) - 1):
#        print lTracePath[iIndex].source + '\t' + lTracePath[iIndex].target
#        if fSkipIndex:
#            fSkipIndex = False
#            continue
#        print '    ' + lTracePath[iIndex].source + '\t' + lTracePath[iIndex].target
#        oEdge1Target = lTracePath[iIndex].target
#        oEdge2Source = lTracePath[iIndex + 1].source
#        oEdge2Target = lTracePath[iIndex + 1].target
#        if oNodeList.get_item(oEdge2Target).subNode:
#            if not oEdge1Target == oNodeList.get_item(oEdge2Target).subNode:
#                lNewPath.append(lTracePath[iIndex])
#            else:
#                lNewPath.append(merge_two_edges(lTracePath[iIndex], lTracePath[iIndex + 1]))
#                fSkipIndex = True
#        else:
#            lNewPath.append(lTracePath[iIndex])
#
#
#    return lNewPath

def get_node_from_system(dSystem, sNodeName):

    lNodeName = sNodeName.split('.')
    if len(lNodeName) > 1:
        sSubNodeName = get_node_from_system(dSystem[lNodeName[0]], '.'.join(lNodeName[1:]))
    else:
        sSubNodeName = dSystem[sNodeName]

    return sSubNodeName
