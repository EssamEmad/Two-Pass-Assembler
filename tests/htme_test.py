import unittest
from sys import path
from os.path import dirname, abspath

path.append(dirname(dirname(abspath(__file__))))
from hte import HTMEGenerator


class HTMEGeneratorTests(unittest.TestCase):

    def test_normal_case(self):
        htme_generator = HTMEGenerator('prog', '100000', '1F')
        for _ in range(30):
            htme_generator.add_text_record('00')
        # Check that the new record was generated
        self.assertEqual(len(htme_generator.text_records_pool), 1)
        expected_text_record = "{}{}{}{}".format('T','100000','1e',"00"*30)
        self.assertEqual(htme_generator.text_records_pool[0], expected_text_record)

        # add new object code
        htme_generator.add_text_record('00')
        self.assertEqual(htme_generator.text_record_staging[0], 1)

    def test_no_enough_space(self):
        """
        Add 28 bytes to the staging pool meaning that only 2 bytes are left
        Add 4 bytes object code and check for the expected behaviour
        """
        htme_generator = HTMEGenerator('prog', '100000', '1F')

        for _ in range(28):
            htme_generator.add_text_record('00')
        self.assertEqual(htme_generator.text_record_staging[0], 28)

        htme_generator.add_text_record("11"*4)
        self.assertEqual(len(htme_generator.text_records_pool), 1)
        expected_text_record = "{}{}{}{}{}".format('T', '100000', '1e', "00" * 28, '11'*2)
        self.assertEqual(htme_generator.text_records_pool[0], expected_text_record)

        self.assertEqual(htme_generator.text_record_staging[0], 2)
        self.assertEqual(htme_generator.text_record_staging[1], '11'*2)

    def test_mod_records(self):
        htme_generator = HTMEGenerator('prog', '100000', '1F')
        htme_generator.add_modification_record("100001", 5)
        expected_mod_record = "{}{}{}".format("M", '100001', '05')
        self.assertEqual(htme_generator.mod_records[0], expected_mod_record)

    def test_start_address(self):
        htme_generator = HTMEGenerator('prog', '100000', '1F')
        for _ in range(31):
            htme_generator.add_text_record('00')
        htme_generator.output_records('100000', 'output')
        expected_output = ['Hprog 1000001F', 'T1000001e000000000000000000000000000000000000000000000000000000000000',
                           'T10001e0100', 'E100000']

        f = open('output', 'r')
        for index, line in enumerate(f):
            self.assertEqual(line.strip(), expected_output[index])
        f.close()

if __name__ == '__main__':
    unittest.main(exit=False)