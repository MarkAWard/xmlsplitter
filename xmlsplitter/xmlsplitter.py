from math import log10
import os
from pathlib import Path
from xml.parsers.expat import ParserCreate
from xml.sax.saxutils import escape, quoteattr


# How much data we process at a time
CHUNK_SIZE = 1024 * 1024

# From how much should we start another file
MAX_SIZE = 1024 * 1024  # 1Mb


class File(object):
    def __init__(self, name, mode, **kwargs):
        self.fp = open(name, mode, **kwargs)
        self.size = 0

    def write(self, data):
        self.size += len(data)
        self.fp.write(data.encode("utf-8"))

    def close(self):
        self.fp.close()

    def __len__(self):
        return self.size


class RotatingFile(object):
    def __init__(self, filepath, out_dir, max_size):
        self.out_dir = self._output_dir(filepath, out_dir)
        root, ext = self._file_parts(filepath)
        self.file_root = root
        self.file_ext = ext

        size = os.path.getsize(filepath) / max_size
        self.fmt = ".%%0%dd" % (int(log10(size)) + 1)

        self.file_idx = 0
        self.file = None
        self.roll()

    def _output_dir(self, filepath, out_dir):
        if out_dir is not None:
            Path(out_dir).mkdir(parents=True, exist_ok=True)
            return out_dir
        file_dir, _ = os.path.split(filepath)
        return file_dir

    def _file_parts(self, filepath):
        filename = os.path.split(filepath)[-1]
        return os.path.splitext(filename)

    @property
    def _fname(self):
        filename = f"{self.file_root}{self.fmt % self.file_idx}{self.file_ext}"
        return os.path.join(self.out_dir, filename)

    def roll(self):
        if self.file is not None:
            self.file.close()
            self.file_idx += 1
        self.file = File(self._fname, "wb")

    @property
    def size(self):
        return len(self.file)

    def write(self, data):
        self.file.write(data)

    def close(self):
        self.file.close()


class XMLSplitParser(object):
    def __init__(self, filepath, out_dir=None, max_size=MAX_SIZE, tree_depth=None):
        self.max_size = max_size
        self.tree_depth = tree_depth
        self.path = []

        self.parser = ParserCreate()
        self.parser.ordered_attributes = 1
        self.parser.XmlDeclHandler = self.XmlDeclHandler
        self.parser.StartElementHandler = self.StartElementHandler
        self.parser.EndElementHandler = self.EndElementHandler
        self.parser.CharacterDataHandler = self.CharacterDataHandler

        self.filepath = filepath
        self.file = RotatingFile(filepath, out_dir, max_size)

    def XmlDeclHandler(self, version, encoding, standalone):
        decl = ["version", version, "encoding", encoding]
        if standalone != -1:
            decl.extend(["standalone", "yes" if standalone else "no"])
        attrs = self.fmt_attrs(decl)
        self.xml_declaration = f"<?xml{attrs}?>\n"
        self.file.write(self.xml_declaration)

    def _start(self, name, attrs):
        element = f"<{name}{self.fmt_attrs(attrs)}>"
        self.file.write(element)

    def StartElementHandler(self, name, attrs):
        self.push(name, attrs)
        self._start(name, attrs)

    def _end(self, name):
        element = f"</{name}>"
        self.file.write(element)

    def EndElementHandler(self, name):
        self.pop()
        self._end(name)
        if self.should_roll_file():
            self.roll()

    def CharacterDataHandler(self, data):
        self.file.write(escape(data))

    def fmt_attrs(self, attrs):
        fmt = lambda tup: f"{tup[0]}={quoteattr(tup[1])}"
        keys = attrs[::2]
        values = attrs[1::2]
        return " " + " ".join(map(fmt, zip(keys, values))) if attrs else ""

    def push(self, name, attrs):
        self.path.append((name, attrs))

    def pop(self):
        return self.path.pop()

    def should_roll_file(self):
        mx_buffer = self.max_size * 0.95
        cur_size = self.file.size
        depth = len(self.path) == self.tree_depth if self.tree_depth else True
        return cur_size >= mx_buffer and depth

    def roll(self):
        self.add_path_end_elements()
        self.file.roll()
        self.add_path_start_elements()

    def add_path_end_elements(self):
        for name, _ in reversed(self.path):
            self._end(name)

    def add_path_start_elements(self):
        self.file.write(self.xml_declaration)
        for name, attrs in self.path:
            self._start(name, attrs)

    def parse(self, chunk_size=CHUNK_SIZE):
        with open(self.filepath, "r", encoding="ISO-8859-1") as fp:
            while True:
                # Read a chunk
                chunk = fp.read(chunk_size)
                if len(chunk) < CHUNK_SIZE:
                    # tell the parser we're done
                    self.parser.Parse(chunk, 1)
                    break
                # process the chunk
                p.Parse(chunk)
        self.file.close()
