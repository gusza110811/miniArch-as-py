; Hello World program in miniArch assembly
; CS = FFFF
; DS = SS = ES = 0

func print {
    mov bx, msg
    mov ds, cs ; set ds to the same value as cs
    mov dx, 0xFFFF ; dx = port of the serial console
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        out dx, ax
        add bx, 1
        jmp loop
    done:
    halt
}

msg:
.asciiz "Hello, World!\r\n"

.org 0xFFF0 ; F000:FFF0 = FFFF:0000
func reset {
    jmpf 0xF000, 0
}
