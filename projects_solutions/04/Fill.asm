// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
(MAIN)
@KBD
D=M
@FILL
D;JNE
@UNFILL
0;JMP

(FILL)
@SCREEN
D=A
@i
M=D
(FILL_1)
@KBD
D=A-D
@MAIN
D;JLE
@i
A=M
M=-1
@i
MD=M+1
@FILL_1
0;JMP

(UNFILL)
@SCREEN
D=A
@i
M=D
(UNFILL_1)
@KBD
D=A-D
@MAIN
D;JLE
@i
A=M
M=0
@i
MD=M+1
@UNFILL_1
0;JMP
