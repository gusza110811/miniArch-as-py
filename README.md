# MiniArch-AS-py

A Python-based assembler for the MiniArch 16-bit CPU architecture. This assembler translates MiniArch assembly language (`.asm` files) into executable binary code (`.bin` files) that can be run on the MiniArch emulator.

## Features

- Support for multiple numeric bases (binary, octal, decimal, hexadecimal)
- Character and string literals with escape sequences
- Labels and functions for control flow
- Constants and data directives
- Memory layout control
- Export and visibility controls
- "Comprehensive error" reporting with syntax "highlighting"

## Installation

Ensure you have Python 3.6+ installed. The assembler uses the Lark parsing library.

```bash
pip install lark
```

Every example down assume you aliased the assembler with option `--target ma` to `ma-as` as described in the Usage section below.

## Usage

```bash
ma-as <input_file.asm> [output_file.bin]
```

Make symlink of the assembler to anywhere on your path as `ma-as`

For example, at `~/.local/bin`:
```bash
ln -s ~/path/to/repo/main.py ~/.local/bin/ma-as
```
replace `~/path/to/repo/main.py` with the absolute path to main.py


### Command Line Options

- `input_file.asm`: The assembly source file to assemble
- `output_file.bin`: (Optional) The output binary file. Defaults to input filename with `.bin` extension.
If no output file is specified, it defaults to `<input_file_basename>.bin`.

## Syntax

The assembler supports a rich syntax for MiniArch assembly programming. Key elements include:

- **Instructions**: Standard MiniArch opcodes like `mov`, `add`, `jmp`, etc.
- **Registers**: 16-bit registers (`AX`, `BX`, etc.) and 8-bit registers (`AH`, `BH`, etc.)
- **Addressing Modes**: Direct, indirect, and indexed memory access
- **Directives**: `.data`, `.text`, `.org`, `.asciiz`, etc.
- **Labels**: For jumps and data references
- **Expressions**: Full arithmetic and logical expressions in operands

For complete syntax documentation, see [Assembly Documentation](doc/assembly.md).

## Examples

Assemble a hello world program:

```bash
ma-as examples/hello_world.asm
```

This produces `examples/hello_world.bin`, which can then be run in the emulator.

## Error Handling

The assembler provides detailed error messages with line numbers and character positions. Common errors include:

- Unexpected characters or tokens
- Unmatched braces or quotes
- Undefined labels or constants
- Invalid register or addressing mode combinations

Errors are displayed with color-coded output for easy debugging.

## Architecture

Built using:
- **Lark**: Parsing library with a formal grammar definition (`grammar.lark`)
- **Parser**: Converts source code to AST
- **Constructor**: Translates AST to machine code
- **Context**: Manages symbols, labels, and memory layout

## Contributing

I dont think there's much for you to contribute. feel free to just make a pull request though

## License

license later, normal copyright law applies
