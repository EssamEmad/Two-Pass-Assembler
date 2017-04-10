class Second_Pass:

    def registers = {
    'A':'00', 'X':'01', 'L':'02','B': '03'
    'S':'04','T': '05', 'F':'06', 'PC':'08', 'SW':'09'
    }
    def instruction_set
    def __init__(self, lines, instruction_set):
        """ Takes an array of Assembly_Line"""
        self.lines = lines
        self.instruction_set = instruction_set

    def second_pass(self):
        object_codes = []
        for line in lines:
            opcode_format = self.get_opcode(line.mnemonic)
            is_indexed = len(line.operands) > 1
            opcode = opcode_format[1]
            operand = line.operands[0]
            # switch on formats
            if opcode_format[0] == '1':
                object_codes.extend(opcode)
            elif opcode_format[0] == '2':
                object_codes.extend(opcode + self.registers[operand])
            else:
                #both format 3 and 4
                is_immediate = operand[0] == '#'
                is_indirect = operand[0] == '@'
                n = i = x = b = p = e = 0
                if is_immediate == is_indirect:
                     # that can only happen if both are False
                     n = i = 1
                else:
                    i = 1 if is_immediate
                    n = 1 if is_indirect
                x = 1 if is_indexed
                

    def get_opcode(self, mnemonic):
        opcode = instruction_set[mnemonic]

        if opcode is None:
            #TODO handle the error
        return opcode
