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

(LOOP)
    @KBD
    D=M
    @BLACKSCREEN // if keyboard is not clicked RAM[KBD] = 0, goto WHITESCREEN
    D;JEQ
    @WHITESCREEN // if keyboard is clicked RAM[KBD] > 0, goto BLACKSCREEN
    D;JGT
    @LOOP // otherwise, loop again
    0;JMP

(BLACKSCREEN)
    @8191 // i = 8191, last register cover the screen start from SCREEN pointer
    D=A
    @i
    M=D 
    (BLACKSCREENLOOP)
    @KBD
    D=M
    @WHITESCREEN // if keyboard is not clicked RAM[KBD] = 0, goto WHITESCREEN
    D;JEQ
    @i
    D=M
    @LOOP
    D;JLT // i < 0 goto LOOP
    @SCREEN
    A=D+A // set address = screen + i
    M=-1 // set the RAM[address] to 1111111111111111
    @i
    M=M-1 // i = i - 1
    @BLACKSCREENLOOP
    0;JMP


(WHITESCREEN)
    @8191
    D=A
    @i
    M=D // i < 0 goto LOOP
    (WHITESCREENLOOP)
    @KBD
    D=M
    @BLACKSCREEN // if keyboard is clicked RAM[KBD] > 0, goto BLACKSCREEN
    D;JGT
    @i
    D=M
    @LOOP
    D;JLT
    @SCREEN
    A=D+A // set address = screen + i
    M=0 // set the RAM[address] to 0000000000000000
    @i
    M=M-1 // i = i - 1
    @WHITESCREENLOOP
    0;JMP
