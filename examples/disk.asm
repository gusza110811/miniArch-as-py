; MiniArch boot sector example using the BIOS disk service.

.offset 0x7c00

main {
    ; check disk status via BIOS disk service
    mov dx, 0x0000
    int 0x13
    cmp ax, 0x0000
    jnz disk_error

    ; select sector 1
    mov ax, 1
    mov cx, 0
    mov dx, 4
    int 0x13
    cmp ax, 0x0000

    ; read sector 1 into memory at 0x7e00
    mov bx, 0x7e00
    mov dx, 1
    int 0x13
    cmp ax, 0
    jnz disk_error

    ; report success
    mov bx, success_msg
    call print_string
    hlt
}

print_string {
    mov dx, 0x0001

print_loop:
    mov ax, [b bx]
    cmp ax, 0x0000
    jz print_done
    int 0x14
    add bx, 0x0001
    jmp print_loop

print_done:
    ret
}

disk_error {
    mov bx, error_msg
    call print_string
    hlt
}

success_msg:
.asciiz "Disk service read sector 1 successfully!\r\n"

error_msg:
.asciiz "Disk service failed.\r\n"

.offset 0
.org 0x200

.asciiz "Test test\r\n"
.org 0x400
