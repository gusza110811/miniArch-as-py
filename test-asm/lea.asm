.offset 0x7c00

main {
    mov ds, 0x0700

    lea ax, [cs:0x7c00]

    hlt
}
