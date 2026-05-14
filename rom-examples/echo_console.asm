; echo console
; this program reads characters from the input and echoes them back to the output.
; it assumes that the "terminal" does not send CRLF, but only CR or LF, and it will echo CRLF for both cases.

buffer = 0x1000

init {
    mov bx, text
    mov ds, cs
    call print
}

main {
    mov ds, 0
    mov bx, buffer
    call input
    mov bx, buffer
    call print
    jmp main
}

{
    ; affects all gpr
    ; parameter:
    ; bx = pointer to buffer
    ; returns:
    ; bx = pointer to end of string
    export input {
        mov dx, 0xffff
        in ax, dx
        cmp ax, 0
        jz input

        cmp ax, '\b'
        bz bksp

        cmp ax, '\n'
        jz crlf

        cmp ax, '\r'
        jz crlf

        out dx, ax

        mov [b bx], ax
        add bx, 1
        jmp input
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
        jmp input
    }
}
; crlf and bksp is out of scope

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

text:   .asciiz "Echo Console\n"

; reset vector
.org 0xFFF0
reset {
    jmpf 0xF000, 0
}

.org 0xFFFF .zero ; this part isnt important but it makes the output binary perfectly 64kiB
