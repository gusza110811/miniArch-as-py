# MiniArch Assembler Documentation

## Table of Contents

1. [Overview](#overview)
2. [Syntax Basics](#syntax-basics)
3. [Data Types and Values](#data-types-and-values)
4. [Registers](#registers)
5. [Addressing Modes](#addressing-modes)
6. [Instructions](#instructions)
7. [Labels and Functions](#labels-and-functions)
8. [Constants](#constants)
9. [Data Directives](#data-directives)
10. [Memory Layout Directives](#memory-layout-directives)
11. [Export and Visibility](#export-and-visibility)
12. [Examples](#examples)
13. [Compiler Usage](#compiler-usage)

---

## Overview

The MiniArch Assembler translates assembly source code (`.asm` files) into machine-executable binary code (`.bin` files). The assembler processes a single-pass compilation with a full expression evaluator, supporting numeric literals in multiple bases, constants, labels, and full control over memory layout.

The assembler is built using the Lark parsing framework with a formal grammar and transforms the parsed abstract syntax tree (AST) into executable machine code following the MiniArch Instruction Set Architecture (ISA).

---

## Syntax Basics

### Comments

Comments begin with a semicolon (`;`) and extend to the end of the line:

```asm
; This is a comment
mov ax, 0x10  ; This is also a comment
```

### Whitespace

Whitespace (spaces and tabs) is used to separate tokens but is otherwise ignored. Newlines are significant and divide statements.

### Case Insensitivity

Register names and instruction mnemonics are case-insensitive:

```asm
mov AX, 0x10    ; Valid
MOV ax, 0x10    ; Valid
Mov Ax, 0x10    ; Valid
```

---

## Data Types and Values

### Numeric Literals

The assembler supports numeric values in four bases:

| Base | Prefix | Example | Decimal Value |
|------|--------|---------|---------------|
| Binary | `0b` | `0b1010_1100` | 172 |
| Octal | `0o` | `0o254` | 172 |
| Decimal | None | `172` | 172 |
| Hexadecimal | `0x` | `0xAC` | 172 |

Underscores can be used as digit separators for readability (e.g., `0x1234_5678`).

### Character Literals

Single characters can be specified using single quotes:

```asm
mov ax, 'A'    ; Load ASCII code for 'A' (0x41)
```

### String Literals

Strings are enclosed in double quotes and support standard escape sequences:

```asm
.asciiz "Hello, World!\r\n"
```

Supported escape sequences:
- `\n` - Newline
- `\r` - Carriage return
- `\t` - Tab
- `\\` - Backslash
- `\"` - Double quote
- `\xHH` - Hex escape

---

## Registers

### Word Registers (16-bit)

**General Purpose:**
- `AX` - Accumulator
- `BX` - Base
- `CX` - Counter
- `DX` - Data

**Segment Registers:**
- `CS` - Code Segment
- `DS` - Data Segment
- `SS` - Stack Segment
- `ES` - Extra Segment

**Pointer Registers:**
- `SP` - Stack Pointer
- `BP` - Base Pointer

### Byte Registers (8-bit)

High bytes of word registers:
- `AH` - High byte of AX
- `BH` - High byte of BX
- `CH` - High byte of CX
- `DH` - High byte of DX

### Special Registers (Internal, Read-only)

- `PC` - Program Counter (next instruction)
- `IP` - Instruction Pointer (current instruction)
- `FLAGS` - Status Flags (bit 0: Zero, bit 1: Carry, bit 2: Negative, bit 3: Overflow, bit 4: Interrupt Enable)

Registers are specified in instruction parameters by their mnemonic name.

---

## Addressing Modes

Memory addresses can be specified using three addressing modes. Each mode can optionally specify the size (`b` for byte, `w` for word) and segment.

### Direct Addressing

Access memory at an immediate address:

```asm
mov ax, [DS:0x1000]     ; Load from DS:0x1000
mov ax, [0x1000]        ; Default segment (typically DS)
mov ax, [w 0x1000]      ; Word-sized access
mov ax, [b 0x1000]      ; Byte-sized access
```

**Syntax:** `[` [`SEGMENT` `:` ] `address` `]`

### Indirect Addressing

Access memory at the address in the `BX` or `BP` register:

```asm
mov ax, [BX]            ; Load from DS:BX
mov ax, [CS:BX]         ; Load from CS:BX with custom segment
mov ax, [w BX]          ; Word-sized access
mov ax, [b BP]          ; Byte-sized access from BP
```

**Syntax:** `[` [`SEGMENT` `:` ] (`BX` | `BP`) `]`

### Indexed Addressing

Access memory at the address in `BX` or `BP` plus an offset:

```asm
mov ax, [BX + 0x10]     ; Load from DS:BX with offset 16
mov ax, [BP - 4]        ; Load from SS:BP with offset -4
mov ax, [SS:BX + 100]   ; Load from SS:BX with offset 100
mov ax, [w CS:BX + 0x20]; Load from CS:BX with offset 32
```

**Syntax:** `[` [`SEGMENT` `:` ] (`BX` | `BP`) `+`|`-` `offset` `]`

---

## Instructions

Instructions follow the format:

```asm
MNEMONIC destination, source
```

All MiniArch instructions are supported. Instructions with multiple variants (e.g., `ldi4`, `ldi8`, `ldi16`) are automatically selected based on operand types.

### Instruction Categories

#### Data Movement

- `mov` - Move between registers, memory, and immediate values
- `lea` - Load effective address into a register
- `ldi4`, `ldi8`, `ldi16` - Load immediate values
- `ld`, `ldb`, `ldw` - Load from memory
- `st`, `stb`, `stw` - Store to memory

#### Arithmetic

- `add` - Add two registers
- `addi4`, `addi8`, `addi16` - Add immediate
- `sub` - Subtract two registers
- `subi4`, `subi8`, `subi16` - Subtract immediate
- `neg` - Negate a register

#### Comparison

- `cmp` - Compare two registers
- `cmpi4`, `cmpi8`, `cmpi16` - Compare with immediate

#### Bitwise Operations

- `and` - Bitwise AND
- `andi` - Bitwise AND with immediate
- `or` - Bitwise OR
- `ori` - Bitwise OR with immediate
- `xor` - Bitwise XOR
- `xori` - Bitwise XOR with immediate
- `not` - Bitwise NOT

#### Shift Operations

- `shl` - Shift left
- `shr` - Shift right

#### Control Flow

- `jmp` - Unconditional jump
- `jz`, `jnz` - Jump on zero / not zero
- `jc`, `jnc` - Jump on carry / no carry
- `jn`, `jnn` - Jump on negative / not negative
- `jo`, `jno` - Jump on overflow / no overflow
- `call` - Call subroutine
- `ret` - Return from subroutine
- `jmpf` - Far jump to different segment
- `callf` - Far call to different segment
- `retf` - Far return from different segment

#### Stack and Flags

- `push`, `pushw`, `pushb` - Push register values onto the stack
- `pop`, `popw`, `popb` - Pop values from the stack into registers
- `pushf`, `popf` - Push and pop the full flag byte
- `pusha`, `popa` - Push and pop `AX`, `BX`, `CX`, `DX`
- `stz`, `stc`, `stn`, `sto`, `sti`, `sta` - Set individual flags
- `clz`, `clc`, `cln`, `clo`, `cli`, `cla` - Clear individual flags

#### I/O and System

- `out` - Write a register value to an I/O port register
- `in` / `inp` - Read a value from an I/O port into a register
- `int` - Call a BIOS interrupt vector
- `halt` / `hlt` - Stop execution

#### Miscellaneous

- `nop`, `nop0`, `nop1`, `nopf` - No operation
- `halt` - Halt execution (emulator termination)

---

## Labels and Functions

### Labels

Labels mark positions in code and are used for jumps and references. A label is defined by placing an identifier followed by a colon:

```asm
loop:
    add ax, 1
    cmp ax, 10
    jnz loop
```

Labels can be used in immediate expressions to get their address:

```asm
jmp start_address   ; Jump to the label
```

### Functions

Functions are named scope blocks:

```asm
print {
    push bp
    mov bp, sp
    ; Function code here
    pop bp
    ret
}
```

**Syntax:** `IDENTIFIER` `{` statements... `}`

Functions provide:
- **Naming** - Makes code more readable
- **Scoping** - Local labels within the function
- **Jump targets** - Can jump to function entry point

### Scopes

Anonymous scopes can organize data or code:

```asm
{
    export int:
    .word 0x6502
    export string:
    .asciiz "Hello, World!\r\n"
}
```

---

## Constants

Constants define named values that can be used throughout the assembly:

```asm
BUFFER_SIZE = 256
MAX_ITEMS = 0x100

mov cx, BUFFER_SIZE
```

**Syntax:** `IDENTIFIER` `=` `expression`

Constants are evaluated at assembly time and can use any expression with operators:

```asm
PAGE_SIZE = 0x1000
PAGES = 16
TOTAL_SIZE = PAGE_SIZE * PAGES   ; = 0x10000
MASK = ~0xFF                      ; Bitwise NOT
```

### Expression Operators

Constants and immediate values support full expression evaluation:

| Operator | Precedence | Description |
|----------|------------|-------------|
| `~` | 1 | Bitwise NOT |
| `-` (unary) | 1 | Negation |
| `*`, `/`, `%` | 2 | Multiplication, Division, Modulo |
| `+`, `-` | 3 | Addition, Subtraction |
| `<<`, `>>` | 4 | Logical shifts |
| `&` | 5 | Bitwise AND |
| `^` | 6 | Bitwise XOR |
| `\|` | 7 | Bitwise OR |
| `()` | 0 | Grouping |

Example:
```asm
const ADDR = (0x10 + 0x20) * 0x100 & 0xFFFF
```

---

## Data Directives

The assembler supports several data directives for embedding data into the output binary.

- `.ascii` "string" - write a string without a terminating zero
- `.asciiz` "string" - write a null-terminated string
- `.byte` expr - write a single byte value
- `.bytes` expr* - write one or more bytes
- `.word` expr - write a 16-bit value
- `.double` expr - write a 32-bit value
- `.quad` expr - write a 64-bit value
- `.zero` expr - allocate zero-initialized bytes
- `.org` expr - set the current assembly location counter
- `.offset` expr - change the active address offset for scalars and labels
- `export` identifier / `export` label: / `export` function { ... } - expose symbols to parent scope

Data directives reserve space and initialize values in memory.

### Text - ASCII String

```asm
.ascii "Hello"          ; No null terminator
.asciiz "Hello"         ; With null terminator
```

The `.ascii` directive reserves space for a string without a terminating null byte. The `.asciiz` directive includes a null terminator, useful for C-style string handling.

### Numeric Data

```asm
.byte 0xFF              ; 8-bit value
.byte                   ; Reserve 1 byte (zero-initialized)

.word 0x1234            ; 16-bit value
.word                   ; Reserve 2 bytes (zero-initialized)

.double 0x12345678      ; 32-bit value
.double                 ; Reserve 4 bytes (zero-initialized)

.quad 0x123456789ABCDEF0; 64-bit value
.quad                   ; Reserve 8 bytes (zero-initialized)
```

**Syntax:**
- `.byte [expression]` - Define/reserve a byte
- `.word [expression]` - Define/reserve a word (16-bit)
- `.double [expression]` - Define/reserve a doubleword (32-bit)
- `.quad [expression]` - Define/reserve a quadword (64-bit)

If no expression is provided, the space is zero-initialized.

### Zero Padding

```asm
.zero 0x100            ; Reserve 256 zero-filled bytes
```

---

## Memory Layout Directives

### Origin

The `.org` directive sets the absolute assembly position in memory:

```asm
.org 0x0000            ; Start code at address 0x0000
    mov ax, 1
    
.org 0x1000            ; Jump to address 0x1000
    mov bx, 2
```

Memory between the previous position and the new `.org` position filled with 0.

### Offset

The `.offset` directive shifts the active address offset within the current scope, useful for organizing data sections:

```asm
{
    .offset 0x8000
    ; Symbols defined here use 0x8000 as the base offset
    message:
        .asciiz "Hello"
}
```

---

## Export and Visibility

The `export` directive marks symbols as visible to parent scope.

### Export Labels

```asm
export main:
    mov ax, 1
    ret
```

### Export Constants

```asm
export VERSION = 0x0100
```

### Export Functions

```asm
export entry {
    jmp main
}
```

### Export with Alias

Create an alternative name for a symbol:

```asm
export main -> _start   ; main is called as _start externally
```

---

## Examples

### Hello World with Print Function

```asm
; Hello World program in miniArch assembly

print {
    mov bx, msg
    mov ds, cs  
    mov dx, 0xFFFF        ; Serial port
    loop:
        mov ax, [b bx]    ; Load byte
        cmp ax, 0         ; Check for null
        jz done
        out dx, ax        ; Output character
        add bx, 1
        jmp loop
    done:
        ret
}

msg:
.asciiz "Hello, World!\r\n"

.org 0xFFF0
reset {
    jmpf 0xF000, 0
}
```

### Bitwise Operations

```asm
test {
    mov ax, 0xAA
    and ax, 0xCC          ; Bitwise AND with immediate
    
    mov bx, 0xCC
    or  bx, 0xAA          ; Bitwise OR with immediate
    
    mov cx, 0xAA
    xor cx, 0xCC          ; Bitwise XOR with immediate
    
    mov dx, 0xAA
    not dx                ; Bitwise NOT
    
    shl ax, 8             ; Shift left by value in CX
    shr dx, 8             ; Shift right by value in CX
    
    halt
}

.org 0xFFF0
reset {
    jmpf 0xF000, test
}
```

### Using Constants and Labels

```asm
const BUFFER_START = 0x2000
const BUFFER_SIZE = 256

copy_buffer {
    xor cx, cx            ; Counter = 0
    
copy_loop:
    cmp cx, BUFFER_SIZE
    jge copy_done
    
    mov ax, [DS:BX + cx]  ; Load from source
    mov [ES:BX + cx], ax  ; Store to destination
    
    add cx, 1
    jmp copy_loop
    
copy_done:
    ret
}
```

### Stack Operations

```asm
sum_array {
    ; Input: BX = array start, CX = count
    ; Output: AX = sum
    
    push bp
    mov bp, sp
    
    xor ax, ax            ; AX = accumulator (sum)
    xor dx, dx            ; DX = index
    
loop_start:
    cmp dx, cx            ; Check if done
    jge loop_end
    
    mov bx, [BP - 4]      ; Load array base from stack
    add bx, dx            ; Add index
    add ax, [bx]          ; Add element to sum
    
    add dx, 1             ; Increment index
    jmp loop_start
    
loop_end:
    pop bp
    ret
}
```

---

## Compiler Usage

### Command Line

```bash
python3 assembler/main.py source.asm [-o output.bin]
```

**Arguments:**
- `source.asm` - Required. Path to the assembly source file
- `-o`, `--output` - Optional. Output binary file path. If not specified, the output file will have the same name as the source but with `.bin` extension.

### Examples

```bash
# Compile hello_world.asm to hello_world.bin
python3 assembler/main.py examples/hello_world.asm

# Compile and specify output location
python3 assembler/main.py examples/hello_world.asm -o build/hello.bin

# Compile multiple files
python3 assembler/main.py examples/bitwise.asm -o build/bitwise.bin
python3 assembler/main.py examples/stack_test.asm -o build/stack_test.bin
```

### Error Messages

The assembler provides helpful error messages:

- **Syntax Errors** - Unexpected tokens or characters
- **Type Errors** - Invalid operand combinations
- **Range Errors** - Values out of valid range
- **Undefined Symbols** - References to undefined labels/constants

Each error message includes the line number and character position for easy debugging.

---

## Advanced Topics

### Memory Segmentation

MiniArch uses segmented memory with 4 segment registers (CS, DS, SS, ES). Each segment provides a 64KB address space:

```asm
; Set data segment to code segment
mov ds, cs

; Access memory in different segments
mov ax, [CS:0x1000]
mov bx, [DS:0x2000]
mov cx, [SS:0x3000]
```

### Reset Vector

The MiniArch CPU boots from address `FFFF:0000` (ROM), which should contain a far jump to the main program:

```asm
main {
    ; Program starts here
}

.org 0xFFF0              ; Reset vector location (physical: 0xFFFF0)
reset {
    jmpf 0x0000, main     ; Jump to main program
}
```

### Immediate Value Encoding

The assembler automatically selects the correct immediate encoding:
- Values 0-15 use 4-bit encoding (eg. `addi4`)
- Values 0-255 use 8-bit encoding (eg. `addi8`)
- Larger values use 16-bit encoding (eg. `addi16`)

This is handled automatically by the assembler.
