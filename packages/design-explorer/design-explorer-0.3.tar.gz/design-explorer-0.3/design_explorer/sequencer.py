

def get_participant_subnodes(lNodes):

    lBoxes = []
    for oNode in lNodes:
        if oNode.subNode and oNode.subNode not in lBoxes:
            lBoxes.append(oNode.subNode)

    return lBoxes


def get_participants(oTrace, oNodeList, lEdges):

    lParticipants = []
    for oEdge in lEdges:
        oSourceNode = oNodeList.get_item(oEdge.source)
        oTargetNode = oNodeList.get_item(oEdge.target)
        if oSourceNode not in lParticipants:
            lParticipants.append(oSourceNode)
        if oTargetNode not in lParticipants:
            lParticipants.append(oTargetNode)
    return lParticipants


def create_box_dictionary(lBoxes, lParticipants):

    dBoxes = {}
    for sBox in lBoxes:
        dBoxes[sBox] = []

    for oParticipant in lParticipants:
        if oParticipant.subNode:
            dBoxes[oParticipant.subNode].append(oParticipant.name)
    return dBoxes


def add_participant(lUsedNodes, lDiagram, oParticipant):
    if not oParticipant.subNode:
        lDiagram.append(' '.join(['participant', oParticipant.name]))
        lUsedNodes.append(oParticipant.name)
    return lDiagram


def add_participant_box(lUsedNodes, lDiagram, oParticipant, dBoxes):
    if oParticipant.subNode:
        lDiagram.append('box "' + oParticipant.subNode + '"')
        for sNodeName in dBoxes[oParticipant.subNode]:
            lDiagram.append('  ' + ' '.join(['participant', sNodeName]))
            lUsedNodes.append(sNodeName)
        lDiagram.append('end box')
    return lDiagram


def build_participant_section(lBoxes, lParticipants, lExpandNodes):

    lDiagram = []
    dBoxes = create_box_dictionary(lBoxes, lParticipants)

    lUsedNodes = []
    for oParticipant in lParticipants:
        if oParticipant.name not in lUsedNodes and oParticipant.name not in lExpandNodes:
            lDiagram = add_participant(lUsedNodes, lDiagram, oParticipant)
            lDiagram = add_participant_box(lUsedNodes, lDiagram, oParticipant, dBoxes)

    lDiagram.append('')
    return lDiagram


def build_sequence_section(lEdges):

    lDiagram = []
    for oEdge in lEdges:
        lDiagram.append(' '.join([oEdge.source, '->', oEdge.target, ':', oEdge.interface]))
    return lDiagram


def create_plantuml_sequence_diagram(oTrace, oNodeList, lExpandNodes):

    lDiagram = ['@startuml']
    lDiagram.append('')

    if lExpandNodes:
        lExpandNodes = lExpandNodes
    else:
        lExpandNodes = []

    lEdges = oTrace.get_expanded_path()

    lParticipants = get_participants(oTrace, oNodeList, lEdges)

    lBoxes = get_participant_subnodes(lParticipants)

    lDiagram.extend(build_participant_section(lBoxes, lParticipants, lExpandNodes))

    lDiagram.extend(build_sequence_section(lEdges))

    lDiagram.append('')
    lDiagram.append('@enduml')
    return lDiagram
