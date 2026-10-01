"""DS1 tank reader, based on Scott Bilas's published TankStructure.h."""
from pathlib import Path, PurePosixPath
import datetime, mmap, struct, uuid, zlib

class Tank:
    def __init__(self, path):
        self.path = Path(path)
        self.stream = self.path.open('rb')
        self.data = mmap.mmap(self.stream.fileno(), 0, access=mmap.ACCESS_READ)
        assert self.data[:8] == b'DSigTank', self.path
        self.dirs_at, self.files_at, self.index_size, self.data_at = self.unpack('4I', 12)
        self.priority = self.unpack('I', 52)[0]
        self.dirs = {}
        for offset in self.offsets(self.dirs_at):
            parent, count = self.unpack('2I', self.dirs_at + offset)
            name, end = self.string(self.dirs_at + offset + 16)
            self.dirs[offset] = (parent, name)
        self.files = {}
        for offset in self.offsets(self.files_at):
            at = self.files_at + offset
            parent, size, data, crc, timestamp, fmt, flags = self.unpack('4IQ2H', at)
            name, end = self.string(at + 28)
            path = '/'.join(filter(None, [self.directory(parent), name]))
            self.files[path] = dict(size=size, data=data, crc=crc, format=fmt, flags=flags, header=end)

    def unpack(self, fmt, at):
        return struct.unpack_from('<' + fmt, self.data, at)

    def offsets(self, at):
        count = self.unpack('I', at)[0]
        return self.unpack(str(count) + 'I', at + 4)

    def string(self, at):
        length = self.unpack('H', at)[0]
        return self.data[at + 2:at + 2 + length].decode('cp1252'), at + ((length + 6) & ~3)

    def directory(self, offset):
        if not offset:
            return ''
        parent, name = self.dirs[offset]
        return '/'.join(filter(None, [self.directory(parent) if parent else '', name]))

    def read(self, path):
        f = self.files[path]
        if not f['size'] or f['flags'] & 0x8000:
            return b''
        at = self.data_at + f['data']
        if f['format'] == 0:
            result = self.data[at:at + f['size']]
        else:
            assert f['format'] == 1, (path, f['format'])
            compressed, chunk_size = self.unpack('2I', f['header'])
            if not chunk_size:
                result = zlib.decompress(self.data[at:at + compressed])
            else:
                chunks = []
                for i in range((f['size'] + chunk_size - 1) // chunk_size):
                    uncompressed, compressed, extra, offset = self.unpack('4I', f['header'] + 8 + 16 * i)
                    raw = self.data[at + offset:at + offset + compressed]
                    chunk = zlib.decompress(raw) if uncompressed != compressed else raw
                    chunks.append(chunk + self.data[at + offset + compressed:at + offset + compressed + extra])
                result = b''.join(chunks)
        assert len(result) == f['size'], (path, len(result), f['size'])
        assert zlib.crc32(result) == f['crc'], (path, 'CRC mismatch')
        return result

def write_tank(destination, files, reference, title):
    """Write a new uncompressed user tank; never rewrite a game archive."""
    def pack(fmt, *values):
        return struct.pack('<' + fmt, *values)
    def name(text):
        raw = text.encode('ascii')
        result = pack('H', len(raw)) + raw + b'\0'
        return result + b'\0' * (-len(result) % 4)
    filetime = int((datetime.datetime.now(datetime.timezone.utc).timestamp() + 11644473600) * 10000000)
    paths = sorted(files)
    assert all(str(PurePosixPath(x)) == x and '..' not in PurePosixPath(x).parts and not x.startswith('/') for x in paths)
    dirs = {''}
    for path in paths:
        dirs.update(str(x) for x in PurePosixPath(path).parents if str(x) != '.')
    dirs = sorted(dirs)
    parent = lambda path: '' if str(PurePosixPath(path).parent) == '.' else str(PurePosixPath(path).parent)
    children = {d: sorted([x for x in dirs if x and parent(x) == d] + [x for x in paths if parent(x) == d], key=lambda x: PurePosixPath(x).name) for d in dirs}
    offsets, cursor = {}, 4 + 4 * len(dirs)
    for d in dirs:
        offsets[d] = cursor
        cursor += 16 + len(name(PurePosixPath(d).name)) + 4 * len(children[d])
    dir_size = cursor
    file_offsets, cursor = {}, 4 + 4 * len(paths)
    for path in paths:
        file_offsets[path] = cursor
        cursor += 28 + len(name(PurePosixPath(path).name))
    directory = pack('I', len(dirs)) + pack(str(len(dirs)) + 'I', *[offsets[d] for d in dirs])
    for d in dirs:
        directory += pack('2IQ', offsets[parent(d)] if d else 0, len(children[d]), filetime) + name(PurePosixPath(d).name)
        directory += pack(str(len(children[d])) + 'I', *[offsets[x] if x in offsets else dir_size + file_offsets[x] for x in children[d]])
    assert len(directory) == dir_size
    file_index = pack('I', len(paths)) + pack(str(len(paths)) + 'I', *[file_offsets[x] for x in paths])
    data = bytearray()
    for path in paths:
        raw = files[path]
        file_index += pack('4IQ2H', offsets[parent(path)], len(raw), len(data), zlib.crc32(raw), filetime, 0, 0) + name(PurePosixPath(path).name)
        data += raw
        data += b'\0' * (-len(data) % 8)
    header = bytearray(804)
    header[:52] = Tank(reference).data[:52]
    struct.pack_into('<4I', header, 12, len(header) + len(data), len(header) + len(data) + len(directory), len(directory) + len(file_index), len(header))
    struct.pack_into('<II4s', header, 52, 0x4001, 0, b'RESU')
    header[64:80] = uuid.uuid4().bytes_le
    struct.pack_into('<2I', header, 80, zlib.crc32(directory + file_index), zlib.crc32(data))
    now = datetime.datetime.now(datetime.timezone.utc)
    struct.pack_into('<8H', header, 88, now.year, now.month, (now.weekday() + 1) % 7, now.day, now.hour, now.minute, now.second, 0)
    for offset, width, text in [(104, 100, 'Personal mod for licensed Dungeon Siege'), (304, 100, 'Uncompressed user tank'), (504, 100, title), (704, 40, 'Ivan')]:
        raw = text[:width - 1].encode('utf-16le')
        header[offset:offset + len(raw)] = raw
    Path(destination).write_bytes(header + data + directory + file_index)
    check = Tank(destination)
    assert set(check.files) == set(files)
    for path, raw in files.items():
        assert check.read(path) == raw

if __name__ == '__main__':
    import sys
    tank = Tank(sys.argv[1])
    if len(sys.argv) == 2:
        for path in tank.files:
            print(path)
    else:
        root = Path(sys.argv[2])
        for path in tank.files:
            if Path(path).suffix.lower() in ('.gas', '.skrit'):
                dest = root / path
                assert dest.resolve().is_relative_to(root.resolve())
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(tank.read(path))
        print(tank.path.name, len(tank.files), 'entries; priority', tank.priority)
