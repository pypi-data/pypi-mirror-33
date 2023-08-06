import os


class UploadChunks(object):
    def __init__(self, filename, chunk_size=1 << 15, progress_callback=None):
        self.filename = filename
        self.chunk_size = chunk_size
        self.progress_callback = progress_callback
        self.total_size = os.path.getsize(filename)
        self.readsofar = 0

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            if self.progress_callback:
                self.progress_callback(0)
            while True:
                data = file.read(self.chunk_size)
                if not data:
                    if self.progress_callback:
                        self.progress_callback(self.total_size)
                    break
                self.readsofar += len(data)
                if self.progress_callback:
                    self.progress_callback(self.readsofar)
                yield data

    def __len__(self):
        return self.total_size


class IterableToFileAdapter(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, size=-1):
        return next(self.iterator, b'')

    def __len__(self):
        return self.length
