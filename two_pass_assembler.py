import re


class TwoPassAssembler:
    """
    Two pass assembler simulation
    System Programming Course 2017
    """
    def __init__(self, FILE, output_path, start_address, INST_TABLE_FILE = 'inst.txt'):
        self.FILE = FILE
        self.output_path = output_path
        self.symbol_table = {}
        self.start_address = start_address
        self.INST_TABLE_FILE = INST_TABLE_FILE
        if not self.load_instructions(self.INST_TABLE_FILE):
            raise ValueError("error loading instruction")
        self.inst_table = {}

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
        """
        if self.inst_table[memonic]:
            if self.inst_table[memonic][0] in [1, 2]:
                return self.inst_table[memonic][0]
            else:
                return 4 if operands[0] == '+' else 3
        else:
            # todo get the size of the directive
            pass