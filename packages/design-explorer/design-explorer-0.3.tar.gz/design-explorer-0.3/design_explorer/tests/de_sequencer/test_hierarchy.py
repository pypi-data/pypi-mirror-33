
import os
import unittest

sTestDirPath = os.path.dirname(__file__)

with open(os.path.join(sTestDirPath, 't1_hierarchy_expected_output.uml')) as oFile:
    lT1_expected_output = oFile.readlines()

with open(os.path.join(sTestDirPath, 't3_hierarchy_expected_output.uml')) as oFile:
    lT3_expected_output = oFile.readlines()

class testDeSequencer(unittest.TestCase):

    def test_trace_T1(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't1_hierarchy_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't1_hierarchy_actual_output.uml'))
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sTestDirPath + '/example.hierarchy.json -tn T1 -uf ' + sTestDirPath + '/t1_hierarchy_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't1_hierarchy_actual_output.uml')) as oFile:
            lT1_actual_output = oFile.readlines()
        self.assertEqual(lT1_expected_output, lT1_actual_output)

#    def test_trace_T3(self):
#        if os.path.isfile(os.path.join(sTestDirPath, 't3_hierarchy_actual_output.uml')):
#            os.remove(os.path.join(sTestDirPath, 't3_hierarchy_actual_output.uml'))
#        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sTestDirPath + '/example.hierarchy.json -tn T3 -uf ' + sTestDirPath + '/t3_hierarchy_actual_output.uml --expand N2')
#        with open(os.path.join(sTestDirPath, 't3_hierarchy_actual_output.uml')) as oFile:
#            lT3_actual_output = oFile.readlines()
#        self.assertEqual(lT3_expected_output, lT3_actual_output)


if __name__ == '__main__':
    unittest.main()
