.offset 0x7c00

main {
    mov bx, string
    call atoi
    hlt
}

; bx = pointer to string
; ax = result
atoi {
    push bx
    push dx
    loop:
        mov dx, [b bx]
        sub dx, 0x30
        jn end
        cmp dx, 10
        jnn end
        call mul10
        add ax, dx
        add bx, 1
    jmp loop
    
    end:
    pop dx
    pop bx
    ret
}

; multiplies ax by 10
mul10 {
    push dx

    shl ax, 1
    mov dx, ax
    shl ax, 2
    add ax, dx

    pop dx
    ret
}

string:
    .asciiz "225"
