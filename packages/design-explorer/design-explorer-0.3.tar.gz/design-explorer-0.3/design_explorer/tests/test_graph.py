
import unittest
from design_explorer import graph


class testGraph(unittest.TestCase):

    def test_node_class_attributes_exist(self):
        oNode = graph.node()
        self.assertEqual(oNode.name, None)
        self.assertEqual(oNode.subNode, None)

    def test_node_class_parameters(self):
        oNode = graph.node('name', 'subNode')
        self.assertEqual(oNode.name, 'name')
        self.assertEqual(oNode.subNode, 'subNode')

    def test_edge_class_attributes_exist(self):
        oEdge = graph.edge()
        self.assertEqual(oEdge.source, None)
        self.assertEqual(oEdge.target, None)
        self.assertEqual(oEdge.name, None)
        self.assertEqual(oEdge.interface, None)

    def test_edge_class_parameters(self):
        oEdge = graph.edge('source', 'target', 'name', 'interface')
        self.assertEqual(oEdge.source, 'source')
        self.assertEqual(oEdge.target, 'target')
        self.assertEqual(oEdge.name, 'name')
        self.assertEqual(oEdge.interface, 'interface')

    def test_trace_class_exists(self):
        oTrace = graph.trace('T1')
        self.assertEqual(oTrace.path, None)
        self.assertEqual(oTrace.name, 'T1')

    def test_trace_add_edge(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        self.assertEqual(oTrace.path[0].source, 'S1')
        self.assertEqual(oTrace.path[1].source, 'S2')
        self.assertEqual(oTrace.path[2].source, 'S3')

    def test_trace_expand_path_with_only_edges(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        lEdges = oTrace.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S1')
        self.assertEqual(lEdges[1].source, 'S2')
        self.assertEqual(lEdges[2].source, 'S3')

    def test_trace_expand_path_with_only_traces(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        oTrace1 = graph.trace('T2')
        oTrace1.add_to_path(oTrace)
        lEdges = oTrace1.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S1')
        self.assertEqual(lEdges[1].source, 'S2')
        self.assertEqual(lEdges[2].source, 'S3')

    def test_trace_expand_path_with_only_traces_and_edges(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        oTrace1 = graph.trace('T2')
        oTrace1.add_to_path(oTrace)
        oTrace1.add_to_path(graph.edge('S4', 'T4', 'N4'))
        oTrace1.add_to_path(graph.edge('S5', 'T5', 'N5'))
        lEdges = oTrace1.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S1')
        self.assertEqual(lEdges[1].source, 'S2')
        self.assertEqual(lEdges[2].source, 'S3')
        self.assertEqual(lEdges[3].source, 'S4')
        self.assertEqual(lEdges[4].source, 'S5')

    def test_trace_expand_path_with_nested_traces(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        oTrace1 = graph.trace('T2')
        oTrace1.add_to_path(oTrace)
        oTrace1.add_to_path(graph.edge('S4', 'T4', 'N4'))
        oTrace1.add_to_path(graph.edge('S5', 'T5', 'N5'))
        oTrace2 = graph.trace('T3')
        oTrace2.add_to_path(graph.edge('S6', 'T6', 'N6'))
        oTrace2.add_to_path(oTrace1)
        lEdges = oTrace2.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S6')
        self.assertEqual(lEdges[1].source, 'S1')
        self.assertEqual(lEdges[2].source, 'S2')
        self.assertEqual(lEdges[3].source, 'S3')
        self.assertEqual(lEdges[4].source, 'S4')
        self.assertEqual(lEdges[5].source, 'S5')

    def test_base_list_class_attributes_exist(self):
        oNodeList = graph.base_list()
        self.assertEqual(oNodeList.lItems, None)

    def test_base_list_method_add_item(self):
        oNodeList = graph.base_list()
        oNodeList.add_item(graph.node('N1'))
        oNodeList.add_item(graph.node('N2'))
        oNodeList.add_item(graph.node('N3'))
        self.assertEqual(oNodeList.lItems[0].name, 'N1')
        self.assertEqual(oNodeList.lItems[1].name, 'N2')
        self.assertEqual(oNodeList.lItems[2].name, 'N3')

    def test_base_list_method_get_item(self):
        oNodeList = graph.base_list()
        oNodeList.add_item(graph.node('N1'))
        oNodeList.add_item(graph.node('N2'))
        oNodeList.add_item(graph.node('N3'))
        self.assertEqual(oNodeList.get_item('N1').name, 'N1')
        self.assertEqual(oNodeList.get_item('N2').name, 'N2')
        self.assertEqual(oNodeList.get_item('N3').name, 'N3')
        self.assertEqual(oNodeList.get_item('N564'), None)

    def test_node_list_class_attributes_exist(self):
        oNodeList = graph.node_list()
        self.assertEqual(oNodeList.lItems, None)

    def test_node_list_method_get_subnodes_of_node(self):
        oNodeList = graph.node_list()
        oNodeList.add_item(graph.node('N1', 'S1'))
        oNodeList.add_item(graph.node('N2', 'S1'))
        oNodeList.add_item(graph.node('N3', 'S2'))
        lSubNodes = oNodeList.get_subnodes_of_node('S1')
        self.assertEqual(lSubNodes[0].name, 'N1')
        self.assertEqual(lSubNodes[1].name, 'N2')
        lSubNodes = oNodeList.get_subnodes_of_node('S2')
        self.assertEqual(lSubNodes[0].name, 'N3')
        self.assertEqual(oNodeList.get_subnodes_of_node('N564'), None)

    def test_edge_list_class_attributes_exist(self):
        oEdgeList = graph.edge_list()
        self.assertEqual(oEdgeList.lItems, None)

    def test_edge_list_class_method_get_edges_of_node(self):
        oEdgeList = graph.edge_list()
        oEdgeList.add_item(graph.edge('S1', 'T1', 'N1', 'I1'))
        oEdgeList.add_item(graph.edge('S2', 'T2', 'N2', 'I2'))
        oEdgeList.add_item(graph.edge('S3', 'T3', 'N3', 'I3'))
        oEdgeList.add_item(graph.edge('S3', 'T4', 'N3', 'I4'))
        oEdgeList.add_item(graph.edge('S3', 'T5', 'N3', 'I5'))
        oEdgeList.add_item(graph.edge('S3', 'T6', 'N3', 'I6'))

        lNodeList = oEdgeList.get_edges_of_node('S1')
        self.assertEqual(lNodeList[0].interface, 'I1')

        lNodeList = oEdgeList.get_edges_of_node('S3')
        self.assertEqual(lNodeList[0].interface, 'I3')
        self.assertEqual(lNodeList[1].interface, 'I4')
        self.assertEqual(lNodeList[2].interface, 'I5')
        self.assertEqual(lNodeList[3].interface, 'I6')

    def test_merge_two_edges(self):
        oEdge1 = graph.edge('S1', 'T1', 'N1', 'I1')
        oEdge2 = graph.edge('T1', 'T2', 'N2', 'I2')
        oExpectedEdge = graph.edge('S1', 'T2', 'N1', 'I1')
        oActualEdge = graph.merge_two_edges(oEdge1, oEdge2)
        self.assertEqual(oExpectedEdge.source, oActualEdge.source)
        self.assertEqual(oExpectedEdge.target, oActualEdge.target)
        self.assertEqual(oExpectedEdge.name, oActualEdge.name)
        self.assertEqual(oExpectedEdge.interface, oActualEdge.interface)

#    def test_remove_expanded_nodes_from_path(self):
#        lExpandNodes = ['N2']
#        oNodeList = graph.base_list()
#        oNodeList.add_item(graph.node('N1'))
#        oNodeList.add_item(graph.node('N2'))
#        oNodeList.add_item(graph.node('N3'))
#        oNodeList.add_item(graph.node('SN1', 'N2'))
#        oNodeList.add_item(graph.node('SN2', 'N2'))
#        oTrace = graph.trace('T1')
#        oTrace.add_to_path(graph.edge('N1', 'N2', 'E1', 'I1'))
#        oTrace.add_to_path(graph.edge('N2', 'SN1', 'SE1', 'SI1'))
#        oTrace.add_to_path(graph.edge('SN1', 'SN2', 'SE4', 'SI2'))
#        oTrace.add_to_path(graph.edge('SN2', 'N2', 'SE5', 'SI3'))
#        oTrace.add_to_path(graph.edge('N2', 'N3', 'E2', 'I2'))
#        lPath = oTrace.get_expanded_path()
#        self.assertEqual(lPath[0].source, 'N1')
#        self.assertEqual(lPath[1].source, 'N2')
#        self.assertEqual(lPath[2].source, 'SN1')
#        self.assertEqual(lPath[3].source, 'SN2')
#        self.assertEqual(lPath[4].source, 'N2')
#        lNewEdges = graph.remove_expanded_nodes_from_path(lPath, lExpandNodes, oNodeList)
#        self.assertEqual(lNewEdges[0].source, 'N1')
#        self.assertEqual(lNewEdges[0].target, 'SN1')
#        self.assertEqual(lNewEdges[1].source, 'SN1')
#        self.assertEqual(lNewEdges[1].target, 'SN2')
#        self.assertEqual(lNewEdges[2].source, 'SN2')
#        self.assertEqual(lNewEdges[2].target, 'N3')

    def test_system_dictionary(self):
        dSystem = {}
        dSystem['H1'] = 'Host1'
        dSystem['FPGA'] = {}
        dSystem['FPGA']['U1'] = 'Block1'
        dSystem['FPGA']['U2'] = 'Block2'
        dSystem['FPGA']['U3'] = {}
        dSystem['FPGA']['U3']['SU1'] = 'Sub Block 1'
        dSystem['H2'] = 'Host2'
        self.assertEqual(graph.get_node_from_system(dSystem, 'H1'), 'Host1')
        self.assertEqual(graph.get_node_from_system(dSystem, 'H2'), 'Host2')
        self.assertEqual(graph.get_node_from_system(dSystem, 'FPGA.U1'), 'Block1')
        self.assertEqual(graph.get_node_from_system(dSystem, 'FPGA.U2'), 'Block2')
        self.assertEqual(graph.get_node_from_system(dSystem, 'FPGA.U3.SU1'), 'Sub Block 1')


if __name__ == '__main__':
    unittest.main()
