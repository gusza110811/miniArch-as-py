; test the bitwise instructions
test {
    mov ax, 0xAA
    and ax, 0xCC
    mov bx, 0xCC
    or  bx, 0xAA
    mov cx, 0xAA
    xor cx, 0xCC
    mov dx, 0xAA
    not dx

    shl ax, 8
    shr dx, 8

    halt
}

.org 0xFFF0
reset {
    jmpf 0xF000, test
}

; expected end state:
; ax = 8800
; bx = 00EE
; cx = 0066
; dx = 00FF
