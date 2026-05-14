; relevant ports:
; 0x0320: controller command
; 0x0321: controller status
; 0x0322: sector (octet 0)
; 0x0323: sector (octet 1)
; 0x0324: sector (octet 2)
; 0x0325: sector (octet 3)
; 0x0326: device number
; 0x0327: data
; 0xffff: debug console

; disk commands:
; 0x01: read sector
; 0x02: write sector
; 0x03: query devices
; 0x04: query sector count
; 0x05: clear buffer

main {
    mov ax, 0xF800
    mov ds, ax
    ; check for disks
    mov bx, 0x0320
    mov ax, 0x03
    out bx, ax
    mov bx, 0x0327
    in ax, bx
    cmp ax, 0
    jz no_disks
    jmp read
}

no_disks {
    mov bx, err_msg
    call print
    hlt
}

read {
    mov bx, 0x0320
    mov ax, 0x05
    out bx, ax
    mov ax, 0x01
    out bx, ax

    ; read buffer
    mov dx, 0x0327
    mov bx, 0x8000
    mov cx, 512
    read_loop:
        in ax, dx
        mov [b bx], ax
        add bx, 1
        sub cx, 1
    jnz read_loop

    hlt
}

; bx = pointer to message
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

err_msg:
    .asciiz "No disks found\n"

.org 0xFFF0
reset {
    jmpf 0xf000, main
}
