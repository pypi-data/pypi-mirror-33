
import os
import unittest

sTestDirPath = os.path.dirname(__file__)

with open(os.path.join(sTestDirPath, 't1_expected_output.uml')) as oFile:
    lT1_expected_output = oFile.readlines()

with open(os.path.join(sTestDirPath, 't2_expected_output.uml')) as oFile:
    lT2_expected_output = oFile.readlines()

with open(os.path.join(sTestDirPath, 't3_expected_output.uml')) as oFile:
    lT3_expected_output = oFile.readlines()

with open(os.path.join(sTestDirPath, 't4_expected_output.uml')) as oFile:
    lT4_expected_output = oFile.readlines()


class testDeSequencer(unittest.TestCase):

    def test_trace_T1(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't1_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't1_actual_output.uml'))
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sTestDirPath + '/example.json -tn T1 -uf ' + sTestDirPath + '/t1_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't1_actual_output.uml')) as oFile:
            lT1_actual_output = oFile.readlines()
        self.assertEqual(lT1_expected_output, lT1_actual_output)

    def test_trace_T2(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't2_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't2_actual_output.uml'))
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sTestDirPath + '/example.json -tn T2 -uf ' + sTestDirPath + '/t2_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't2_actual_output.uml')) as oFile:
            lT2_actual_output = oFile.readlines()
        self.assertEqual(lT2_expected_output, lT2_actual_output)

    def test_trace_T3(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't3_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't3_actual_output.uml'))
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sTestDirPath + '/example.json -tn T3 -uf ' + sTestDirPath + '/t3_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't3_actual_output.uml')) as oFile:
            lT3_actual_output = oFile.readlines()
        self.assertEqual(lT3_expected_output, lT3_actual_output)

    def test_trace_T4(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't4_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't4_actual_output.uml'))
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sTestDirPath + '/example.json -tn T4 -uf ' + sTestDirPath + '/t4_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't4_actual_output.uml')) as oFile:
            lT4_actual_output = oFile.readlines()
        self.assertEqual(lT4_expected_output, lT4_actual_output)

    def test_merge_T1(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't1_merge_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't1_merge_actual_output.uml'))
        sFilenames = sTestDirPath + '/example.merge.1.json ' + sTestDirPath + '/example.merge.2.json ' + sTestDirPath + '/example.merge.3.json'
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sFilenames + ' -tn T1 -uf ' + sTestDirPath + '/t1_merge_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't1_merge_actual_output.uml')) as oFile:
            lT1_actual_output = oFile.readlines()
        self.assertEqual(lT1_expected_output, lT1_actual_output)

    def test_merge_T2(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't2_merge_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't2_merge_actual_output.uml'))
        sFilenames = sTestDirPath + '/example.merge.1.json ' + sTestDirPath + '/example.merge.2.json ' + sTestDirPath + '/example.merge.3.json'
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sFilenames + ' -tn T2 -uf ' + sTestDirPath + '/t2_merge_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't2_merge_actual_output.uml')) as oFile:
            lT2_actual_output = oFile.readlines()
        self.assertEqual(lT2_expected_output, lT2_actual_output)

    def test_merge_T3(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't3_merge_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't3_merge_actual_output.uml'))
        sFilenames = sTestDirPath + '/example.merge.1.json ' + sTestDirPath + '/example.merge.2.json ' + sTestDirPath + '/example.merge.3.json'
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sFilenames + ' -tn T3 -uf ' + sTestDirPath + '/t3_merge_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't3_merge_actual_output.uml')) as oFile:
            lT3_actual_output = oFile.readlines()
        self.assertEqual(lT3_expected_output, lT3_actual_output)

    def test_merge_T4(self):
        if os.path.isfile(os.path.join(sTestDirPath, 't4_merge_actual_output.uml')):
            os.remove(os.path.join(sTestDirPath, 't4_merge_actual_output.uml'))
        sFilenames = sTestDirPath + '/example.merge.1.json ' + sTestDirPath + '/example.merge.2.json ' + sTestDirPath + '/example.merge.3.json'
        os.system('python ' + sTestDirPath + '/../../../bin/' + 'de_sequencer -tf ' + sFilenames + ' -tn T4 -uf ' + sTestDirPath + '/t4_merge_actual_output.uml')
        with open(os.path.join(sTestDirPath, 't4_merge_actual_output.uml')) as oFile:
            lT4_actual_output = oFile.readlines()
        self.assertEqual(lT4_expected_output, lT4_actual_output)

if __name__ == '__main__':
    unittest.main()
