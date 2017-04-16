import math

class HTMEGenerator:
    """
    This class is responsible of creating and keeping track of records
    and output the hte records

    Methods
    -----------------

    __init__(name: str, starting_address: string, size_in_bytes: int)
    add_text_record(object_code:string) -> Void
    add_modification_record(start_address, no_of_half_bytes) -> Void
    output_records(address_of_the_first_executable:string, output_file_name:string) -> Bool
    """

    def __init__(self, name, starting_address, size_in_bytes):
        """
        Initialize the HTME Generator, makes the head record

        NOTE: if the name of the program is less than 6 it will be appended with
        spaces

        NOTE: starting address and size_in_bytes both MUST BE STRING (i.e. NO '0x' at the start)
        but the value should be a hex number (base 16)

        :param name: the program name
        :param starting_address: starting address of the program in memeory
        :param size_in_bytes: size of the program in bytes
        """
        if len(name) < 6:
          name = name + " "*(6 - len(name))
        self.head_record = "{}{}{}{}".format('H', name[:5], starting_address, size_in_bytes)
        self.starting_address_hex = starting_address
        """
        stage object code until the size is greater than 30 or the output is required
        the first element of the text_record_staging is the size of the staged records
        """
        self.text_record_staging = [0]
        # pool of ready to output text records
        self.text_records_pool = []

        # pool of modification records
        self.mod_records = []

    def update_starting_address(self, address):
        """
        Update the starting_address to the given address

        NOTE: the address should be in hex but with no '0x' at the start (not necessary)

        :address: to be updated to
        :return: None
        """
        self.starting_address_hex = address

    def add_text_record(self, object_code):
        """
        takes an object code as a string (i.e. no '0x') and add it to a text record
        :param object_code: string
        :return: None
        """
        size_of_object_code = math.ceil(len(object_code) / 2)
        if size_of_object_code + self.text_record_staging[0] > 30:
            # if there's no available space to all bytes in the object code
            # get the remainjng number of hex
            remaining_size_hex = (30 - self.text_record_staging[0]) * 2

            # add this slice to the text record
            self.text_record_staging.append(object_code[:remaining_size_hex])
            self.text_record_staging[0] = 30
            self.generate_and_reset()

            # reset the text_record_staging and call add_text_record on the remaining
            # slice of the object code
            self.add_text_record(object_code[remaining_size_hex:])
        else:
            self.text_record_staging[0] += size_of_object_code
            self.text_record_staging.append(object_code)
        
        if self.text_record_staging[0] == 30:
            self.generate_and_reset()

    def generate_and_reset(self):
        """
        Outside of the generator:
        -------------------------
        call when you want to stop the current text record and start
        a new one.
        you may want to use update_current_address() to update the start_address of the
        new record to be added.

        From inside of the generator:
        ------------------
        When the size of the text_record_staging is 30 or at the end of the program:
        Generate the text record, and add it the text_record_pool
        reset the text_record_staging

        :return: None
        """
        obj_codes = "".join(self.text_record_staging[1::])

        size = hex(self.text_record_staging[0])
        size_to_write = format(self.text_record_staging[0], '02x')

        text_record = "{}{}{}{}".format('T', self.starting_address_hex, size_to_write, obj_codes)
        self.text_records_pool.append(text_record)

        # update the starting address to reflect the size of the last text record
        starting_address_int = int(self.starting_address_hex, 16)
        starting_address_int += int(size, 16)
        self.starting_address_hex = format(starting_address_int, '06x')

        self.text_record_staging = [0]

    def add_modification_record(self, start_address, no_of_half_bytes):
        """
        Add a modification record.

        NOTE: start_address should be a hex number
        NOTE: start_address should be of the first half byte to edit

        :param start_address: hex address of the first half byte to be modified
        :param no_of_half_bytes: Number of half bytes (int)
        :return: None
        """
        start_address = format(int(start_address, 16), '06x')
        no_of_half_bytes = format(no_of_half_bytes, '02x')
        self.mod_records.append("{}{}{}".format('M', start_address, no_of_half_bytes))

    def output_records(self, address, file_name):
        """
        output the htme records to the file given by file_name

        NOTE: the start address MUST BE a string or an int but with no '0x' at the start

        :param address: the start address of the program
        :param file_name: dir or file name
        :return: None
        """
        f = open(file_name, 'w')
        end_record = "E{}".format(address)

        # check if there's any records in the pool
        if self.text_record_staging[0]:
            self.generate_and_reset()

        f.write(self.head_record)
        f.write("\n")

        for record in self.text_records_pool:
            f.write(record)
            f.write("\n")

        for mrecord in self.mod_records:
            f.write(mrecord)
            f.write("\n")

        f.write(end_record)

        print("RECORDS BUILT SUCCESSFULLY AT: ", file_name)

        f.close()

def main():
    HTME = HTMEGenerator('hell', '325444', '00001f')
    for _ in range(0, 31):
        HTME.add_text_record('00')
    HTME.add_modification_record('0x325445', 5)
    HTME.output_records('325444', 'output_test')

if __name__ == '__main__':
    main()