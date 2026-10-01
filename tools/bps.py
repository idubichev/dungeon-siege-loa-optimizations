"""Create and apply BPS patches.

BPS is the binary patch format used across the ROM-hacking community. A patch
is a list of four actions that rebuild the target file:

    SourceRead   copy bytes from the source at the current output offset
    TargetRead   insert literal bytes stored in the patch
    SourceCopy   copy bytes from anywhere in the source
    TargetCopy   copy bytes from earlier in the output

Unchanged code and relocated copies of the game's own functions are encoded as
SourceRead/SourceCopy, so the patch stores only new bytes. CRC32 checksums of
the source, target and patch close the file.

    python3 tools/bps.py create SOURCE TARGET PATCH
    python3 tools/bps.py apply  SOURCE PATCH TARGET
"""
import sys
import zlib

SOURCE_READ, TARGET_READ, SOURCE_COPY, TARGET_COPY = range(4)
MIN_COPY = 10          # shortest SourceCopy worth an action
MIN_READ = 4           # shortest in-place SourceRead worth an action
KEY = 6                # bytes hashed per index entry
STEP = 4               # index every STEP-th source offset


def _number(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(0x80 | byte)
            return bytes(out)
        out.append(byte)
        value -= 1


def _signed(value):
    return _number((abs(value) << 1) | (1 if value < 0 else 0))


def _read_number(data, pos):
    value, shift = 0, 1
    while True:
        byte = data[pos]
        pos += 1
        value += (byte & 0x7F) * shift
        if byte & 0x80:
            return value, pos
        shift <<= 7
        value += shift


def create(source, target, metadata=b""):
    # Index every STEP-th source position; a lookup tries each alignment, so
    # any match of KEY + STEP - 1 bytes or more is found.
    index = {}
    for i in range(0, len(source) - KEY + 1, STEP):
        index.setdefault(source[i:i + KEY], []).append(i)

    out = bytearray(b"BPS1")
    out += _number(len(source)) + _number(len(target)) + _number(len(metadata)) + metadata
    literal = bytearray()
    source_rel = 0
    pos = 0

    def flush():
        nonlocal literal
        if literal:
            out.extend(_number(((len(literal) - 1) << 2) | TARGET_READ))
            out.extend(literal)
            literal = bytearray()

    while pos < len(target):
        run = 0
        while (pos + run < len(target) and pos + run < len(source)
               and source[pos + run] == target[pos + run]):
            run += 1
        if run >= MIN_READ:
            flush()
            out.extend(_number(((run - 1) << 2) | SOURCE_READ))
            pos += run
            continue

        best_len, best_at = 0, 0
        candidates = []
        for k in range(STEP):
            for at in index.get(target[pos + k:pos + k + KEY], ())[:16]:
                if at - k >= 0:
                    candidates.append(at - k)
        for at in candidates:
            n = 0
            while (pos + n < len(target) and at + n < len(source)
                   and source[at + n] == target[pos + n]):
                n += 1
            if n > best_len:
                best_len, best_at = n, at
        if best_len >= MIN_COPY:
            flush()
            out.extend(_number(((best_len - 1) << 2) | SOURCE_COPY))
            out.extend(_signed(best_at - source_rel))
            source_rel = best_at + best_len
            pos += best_len
            continue

        literal.append(target[pos])
        pos += 1
    flush()

    out += zlib.crc32(source).to_bytes(4, "little")
    out += zlib.crc32(target).to_bytes(4, "little")
    out += zlib.crc32(bytes(out)).to_bytes(4, "little")
    return bytes(out)


def literals(patch):
    """Yield (output_offset, bytes) for every TargetRead action in a patch."""
    pos = 4
    _, pos = _read_number(patch, pos)
    target_size, pos = _read_number(patch, pos)
    meta, pos = _read_number(patch, pos)
    pos += meta
    out = 0
    end = len(patch) - 12
    while pos < end:
        data, pos = _read_number(patch, pos)
        action, length = data & 3, (data >> 2) + 1
        if action == TARGET_READ:
            yield out, patch[pos:pos + length]
            pos += length
        elif action in (SOURCE_COPY, TARGET_COPY):
            _, pos = _read_number(patch, pos)
        out += length


def apply(source, patch):
    if patch[:4] != b"BPS1":
        raise ValueError("not a BPS patch")
    if zlib.crc32(patch[:-4]) != int.from_bytes(patch[-4:], "little"):
        raise ValueError("patch file is corrupt")
    if zlib.crc32(source) != int.from_bytes(patch[-12:-8], "little"):
        raise ValueError("source file does not match this patch")
    pos = 4
    source_size, pos = _read_number(patch, pos)
    target_size, pos = _read_number(patch, pos)
    meta, pos = _read_number(patch, pos)
    pos += meta
    if source_size != len(source):
        raise ValueError("source file size does not match this patch")
    target = bytearray()
    source_rel = target_rel = 0
    end = len(patch) - 12
    while pos < end:
        data, pos = _read_number(patch, pos)
        action, length = data & 3, (data >> 2) + 1
        if action == SOURCE_READ:
            target += source[len(target):len(target) + length]
        elif action == TARGET_READ:
            target += patch[pos:pos + length]
            pos += length
        else:
            offset, pos = _read_number(patch, pos)
            offset = -(offset >> 1) if offset & 1 else offset >> 1
            if action == SOURCE_COPY:
                source_rel += offset
                target += source[source_rel:source_rel + length]
                source_rel += length
            else:
                target_rel += offset
                for _ in range(length):
                    target.append(target[target_rel])
                    target_rel += 1
    if len(target) != target_size or zlib.crc32(target) != int.from_bytes(patch[-8:-4], "little"):
        raise ValueError("patched output failed its checksum")
    return bytes(target)


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] not in ("create", "apply"):
        sys.exit(__doc__)
    a, b, c = (open(p, "rb").read() if i < 2 else p for i, p in enumerate(sys.argv[2:]))
    if sys.argv[1] == "create":
        result = create(a, b)
    else:
        result = apply(a, b)
    open(c, "wb").write(result)
    print(f"wrote {c} ({len(result):,} bytes)")
