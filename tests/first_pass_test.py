import two_pass_assembler as tpa
import unittest
from itertools import zip_longest

class FirstPassTest(unittest.TestCase):

    def test_load_instructions(self):
        """
        Test the load instructions functions
        """
        assembler = tpa.TwoPassAssembler('progtest', 'progtest')
        self.assertEqual(len(assembler.inst_table.keys()), 58)
        self.assertEqual(assembler.inst_table['RSUB'], [[3,4], '4C'])

    def test_get_parts(self):
        parts = tpa.TwoPassAssembler.get_parts('COPY\tSTART\t1000,2000')
        self.assertEqual(parts, {'label': 'COPY', 'memonic': 'START', 'operands': ['1000', '2000']})
        parts = tpa.TwoPassAssembler.get_parts('\tLDA\tCOPY,X')
        self.assertEqual(parts, {'label': '', 'memonic': 'LDA', 'operands': ['COPY', 'X']})

    def test_byte(self):
        size = tpa.TwoPassAssembler.byte(["C'HELLO'"])
        self.assertEqual(size, 5)
        size = tpa.TwoPassAssembler.byte(["20"])
        self.assertEqual(size, 1)
        size = tpa.TwoPassAssembler.byte(["X'38f'"])
        self.assertEqual(size, 2)


    def test_first_pass(self):
        assembler = tpa.TwoPassAssembler('progtest', 'progtest')
        assembler.first_pass()
        output = open('progtest.temp', 'r')
        expected = open('progtest-result', 'r')
        for oline, eline in zip_longest(output, expected):
            self.assertEqual(oline, eline)

if __name__ == '__main__':
    unittest.main(exit=False)