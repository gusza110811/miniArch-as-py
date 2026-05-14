main {
    mov ax, 0xAEFE
    mov cx, ah
    mov dh, ax
    halt
}

.org 0xFFF0
reset {
    jmpf 0xF000, main
}
; expected end state
; ax = AEFE
; cx = AE
; dx = FE00
