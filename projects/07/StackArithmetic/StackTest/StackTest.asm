@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_0
D;JEQ
@SP
A=M
M=0
@$$CMPe_0
0;JMP
($$CMPt_0)
@SP
A=M
M=-1
($$CMPe_0)
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_1
D;JEQ
@SP
A=M
M=0
@$$CMPe_1
0;JMP
($$CMPt_1)
@SP
A=M
M=-1
($$CMPe_1)
@SP
M=M+1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_2
D;JEQ
@SP
A=M
M=0
@$$CMPe_2
0;JMP
($$CMPt_2)
@SP
A=M
M=-1
($$CMPe_2)
@SP
M=M+1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_3
D;JLT
@SP
A=M
M=0
@$$CMPe_3
0;JMP
($$CMPt_3)
@SP
A=M
M=-1
($$CMPe_3)
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_4
D;JLT
@SP
A=M
M=0
@$$CMPe_4
0;JMP
($$CMPt_4)
@SP
A=M
M=-1
($$CMPe_4)
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_5
D;JLT
@SP
A=M
M=0
@$$CMPe_5
0;JMP
($$CMPt_5)
@SP
A=M
M=-1
($$CMPe_5)
@SP
M=M+1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_6
D;JGT
@SP
A=M
M=0
@$$CMPe_6
0;JMP
($$CMPt_6)
@SP
A=M
M=-1
($$CMPe_6)
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_7
D;JGT
@SP
A=M
M=0
@$$CMPe_7
0;JMP
($$CMPt_7)
@SP
A=M
M=-1
($$CMPe_7)
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@$$CMPt_8
D;JGT
@SP
A=M
M=0
@$$CMPe_8
0;JMP
($$CMPt_8)
@SP
A=M
M=-1
($$CMPe_8)
@SP
M=M+1
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D+M
@SP
A=M
M=D
@SP
M=M+1
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D-M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
M=-M
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D&M
@SP
A=M
M=D
@SP
M=M+1
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
D=D|M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
M=!M
@SP
M=M+1