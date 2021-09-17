
class CodeWriter:

    def __init__(self, out_path):
        self.out_stream = open(out_path, "w")
        self.file_name = out_path.split(".")[0]
        self.op_count = {"eq": 0, "gt": 0, "lt": 0}
        self.return_count = 0

    def writeArithmetic(self, operation):
        if operation == "add":
            code = f"""
// add
@SP
M=M-1
A=M
D = M
@SP
M = M - 1
A = M
M = D + M
@SP
M = M + 1
"""
        elif operation == "sub":
            code = f"""
// sub
@SP
M = M - 1
A = M
D = M
@SP
M = M - 1
A = M
M = M - D
@SP
M = M + 1
"""
        elif operation == "neg":
            code = f"""
// neg
@SP
M = M - 1
A = M
M = -M

@SP
M = M + 1
"""
        elif operation == "eq":
            code = f"""
// eq
@SP
M = M-1
A = M
D = M
// D becomes y

@SP
M = M-1
A = M
D = M-D

// D becomes x - y
@TRUE_eq_{self.op_count['eq']}
// Jump if x == y
D;JEQ

// Jump unconditionally
@FALSE_eq_{self.op_count['eq']}
0;JMP

(TRUE_eq_{self.op_count['eq']})
@SP
A = M
M = -1

@END_eq_{self.op_count['eq']}
0;JMP

(FALSE_eq_{self.op_count['eq']})
@SP
A = M
M = 0

(END_eq_{self.op_count['eq']})
// SP++;
@SP
M = M + 1
"""
            self.op_count["eq"] += 1
        elif operation == "gt":
            code = f"""
// gt
@SP
M = M-1
A = M
D = M
// D becomes y

@SP
M = M-1
A = M
D = M-D

// D becomes x - y
@TRUE_gt_{self.op_count['gt']}
// Jump if x > y
D;JGT

// Jump unconditionally
@FALSE_gt_{self.op_count['gt']}
0;JMP

(TRUE_gt_{self.op_count['gt']})
@SP
A = M
M = -1

@END_gt_{self.op_count['gt']}
0;JMP

(FALSE_gt_{self.op_count['gt']})
@SP
A = M
M = 0

(END_gt_{self.op_count['gt']})
// SP++;
@SP
M = M + 1
"""
            self.op_count["gt"] += 1
        elif operation == "lt":
            code = f"""
// lt
@SP
M = M-1
A = M
D = M
// D becomes y

@SP
M = M-1
A = M
D = M-D

// D becomes x - y
@TRUE_lt_{self.op_count['lt']}
// Jump if x < y
D;JLT

// Jump unconditionally
@FALSE_lt_{self.op_count['lt']}
0;JMP

(TRUE_lt_{self.op_count['lt']})
@SP
A = M
M = -1

@END_lt_{self.op_count['lt']}
0;JMP

(FALSE_lt_{self.op_count['lt']})
@SP
A = M
M = 0

(END_lt_{self.op_count['lt']})
// SP++;
@SP
M = M + 1
"""
            self.op_count["lt"] += 1
        elif operation == "and":
            code = f"""
// and
@SP
M = M - 1
A = M
D = M
@SP
M = M - 1
A = M
M = D & M
@SP
M = M + 1
"""

        elif operation == "or":
            code = f"""
// or
@SP
M = M - 1
A = M
// D becomes y
D = M

@SP
M = M - 1
A = M
M = D|M
@SP
M = M + 1
"""
        elif operation == "not":
            code = f"""
// not
// neg
@SP
M = M - 1
A = M
M = !M

@SP
M = M + 1     
"""
        else:
            print("INVALID ARITHMETIC OPERATION!!!")
        self.out_stream.write(code)

    def writePushPop(self, command_type, tokens):
        base = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

        if command_type == "PUSH":
            if tokens["arg1"] == "constant":
                code = f"""
// push constant {tokens['arg2']}
@{tokens['arg2']}
D = A
@SP
A = M
M = D
@SP
M = M + 1
"""
            elif tokens["arg1"] in ("local", "argument", "this", "that"):
                code = f"""
// push {tokens['arg1']} {tokens['arg2']}
@{tokens['arg2']}
D = A
@{base[tokens['arg1']]} 
A = D + M
D = M
@SP
A = M
M = D
@SP
M = M + 1
"""
            elif tokens["arg1"] == "static":
                code = f"""
// push static {tokens['arg2']}
@{self.file_name}.{tokens['arg2']}
D = M
@SP
A = M
M = D
@SP
M = M + 1
"""
            elif tokens["arg1"] == "temp":
                code = f"""
// push temp {tokens['arg2']}
@{tokens['arg2']}
D = A
@5
A = D + A
D = M
@SP
A = M
M = D
@SP
M = M + 1
"""
            elif tokens["arg1"] == "pointer":
                if tokens["arg2"] == "0":
                    code = f"""
// push pointer 0
@THIS
D = M
@SP
A = M
M = D
@SP
M = M + 1
"""
                else:
                    code = f"""
// push pointer 1
@THAT
D = M
@SP
A = M
M = D
@SP
M = M + 1
"""
        elif command_type == "POP":
            if tokens["arg1"] in ("local", "argument", "this", "that"):
                code = f"""
// pop {tokens['arg1']} {tokens['arg2']}
@{tokens['arg2']}
D = A
@{base[tokens['arg1']]}
D = D + M
@SP
A = M
M = D
@SP
M = M - 1
@SP
A = M
D = M
A = A + 1
A = M
M = D
"""
            elif tokens["arg1"] == "static":
                code = f"""
// pop static {tokens['arg2']}
@SP
M = M - 1
A = M
D = M

@{self.file_name}.{tokens['arg2']}
M = D
"""
            elif tokens["arg1"] == "temp":
                code = f"""
// pop temp {tokens['arg2']}
@{tokens['arg2']}
D = A
@5
D = D + A
@SP
A = M
M = D
@SP
M = M - 1
@SP
A = M
D = M
A = A + 1
A = M
M = D
"""
            elif tokens["arg1"] == "pointer":
                if tokens["arg2"] == "0":
                    code = f"""
// pop pointer 0
@SP
M = M - 1
A = M
D = M

@THIS 
M = D
"""
                else:
                    code = f"""
// pop pointer 1
@SP
M = M - 1
A = M
D = M

@THAT 
M = D
"""
        self.out_stream.write(code)

    def writeLabel(self, label):
        code = f"\n// label {label}\n({label})\n"
        self.out_stream.write(code)

    def writeGoto(self, label):
        code = f"\n// goto {label}\n@{label}\n0;JMP"
        self.out_stream.write(code)

    def writeIf(self, label):
        code = f"""
// if-goto label
@SP
M = M - 1
A = M
D = M

@{label}
D;JNE
"""
        self.out_stream.write(code)

    def writeFunction(self, function_name, nvars):
        code = f"""
// function {function_name} {nvars}     
({function_name})
@{nvars}   
D = A
({function_name + "$local$loop"})

@{function_name + "$local$end"}
D;JLE

@SP
A = M
M = 0
@SP
M = M + 1

@{function_name + "$local$loop"}
D = D - 1
0;JMP
({function_name + "$local$end"})
"""
        self.out_stream.write(code)

    def writeCall(self, function_name, nargs):
        code = f"""
// call {function_name} {nargs}

// push retAddrLabel
@{self.file_name}$return.{self.return_count}
D = A

@SP
A = M
M = D

@SP
M = M + 1

// push LCL
@LCL
D = M

// SP++;
@SP
A = M
M = D

@SP
M = M + 1

// push ARG
@ARG
D = M

// SP++;
@SP
A = M
M = D

@SP
M = M + 1

// push THIS
@THIS
D = M

// SP++;
@SP
A = M
M = D

@SP
M = M + 1

// push THAT
@THAT
D = M

// SP++;
@SP
A = M
M = D

@SP
M = M + 1

// ARG = SP - 5 - nargs
@5
D = A

@SP
D = M - D

@{nargs}
D = D - A

@ARG 
M = D

// LCL = SP
@SP
D = M

@LCL
M = D

// goto functionName
@{function_name}
0;JMP

({self.file_name}$return.{self.return_count})
"""
        self.return_count += 1
        self.out_stream.write(code)

    def write_return(self):
        code = f"""
// return

// endFrame = LCL
@LCL
D = M

@R13
M = D

// retAddr = *(endFrame - 5)
@5
D = D - A
A = D
D = M

@R14
M = D

// *ARG = pop()
@SP
M = M - 1
A = M
D = M

@ARG
A = M
M = D

// SP = ARG + 1
@ARG
D = M

@SP
M = D + 1

// THAT = *(endFrame - 1)
@R13
A = M - 1
D = M

@THAT
M = D

// THIS = *(endFrame - 2)
@2
D = A

@R13
D = M - D
A = D
D = M

@THIS
M = D

// ARG = *(endFrame - 3)
@3
D = A

@R13
D = M - D
A = D
D = M

@ARG
M = D

// LCL = *(endFrame - 4)
@4
D = A

@R13
D = M - D
A = D
D = M

@LCL
M = D

@R14
A = M
0;JMP
"""
        self.out_stream.write(code)

    def writeInit(self):
        code = f"""
// Bootstrap code
// SP = 256
@256
D = A

@SP
M = D
"""
        self.out_stream.write(code)
        self.writeCall("Sys.init", "0")

    def set_file_name(self, new_filename):
        self.file_name = new_filename

    def close(self):
        self.out_stream.close()
