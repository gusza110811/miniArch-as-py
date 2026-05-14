; Hello World program in miniArch assembly

.offset 0x7c00

print {
    mov bx, msg
    mov dx, 0x01
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        int 0x14
        add bx, 1
        jmp loop
    done:
    hlt
}

msg:
.asciiz "Hello, World!\r\n"
