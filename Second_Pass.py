from hte import HTMEGenerator

class Second_Pass:

    registers = {
    'A':'00', 'X':'10', 'L':'02','B': '03',
    'S':'04','T': '05', 'F':'06', 'PC':'08', 'SW':'09'
    }
    # instruction_set = None
    # def symbol_table
    def __init__(self, lines, instruction_set, symbol_table,symbol_table_en, global_variables, filename="output"):
        """ Takes an array of Assembly_Line"""
        self.lines = lines
        self.instruction_set = instruction_set
        self.symbol_table = symbol_table
        self.filename = filename
        self.symbol_table_en = symbol_table_en
        self.global_variables  = global_variables

    def second_pass(self):
        object_codes = []
        base = None # this is used for base relative addressing mode
        startLine = self.lines[0]
        ht = HTMEGenerator(startLine.label,startLine.operands[0],'00000')
        for index,line in enumerate(self.lines):
            # line = self.lines[i]
            # print('line with instruction:{} has address:{}'.format(line.mnemonic, line.current_address))
            if line.mnemonic == 'START'  or line.mnemonic == 'EXTREF':
                continue
            elif line.mnemonic == 'CSECT':
                ht.output_records('0000',self.filename + ".txt", line.current_address[-2:] )
                ht = HTMEGenerator(line.label,'0','0')
                continue
            elif line.mnemonic == 'EXTDEF':
                continue
            elif line.mnemonic == 'END':
                ht.output_records(line.operands[0], self.filename + ".txt", line.current_address[-2:])
                break # This guarrentees that we can calculate
                #the PC for every instruction by checking the next line (No out of bounds)
            elif line.mnemonic == 'BASE':
                base = self.symbol_table[line.operands[0]]
            elif line.mnemonic == 'RESW' or line.mnemonic == 'RESB':
                dummy = 0
            elif line.mnemonic == 'BYTE' or line.mnemonic == 'WORD':
                object_codes.append(line.operands[0])
                print(operand[0], self.get_value((operand[0])))
                ht.add_text_record(self.get_value(line.operands[0]))
            elif line.mnemonic == 'RSUB':
                #special case
                object_codes.append('4C0000')
                ht.add_text_record('4c0000')
            else:
                opcode_format = self.get_opcode(line.mnemonic)
                is_indexed = len(line.operands) > 1
                opcode = opcode_format[1]
                operand = line.operands[0]
                # switch on formats
                if opcode_format[0][0] == 1:
                    object_codes.append(opcode)
                    ht.add_text_record(opcode)
                elif opcode_format[0][0] == 2:
                    object_codes.append(opcode + self.registers[operand])
                    ht.add_text_record(opcode + self.registers[operand])

                else:
                    #format 3 and 4
                    print('operand is:{}, mnemnoic is:{}, operands are:{}\n'.format(operand, line.mnemonic, line.operands))
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
                        # if format 4 we put the operand as is
                        address_in_obj_code = None
                        if line.mnemonic[0] == '+':
                            value = self.symbol_table[operand] if not operand[0].isdigit() else operand
                            if len(value) > 5:
                                raise SyntaxError('Operand is too big')
                            address_in_obj_code =  value
                            ht.add_modification_record(format(int(line.current_address,16) + 1,'02X'),5)
                        else:
                            # format 3
                            if is_immediate and (operand[0].isdigit() or operand in self.symbol_table_en):
                                if  operand[0].isdigit():
                                    address_in_obj_code = operand
                                else:
                                    address_in_obj_code =  self.symbol_table[operand]
                                    if self.symbol_table_en[operand] == 0: # if it's relative we add a modif record
                                        ht.add_modification_record(format(int(line.current_address,16) + 1,'02X'),5)
                            else:
                                hex_target_address = None
                                operand_abs_address = self.symbol_table[operand]
                                if operand_abs_address is None:
                                    raise SyntaxError('Cant find operand:{} in symbol table'.format(operand))
                                #first try PC relative
                                # print('{}\n'.format(i))
                                pc = self.lines[index + 1].current_address
                                TA = int(operand_abs_address,16) - int(pc,16)
                                print('index:{} pc hex is:{}, pc is:{} TA is:{}\n'.format(index,pc,int(pc,16),TA))
                                maximum_offset = 2048 #2^11
                                if TA <= maximum_offset - 1 and TA > -1 * maximum_offset:
                                    # we can make it PC relative
                                    address_in_obj_code = self.getTwosHex(TA)
                                    p = 1
                                else:
                                    #use base relative
                                    if base is None:
                                        raise SyntaxError('Need to set BASE because PC is out of bounds')
                                    else:
                                        TA = int(operand_abs_address,16) - int(base,16)
                                        if TA <= maximum_offset - 1 and TA > -1 * maximum_offset:
                                            #we use base
                                            address_in_obj_code = self.getTwosHex(TA)
                                            b = 1
                                        else:
                                            #TODO handle out of range error
                                            raise SyntaxError("The index is out of range: \n line:{} with instruction: {}  target address is:{}".format(line.current_address, line.mnemonic,operand_abs_address))
                        mnemonic_bin = format(int(opcode,16),'08b')
                        mnemonic_bin = mnemonic_bin[0:len(mnemonic_bin) - 2] #remove last 2 bits
                        obj_code_bin = mnemonic_bin + str(n) + str(i) + str(x) + str(b) + str(p) + str(e)
                        #Align displacement with zeros
                        while line.mnemonic[0] == '+' and len(address_in_obj_code) < 5:
                            address_in_obj_code = '0' + address_in_obj_code
                        #for format 3:
                        while len(address_in_obj_code) < 3:
                            address_in_obj_code = '0' + address_in_obj_code
                        full_obj_code = format(int(obj_code_bin, 2),'03X') + address_in_obj_code
                        # print("Instruction:{} opcode:{} Mnemonic in binary:{} Object_code_bin:{} hex:{}, full_object_code: {}".format(line.mnemonic, opcode,mnemonic_bin,obj_code_bin,format(int(obj_code_bin, 2),'02X'),full_obj_code))
                        object_codes.append(str(full_obj_code))
                        ht.add_text_record(str(full_obj_code))
        return object_codes
    def getTwosHex(self,int_address):
        twos = (abs(int_address) ^ 0xFFF) + 1 if int_address < 0 else int_address
        return format(twos, '03X')


    def get_opcode(self, mnemonic):
        if mnemonic[0] == '+':
            mnemonic = mnemonic[1:]
        opcode = self.instruction_set[mnemonic]

        if opcode is None:
            raise SyntaxError('No function named: {}'.format(mnemonic))
        return opcode

    def get_value(self, operand):
        """
        Get the hex value of the BYTE, WORD directives
        :param operand: operand for the BYTE, WORD directives
        :return:
        """
        value = ''
        if operand[0] == 'C':
            word = operand
            print(word)
            word_length = len(operand)
            value = "".join([hex(ord(s))[2:] for s in word[2: word_length - 1]])
            print("Ascii is ", value)
        elif operand[0] == 'X':
            value = operand[2: len(operand) - 1]
        else:
            # value = hex(int(operand))[2::]
            value = operand
        return value
