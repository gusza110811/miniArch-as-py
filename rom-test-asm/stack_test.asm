main {
    mov ax, 0x1108
    push ax
    pushb ax
    pushb ah

    popb bx
    popb dx
    pop cx
    halt
}

; expected end state
; ax = 1108
; bx =   11
; cx = 1108
; dx =   08

.org 0xfff0
reset {
    jmpf 0xf000, 0x0
}
