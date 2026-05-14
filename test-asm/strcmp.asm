.offset 0x7c00

result0 = 0x8000
result1 = 0x8001

main {
    mov ax, string0
    mov dx, string1
    call strcmp
    mov [result0], ax

    mov ax, string0
    mov dx, string0
    call strcmp
    mov [result1], ax

    hlt
}

; ax <- string 0
; dx <- string 1
; ax -> result
; 0 -> equal, 1 -> string 0 < string 1, 2 -> string 1 < string 0
strcmp {
    loop:
        mov bx, dx
        mov cx, [b bx]
        mov bx, ax
        mov bx, [b bx]

        cmp bx, cx
        jn less
        jnz more

        cmp bx, 0
        jz equal

        add ax, 1
        add dx, 1

        jmp loop

    less:
        mov ax, 1
        ret
    more:
        mov ax, 2
        ret
    equal:
        mov ax, 0
        ret

}

string0: .ascii "Hello"
string1: .ascii "World"
