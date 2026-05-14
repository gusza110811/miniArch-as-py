.offset 0x7c00

main {
    mov ax, 0x15
    push ax
    mov ax, 0x25
    push ax
    mov ax, 0x35
    push ax

    mov bx, [bp-2]
    mov cx, [bp-4]
    mov dx, [bp-6]

    hlt
}
