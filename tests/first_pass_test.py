import two_pass_assembler as tpa
import unittest


class FirstPassTest(unittest.TestCase):

    def test_load_instructions(self):
        """
        Test the load instructions functions
        """
        assembler = tpa.TwoPassAssembler('progtest', 'progtest')
        self.assertEqual(len(assembler.inst_table.keys()), 58)
        self.assertEqual(assembler.inst_table['RSUB'], [[3,4], '4C'])
