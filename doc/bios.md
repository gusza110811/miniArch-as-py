# MiniArch BIOS interface definition

## Table of Contents

...

## The BIOS
- Located at F0000-FFFFF
- May use memory at `E8000`-`EFFFF` for its own data

## Boot process
- Check if Disk 0 exists by querying the disk controller
- Fail boot if it does not exist
- Otherwise load the first sector into `07C00`
- Set up interrupt vector table with serial console service (0x14)
- Then Far Jump to `0000:7C00`
- Segment registers reset to 0
- GPRs and stack registers are not reset by the BIOS; the bootloader is responsible for initialization

## Services

### Disk Service
- interrupt id `0x13`
- note: not all disk features have been implemented **yet**

#### Get Status
- `DX` = 0
- status returned in `AX`

#### Read Sector
- `DX` = 1
- `BX` <- start of 512 bytes buffer to store data read from sector
- `AX` -> status (0 = success)

#### Write Sector
- `DX` = 2
- `BX` <- start of 512 bytes data to write into sector
- `AX` -> status (0 = success)

#### Set Sector
- `DX` = 4
- `AX` <- lower 16 bit of sector
- `CX` <- upper 16 bit of sector

### Serial Console Service
- interrupt id `0x14`

#### Put Character
- `DX` = 1
- `AX` <- character

#### Get Character
- `DX` = 2
- `AX` -> character
