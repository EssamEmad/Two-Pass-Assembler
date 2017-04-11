class Second_Pass:

    def registers = {
    'A':'00', 'X':'01', 'L':'02','B': '03'
    'S':'04','T': '05', 'F':'06', 'PC':'08', 'SW':'09'
    }
    def instruction_set
    def symbol_table
    def __init__(self, lines, instruction_set, symbol_table):
        """ Takes an array of Assembly_Line"""
        self.lines = lines
        self.instruction_set = instruction_set
        self.symbol_table = symbol_table

    def second_pass(self):
        object_codes = []
        for i in range(len(lines)):
            line = lines[i]
            if line.mnemonic == 'END':
                return # This guarrentees that we can calculate
                #the PC for every instruction by checking the next line (No out of bounds)
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
                    i = 1 if is_immediate else 0
                    n = 1 if is_indirect else 0
                x = 1 if is_indexed else 0
                #remove the # or @
                if is_immediate or is_indirect:
                    operand = operand[1:]
                #Now we calculate the operand
                if is_immediate and operand[1:].isdigit():
                    # ex #13242
                    # This is an exceptional case, where the operand is passed as is
                    b = p = 0
                else:
                    operand_abs_address = self.symbol_table[operand]
                    if operand_abs_address is None:
                        #TODO handle the error
                    #first try PC relative
                    pc = lines[i + 1].current_address
                    TA = operand_abs_address - pc
                    maximum_offset = 2048 #2^11
                    if line.mnemonic[0] == '+':
                        #if format 4 increase the offset
                        maximum_offset = 2**19
                    if TA <= maximum_offset - 1 and TA > -1 * maximum_offset:
                        # we can make it PC relative
                        

    def get_opcode(self, mnemonic):
        opcode = instruction_set[mnemonic]

        if opcode is None:
            #TODO handle the error
        return opcode
