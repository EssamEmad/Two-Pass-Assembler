import sys
import two_pass_assembler
import Second_Pass


def main():
    try:
        file_name = sys.argv[1]
    except IndexError:
        print("Please provide a file name/path to assemble")
        return
    fp = two_pass_assembler.TwoPassAssembler(file_name,
                                             sys.argv[2] if len(sys.argv) > 2 else file_name)
    lines = fp.first_pass()
    sp = Second_Pass.Second_Pass(lines, fp.inst_table, fp.symbol_table)
    sp.second_pass()

if __name__ == '__main__':
    main()