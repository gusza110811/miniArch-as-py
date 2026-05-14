dbgconsole = 0xffff

main {
    mov [w 2*4], ax
    mov [w 2*4 + 2], cs
    mov ax, test
    int 2
    hlt
}

test {
    mov bx, dbgconsole
    mov ax, '!'
    out bx, ax
    retf
}

.org 0xfff0
reset {
    jmpf 0xf000, 0x0
}
