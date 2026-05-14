lastaddr = 0x100
buffer = 0x200
printbuf = 0x300
console = 0xFFFF

entry {
    mov ds, 0xE800
    mov ss, 0xE000
    mov es, 0xD000
}

main {
    mov bx, buffer
    call input

    loop:
        mov ax, [b bx]

        cmp ax, 'w'
        jz write

        cmp ax, 0
        jz main

    jmp read

    read {
        push ax
        push cx

        call hex_to_int
        push bx

        mov [w lastaddr], ax
        mov bx, ax
        mov ax, [b es:bx]

        mov bx, printbuf
        mov cx, 2
        call int_to_hex
        call print
        call printLine

        pop bx
        add bx, 1
        pop cx
        pop ax
        jmp loop
    }
    write {
        push ax
        add bx, 1
        call hex_to_int
        push bx
        mov bx, [w lastaddr]

        mov [b es:bx], ax
        add bx, 1
        mov [w lastaddr], bx

        pop bx
        add bx, 1
        pop ax
        jmp loop
    }
}

; bx = pointer to string
print {
    pusha
    mov dx, 0xffff
    mov cx, '\r'
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        add bx, 1
        cmp ax, '\n'
        jz lfcrlf
        out dx, ax
        jmp loop
    lfcrlf:
        out dx, cx
        out dx, ax
    jmp loop

    done:
    popa
    ret
}

printLine {
    push ax
    push bx
    mov bx, 0xffff
    mov ax, '\r'
    out bx, ax
    mov ax, '\n'
    out bx, ax
    pop bx
    pop ax
    ret
}

{
    ; parameter:
    ; bx = pointer to buffer
    export input {
        pusha
        export loop:
        mov dx, 0xffff
        in ax, dx
        cmp ax, 0
        jz loop

        cmp ax, '\b'
        bz bksp

        cmp ax, '\n'
        jz crlf

        cmp ax, '\r'
        jz crlf

        out dx, ax

        mov [b bx], ax
        add bx, 1
        jmp loop
    }

    ; affect cx
    crlf {
        mov cx, '\r'
        out dx, cx
        mov cx, '\n'
        out dx, cx
        mov [b bx], cx
        add bx, 1
        mov cx, 0
        mov [b bx], cx
        popa
        ret
    }

    ; affect cx, bx--
    bksp {
        mov cx, ' '
        out dx, ax
        out dx, cx
        out dx, ax
        sub bx, 1
        mov ax, [b bx]
        jmp loop
    }
}

; bx <- pointer to string result
; cx <- length
; ax <- integer
; doesnt null terminate
int_to_hex {
    pusha
    add bx, cx
    loop:
        sub bx, 1
        mov dx, ax
        shr ax, 4
        and dx, 0xF

        add dx, 0x30
        cmp dx, 0x3A

        jn skip
        add dx, 0x7
        skip:

        mov [b bx], dx
        sub cx, 1
    jnz loop

    popa
    ret
}

; bx <- pointer to string
; ax -> result
; bx -> end of hex
hex_to_int {
    push dx
    xor ax, ax
    loop:
        mov dx, [b bx]
        sub dx, 0x30
        jn end
        cmp dx, 10
        jn skip
            sub dx, 0x7
        cmp dx, 0xF
        jn skip
            sub dx, 0x20
        skip:
        cmp dx, 16
        jnn end
        shl ax, 4
        or ax, dx
        add bx, 1
    jmp loop
    
    end:
    pop dx
    ret
}

.offset 0x8000
; read-only data goes here
.offset 0

.org 0xfff0
reset {
    jmpf 0xf000, entry
}
