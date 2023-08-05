import os
import pathlib
import io


ETC_DIR = "/etc/irk"
if not os.path.exists(ETC_DIR):
    os.makedirs(ETC_DIR, 0o777, True)

ETC_PATH = pathlib.Path(ETC_DIR)


class EtcFile:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.fullpath = ETC_PATH.joinpath(self.path)

    def open(self, *args, **kwargs):
        return self.fullpath.open(*args, **kwargs)

    def makedir(self):
        if not self.fullpath.exists():
            os.makedirs(self.fullpath.as_posix())


class FileConcat(io.BufferedIOBase):
    def __init__(self, files, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = files
        self.last_file = 0

    def readable(self, *args, **kwargs):
        return True

    def read1(self, n=None):
        if self.last_file >= len(self.files):
            return b""
        else:
            result = self.files[self.last_file].read(n)
            if n is None or n > 0:
                self.last_file += 1
            return bytes(result, encoding="ascii")

    def close(self, *args, **kwargs):
        for i in self.files:
            i.close()


class EtcConcatDir(EtcFile):
    def __init__(self, path):
        super().__init__(path)

    def open(self):
        self.makedir()
        files = os.listdir(self.fullpath.as_posix())
        files.sort()
        return io.TextIOWrapper(FileConcat([self.fullpath.joinpath(x).open("r") for x in files]))
