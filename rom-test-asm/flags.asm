main {
    sta
    sti
    clz
    clc
    cln
    clo
    cli

    halt
}

.org 0xFFF0
reset {
    jmpf 0xF000, 0
}
