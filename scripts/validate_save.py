"""Validate a DSP save file for common issues that cause 'invalid save file' errors.

Usage: python3 validate_save.py <path_to_.dsv>
"""
import struct, sys, os


def validate(path):
    if not os.path.isfile(path):
        print(f'ERROR: File not found: {path}')
        return False

    file_size = os.path.getsize(path)
    print(f'File: {path}')
    print(f'Size: {file_size} bytes')
    print()

    with open(path, 'rb') as f:
        data = f.read()

    ok = True

    # 1. Magic bytes
    magic = data[:6]
    if magic == b'VFSAVE':
        print(f'  [OK] Magic: {magic}')
    else:
        print(f'  [FAIL] Magic: {magic!r} (expected b\'VFSAVE\')')
        ok = False

    # 2. fileLength matches actual file size
    file_length = struct.unpack('<q', data[6:14])[0]
    if file_length == file_size:
        print(f'  [OK] fileLength ({file_length}) == actual file size ({file_size})')
    else:
        print(f'  [FAIL] fileLength ({file_length}) != actual file size ({file_size})')
        ok = False

    # 3. Save version
    version = struct.unpack('<i', data[14:18])[0]
    print(f'  [INFO] Save format version: {version}')

    # 4. Game version
    major = struct.unpack('<i', data[20:24])[0]
    minor = struct.unpack('<i', data[24:28])[0]
    release = struct.unpack('<i', data[28:32])[0]
    build = struct.unpack('<i', data[32:36])[0]
    print(f'  [INFO] Game version: {major}.{minor}.{release}.{build}')

    # 5. PNG screenshot present
    png_offset = data.find(b'\x89PNG')
    if png_offset >= 0:
        print(f'  [OK] PNG screenshot found at offset {png_offset}')
    else:
        print(f'  [WARN] PNG screenshot not found')

    # 6. File naming convention
    basename = os.path.basename(path)
    if basename.startswith('_') and basename.endswith('.dsv'):
        if basename[:-4].endswith('_'):
            print(f'  [OK] File name "{basename}" follows DSP convention (_name_.dsv)')
        else:
            print(f'  [WARN] File name "{basename}" should end with underscore: _name_.dsv')
    else:
        print(f'  [FAIL] File name "{basename}" must start with _ and end with _.dsv')
        print(f'         Example: _Indot_.dsv, _auto_0_.dsv, _lastexit_.dsv')
        ok = False

    print()
    if ok:
        print('=== SAVE FILE LOOKS VALID ===')
    else:
        print('=== SAVE FILE HAS ISSUES — see above ===')
    return ok


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 validate_save.py <path_to_.dsv>')
        sys.exit(1)
    validate(sys.argv[1])
