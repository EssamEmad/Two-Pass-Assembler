import re
import math
import sys, os
sys.path.append(os.path.realpath(__file__))
from Assembly_Line import Assembly_Line

class TwoPassAssembler:
    """
    Two pass assembler simulation
    System Programming Course 2017
    """
    def __init__(self, FILE, output_path, INST_TABLE_FILE = 'instructions.txt'):
        self.FILE = FILE
        self.output_path = output_path
        self.symbol_table = {}
        self.symbol_table_en = {}
        self.control_section = 0 # default control section
        self.external_refs = [] # a list of external refs for each CSECT
        self.external_defs = []
        self.start_address = 0 # default if not changed
        self.INST_TABLE_FILE = INST_TABLE_FILE
        self.inst_table = {}
        if not self.load_instructions(self.INST_TABLE_FILE):
            raise ValueError("error loading instruction")
        self.directive_table = ["START", "END", "BYTE", "WORD", "RESB", "RESW", "LITORG", "BASE",
                                "EQU", "ORG", "CSECT", "EXTDEF", "EXTREF"]
        # adding compatibilty with literals
        self.literal_table = {} # {"name": address or 0}

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
        :return: a list of objects of Assembly_line
        """
        first_pass_output = [] #array of assembly_line objects
        f = open(self.FILE, "r")
        temp_file = open(self.FILE +'.temp', 'w')

        self.current_address = self.start_address = self.get_start_address()
        # current_address = self.start_address

        for line in f:
            # handle comments
            if line[0] == '.':
                continue

            # get parts of the instruction
            parts = TwoPassAssembler.get_parts(line)

            # check if mnemonic exist
            if not parts['mnemonic']:
                raise SyntaxError('Mnemonics must be provided')

            # check if a label exist save it to the symbol table
            if parts['label']:
                if parts['label'] in self.symbol_table:
                    raise ValueError('Duplicate Label: ', parts['label'])

                if parts['mnemonic'] == 'EQU':
                    self.current_label = parts['label']
                else:
                    self.symbol_table[parts['label']] = self.current_address

            if "operands" not in parts:
                parts["operands"] = [""]

            # checking if the operand is a literal
            if re.search("^=([a-zA-Z]\"[a-zA-Z0-9]+\")", parts['operands'][0]):
                self.literal_table[parts['operands'][0]] = 0

            temp_line = "{} {} {} {}\n".format(self.current_address,
                                                parts['label'] if parts['label'] else '',
                                                parts['mnemonic'],
                                                ','.join(parts['operands']))

            temp_file.write(temp_line)

            assemb_line = Assembly_Line(self.current_address, parts['label'], parts['mnemonic'],
                parts['operands'])
            first_pass_output.append(assemb_line)

            current_inst_size = self.get_size(parts['mnemonic'], parts['operands'])
            current_address_int = int(self.current_address, 16)
            current_address_int += current_inst_size
            self.current_address = format(current_address_int, '04x')
            # self.current_address += self.get_size(parts['mnemonic'], parts['operands'])

        symbol_table = open(self.FILE + ".symbols", 'w')
        for symbol, address in self.symbol_table.items():
            # print(symbol, address)
            type = 'A' if symbol in self.symbol_table_en and not self.symbol_table_en[symbol] else 'R'
            symbol_table.write("{}: {} {}\n".format(symbol, address, type))

        symbol_table.close()
        f.close()
        temp_file.close()
        return first_pass_output


    @staticmethod
    def get_parts(line):
        """ (str) -> dict (str: str)

            get the parts of an instruction input line
            (Label)   menimoic    operands    #comments
            and return a dictionary of their values

            parts {
                'label': label if exist
                'mnemonic' memoic in the instruction
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
            elif t.isalpha() or (t == '+' and not current):
                current += t
            else:
                if len(current) == 0 and current_index != 2:
                    raise SyntaxError("Unexpected Start of instruction: " + t)
                else:
                    current += t

        if current != "":
            TwoPassAssembler.save_value(current_index, current, parts)

        if "operands" in parts:
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
              "mnemonic" if current_index == 1 else
              "operands" if current_index == 2 else
              "comment"] = current


    def get_size(self, mnemonic, operands):
        """
        Returns the size of the instruction depending on the instruction format
        and if it's a directive
        :param mnemonic: the operation mnemonic
        :param operands: operands of the instruction to decide on format 3 or 4
        :return: int

        >>> self.get_size("BYTE", ["X'F1'"])
        8
        >>> self.get_size("BYTE", ["C'EOF'"])
        24
        """
        # check if the mnemonic is a instruction in the assember instruction table
        tmnemonic = mnemonic[1::] if mnemonic[0] == '+' else mnemonic
        if tmnemonic in self.inst_table:
            # check if the instruction format is 1 or 2
            if self.inst_table[tmnemonic][0] in [1, 2] or self.inst_table[tmnemonic][0] == [2]:
                return self.inst_table[tmnemonic][0][0]
            else:
                # return size 4 if + which indicates a type 4 instruction
                return 4 if mnemonic[0] == '+' else 3
        elif mnemonic in self.directive_table:
            # check if the mnemonic is a directive
            # get the method that has the same name of the mnemonic and pass it the operands
            return self.__getattribute__(str.lower(mnemonic))(operands)
        else:
            # mnemonic is not an instruction or mnemonic
            print("mnemonic : ", tmnemonic)
            raise SyntaxError("Invalid mnemonic or directive")

    def get_start_address(self):
        f = open(self.FILE, 'r')
        # get the first line of the file if it has a START directive
        # set the start address of the assembler to the operand
        parts = self.get_parts(f.readline())
        if parts['mnemonic'] == 'START':
            # removed int to return a string which is more applicable to hex
            return parts['operands'][0]
        f.close()
        return 0

    @staticmethod
    def byte(operand):
        """
        Eval the number of bytes needed for the operand of the BYTE directive
        :param operand: the operand of the 'BYTE' directive
        :return: size of the operand in bytes

        >>> TwoPassAssembler.byte(["X'F1'"])
        1
        >>> TwoPassAssembler.byte(["C'EOF'"])
        3
        """
        operand = operand[0]
        if operand[0] == 'C':
            return len(operand[2:len(operand) - 1])
        elif operand[0] == 'X':
            return math.ceil(len(operand[2:len(operand) - 1]) / 2)
        else:
            try:
                if int(operand): #TODO
                    if len(hex(operand)) > 4:
                        raise ValueError("Number can't be represented with a Byte")
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

    def base(self, operands):
        return 0

    def litorg(self, operand):
        """
        Adds the literals with no address assigned in the literal table to this
        literal pool and return size accordinly
        :return: size of literal pool (int)
        """
        total_pool_size = 0
        current_address = self.current_address
        if self.literal_table.keys():
            # get the literal with value = 0
            for litral in [literal for literal in self.literal_table.keys() if not self.literal_table[literal]]:
                # TODO add word
                # get the size of the literal using BYTE method
                literal_size = TwoPassAssembler.byte([litral[1::]])
                self.literal_table[litral] = current_address

                current_address_int = int(current_address, 16)
                current_address_int += literal_size
                current_address = format(current_address_int, '04x')
                # current_address += literal_size
                total_pool_size += literal_size
        return total_pool_size

    def end(self, operands):
        return self.litorg(operands)

    def output_error(self, mssg, extra_arg):
        f = open(self.FILE + "_error", 'a')
        f.write(mssg + " : ")
        f.write(extra_arg + "\n")
        f.close()
        #exit()

    def org(self, operands):
        self.current_address = operands[0]
        return 0

    # Symbols Part
    def equ(self, operands):
        self.evaluate_expression(operands[0])
        return 0

    def check_if_forward(self, label):
        if label not in self.symbol_table:
            for sec in self.external_refs:
                if label in sec:
                    return
            self.output_error("Forward referencing is not allowed", label)
            #exit()

    def evaluate_expression(self, expression):
        """
        Matches the expression to a set of regular expressions and returns
        the evaluation of the expression along with 0:relative or 1:absolute
        :param expression:
        :return:
        """
        if re.fullmatch('^\*$', expression):
            self.symbol_table[self.current_label] = self.current_address
            self.symbol_table_en[self.current_label] = 1
            return

        if expression.count('*') or expression.count("/"):
            self.output_error("Invalid Expression", expression)
            exit()


        if re.fullmatch('^[0-9]+$', expression):
            self.symbol_table[self.current_label] = int(expression)
            self.symbol_table_en[self.current_label] = 0

        m = re.findall('[a-zA-z]+', expression)
        # if one label is used in EQU
        if len(m) == 1:
            self.check_if_forward(m[0])
            self.symbol_table_en[self.current_label] = 0
            self.symbol_table[self.current_label] = self.symbol_table[expression]
        elif len(m) > 1:
            map(self.check_if_forward, m)
            if len(m) % 2 == 0 and expression.count('-') == len(m) // 2:
                self.symbol_table_en[self.current_label] = 0
            elif len(m) > 2 and (len(m) - 1) % 2 == 0 and expression.count('-') == (len(m) - 1) // 2:
                self.symbol_table_en[self.current_label] = 1
            else:
                self.output_error("Invalid Expression not Relative nor Absolute", expression)
            for sym in m:
                sym_value = str(int(self.symbol_table[sym], 16)) if sym in self.symbol_table else 0x0000
                expression = str(expression).replace(sym, sym_value)
            self.symbol_table[self.current_label] = format(eval(expression), '04x')

    def csect(self, operands):
        self.control_section += 1
        return 0

    def extdef(self, operands):
        self.external_defs.insert(self.control_section, operands)
        # self.external_defs[self.control_section] = operands
        return 0

    def extref(self, operands):
        self.external_refs.insert(self.control_section, operands)
        # self.external_refs[self.control_section] = operands
        return 0

if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    FirstPass = TwoPassAssembler('tests/CODE.txt', 'tests/CODE-result.txt')
    FirstPass.first_pass()

