import unittest
from itertools import zip_longest
from sys import path
from os.path import dirname, abspath

path.append(dirname(dirname(abspath(__file__))))

import Second_Pass as sp
import two_pass_assembler as tpa


class Second_Pass_Tests(unittest.TestCase):

    def test_second_pass_trivial(self):
        first_pass = tpa.TwoPassAssembler('CODE.txt','progtest')
        lines = first_pass.first_pass()
        second_pass = sp.Second_Pass(lines,first_pass.inst_table, first_pass.symbol_table)
        print(second_pass.second_pass())

if __name__ == '__main__':
    unittest.main(exit=False)
