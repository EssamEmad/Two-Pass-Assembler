import re
import math


class TwoPassAssembler:
    """
    Two pass assembler simulation
    System Programming Course 2017
    """
    def __init__(self, FILE, output_path, INST_TABLE_FILE = 'inst.txt'):
        self.FILE = FILE
        self.output_path = output_path
        self.symbol_table = {}
        self.start_address = 0 # default if not changed
        self.INST_TABLE_FILE = INST_TABLE_FILE
        if not self.load_instructions(self.INST_TABLE_FILE):
            raise ValueError("error loading instruction")
        self.inst_table = {}
        self.directive_table = {
            "START": 'start',
            "END": 0, # TODO
            "BYTE": 'byte_size',
            "WORD": 'word_size',
            "RESB": 'resb',
            "RESW": 'resw'
        }

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
            parts = re.split(line, ' ')
            self.inst_table[parts[0]] = [parts[1], parts[2]]
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
            temp_line = "{}\t{}\t{}\t{}".format(current_address, parts['label'], parts['memonic'],
                                                str.join(parts[operands], ","))
            temp_file.write(temp_line)

            current_address += self.get_size(parts['memonic'], parts['operands'])

        f.close()


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
            if t == '/t':
                # save the part collected in the parts hash
                TwoPassAssembler.save_value(current_index, current, parts)
                current_index += 1
            elif t.isalpha():
                current += t
            else:
                if len(current) == 0 and current_index != 1:
                    raise SyntaxError("Insturcations parts must not start with a number")
                else:
                    current += t
        parts[operands] = list(re.split(parts['operands'], ','))
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
        if self.inst_table[memonic]:
            # check if the instruction format is 1 or 2
            if self.inst_table[memonic][0] in [1, 2]:
                return self.inst_table[memonic][0]
            else:
                # return size 4 if + which indicates a type 4 instruction
                return 4 if operands[0] == '+' else 3
        elif self.directive_table[memonic]:
            # check if the memonic is a directive
            # if so get the name of the static method that eval the size of the operand
            # and return the evaluation of the method
            return eval("self.{}({})",format(self.directive_table[memonic], operands[0]))
        else:
            # memonic is not an instruction or memonic
            raise SyntaxError("Invalid memonic or directive")


    def byte_size(self, operand):
        """
        Eval the numer of bytes needed for the operand of the BYTE directive
        :param operand: the operand of the 'BYTE' directive
        :return: size of the operand in bytes

        >>> self.byte_size("X'F1'")
        1
        >>> self.byte_size("C'EOF'")
        3
        """
        if operand[0] == 'C':
            return len(operand[2:len(operand) - 1])
        elif operand[0] == 'X':
            return math.ceil(len(operand[2:len(operand) - 1]) / 2)
        else:
            raise SyntaxError("Invalid BYTE operand")


    def word_size(self, operand):
        """
        Return the number of bytes needed to store the directive operand

        :param operand: the operand of the directive
        :return: num of bytes

        >>> self.word_size(4096)
        3
        """
        return 3


    def resb(self, operand):
        return int(operand[0])


    def resw(self, operand):
        return 3*int(operand[0])

    def start(self, operands):
        self.start_address = int(operands[0])


# if __name__ == '__main__':
#     """
#         Testing few functions
#         not working need to start working with files
#     """
#     assert TwoPassAssembler.byte_size("C'EOF'") == 3
#     assert TwoPassAssembler.byte_size("X'F23'") == 2
#     operands = ["C'EOF'"]
#     memonic = "BYTE"
#     directive_table = {
#         "START": 0,  # TODO
#         "END": 0,  # TODO
#         "BYTE": 'byte_size',
#         "WORD": 'word_size',
#         "RESB": 'resb',
#         "RESW": 'resw'
#     }
#
#     for operands in [["C'EOF'"], ["X'F1'"]]:
#         exp = "TwoPassAssembler.{}(\"{}\")".format(directive_table[memonic], operands[0])
#         size = eval(exp)
#         print(size)
#
#     operands = ['3']
#     for memonic in ["RESB", "RESW"]:
#         exp = "TwoPassAssembler.{}(\"{}\")".format(directive_table[memonic], operands[0])
#         size = eval(exp)
#         print(size)