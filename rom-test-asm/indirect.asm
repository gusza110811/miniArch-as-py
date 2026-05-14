main {
    mov ds, cs
    mov bx, data

    mov ax, [bx]
    mov cx, [bx + 2]
    mov dx, [bx + 4]

    halt
}

.org 0x0100
data:
    .word 0x6502
    .word 0xDEAD
    .word 0xBEEF

; expected end state
; ax = 6502
; bx =  100
; cx = dead
; dx = beef

.org 0xFFF0
reset {
    jmpf 0xF000, 0
}
