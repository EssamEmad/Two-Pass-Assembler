import re
import math


class TwoPassAssembler:
    """
    Two pass assembler simulation
    System Programming Course 2017
    """
    def __init__(self, FILE, output_path, INST_TABLE_FILE = 'instructions.txt'):
        self.FILE = FILE
        self.output_path = output_path
        self.symbol_table = {}
        self.start_address = 0 # default if not changed
        self.INST_TABLE_FILE = INST_TABLE_FILE
        self.inst_table = {}
        if not self.load_instructions(self.INST_TABLE_FILE):
            raise ValueError("error loading instruction")
        self.directive_table = ["START", "END", "BYTE", "WORD", "RESB", "RESW"]

    def load_instructions(self, file_path):
        """
        :param file_path: path the the instruction table file
        :return: bool
        """
        try:
            f = open(file_path, 'r')
        except FileNotFoundError:
            return False

        for line in f:
            parts = re.split(' ',line)
            self.inst_table[parts[0]] = [list(map(int, re.split(',', parts[1]))), parts[2].strip()]
        f.close()
        return True

    def first_pass(self):
        """
        First pass assembler simulation
        Setup the temp file of the same name as the output and with extension .temp
        setup the symbol table
        :return: bool
        """
        f = open(self.FILE, "r")
        temp_file = open(self.FILE + ".temp", 'w+')

        current_address = self.start_address
        for line in f:
            # get parts of the instruction
            parts = TwoPassAssembler.get_parts(line)

            # check if memonic exist
            if not parts['memonic']:
                raise SyntaxError('Memocis must be provided')

            # check if a label exist save it to the symbol table
            if parts['label']:
                self.symbol_table[parts['label']] = current_address

            # print line to the file
            temp_line = "{} {} {} {}\n".format(current_address,
                                                parts['label'] if parts['label'] else '',
                                                parts['memonic'],
                                                str.join(',', parts['operands']))
            temp_file.write(temp_line)

            current_address += self.get_size(parts['memonic'], parts['operands'])

        f.close()
        temp_file.close()


    @staticmethod
    def get_parts(line):
        """ (str) -> dict (str: str)

            get the parts of an instruction input line
            (Label)   menimoic    operands    #comments
            and return a dictionary of their values

            parts {
                'label': label if exist
                'memonic' memoic in the instruction
                'operands': comma seperated operands
                'comments' comments if exist
            }

        """
        current_index = 0
        current = ""
        parts = {}

        for t in line:
            if t == '\t' or t.isspace():
                # save the part collected in the parts hash
                TwoPassAssembler.save_value(current_index, current, parts)
                current_index += 1
                current = ""
            elif t.isalpha():
                current += t
            else:
                if len(current) == 0 and current_index != 2:
                    raise SyntaxError("Insturcations parts must not start with a number")
                else:
                    current += t

        if current != "":
            TwoPassAssembler.save_value(current_index, current, parts)

        if parts['operands']:
            parts['operands'] = list(re.split(',', parts['operands']))

        return parts

    @staticmethod
    def save_value(current_index, current, parts):
        """
        saves the value of the current in the appropirate index
        :param current_index: no of the insturaction part
        :param current: the part
        :param parts: the part dictionary to save value in
        :return: None
        """
        parts["label" if not current_index else
              "memonic" if current_index == 1 else
              "operands" if current_index == 2 else
              "comment"] = current

    def get_size(self, memonic, operands):
        """
        Returns the size of the instruction depending on the instruction format
        and if it's a directive
        :param memonic: the operation memonic
        :param operands: operands of the instruction to decide on format 3 or 4
        :return: int

        >>> self.get_size("BYTE", ["X'F1'"])
        8
        >>> self.get_size("BYTE", ["C'EOF'"])
        24
        """
        # check if the memonic is a instruction in the assember instruction table
        if memonic in self.inst_table:
            # check if the instruction format is 1 or 2
            if self.inst_table[memonic][0] in [1, 2]:
                return self.inst_table[memonic][0]
            else:
                # return size 4 if + which indicates a type 4 instruction
                return 4 if operands[0] == '+' else 3
        elif memonic in self.directive_table:
            # check if the memonic is a directive
            # get the method that has the same name of the memonic and pass it the operands
            return self.__getattribute__(str.lower(memonic))(operands)
        else:
            # memonic is not an instruction or memonic
            raise SyntaxError("Invalid memonic or directive")

    @staticmethod
    def byte(operand):
        """
        Eval the number of bytes needed for the operand of the BYTE directive
        :param operand: the operand of the 'BYTE' directive
        :return: size of the operand in bytes

        >>> TwoPassAssembler.byte("X'F1'")
        1
        >>> TwoPassAssembler.byte("C'EOF'")
        3
        """
        operand = operand[0]
        if operand[0] == 'C':
            return len(operand[2:len(operand) - 1])
        elif operand[0] == 'X':
            return math.ceil(len(operand[2:len(operand) - 1]) / 2)
        else:
            try:
                if int(operand[0]): #TODO
                    return 1
            except ValueError as e:
                raise SyntaxError("Invalid BYTE operand")

    @staticmethod
    def word(operand):
        """
        Return the number of bytes needed to store the directive operand

        :param operand: the operand of the directive
        :return: num of bytes

        >>> TwoPassAssembler.word(4096)
        3
        """
        return 3

    @staticmethod
    def resb(operand):
        return int(operand[0])

    @staticmethod
    def resw(operand):
        return 3*int(operand[0])

    def start(self, operands):
        self.start_address = int(operands[0])
        return 0

    def end(self, operands):
        return 0

if __name__ == '__main__':
    import doctest
    doctest.testmod()