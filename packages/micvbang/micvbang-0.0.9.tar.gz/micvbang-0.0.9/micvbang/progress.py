from .io import open_file


class ProgressTracker(object):
    def __init__(self, it, get_id, fpath=None, flush_freq=1000):
        self.skips = 0
        self._get_id = get_id
        self._it = it

        self._ids = set()

        self._flush_freq = flush_freq

        self._fpath = fpath
        if fpath is None:
            self._fpath = 'progress.gz'

        try:
            with open_file(self._fpath, 'rt') as f:
                self._ids = set(f.read().split('\n'))
        except FileNotFoundError:
            pass

    def iter(self):
        with open_file(self._fpath, 'at') as f:
            for i, data in enumerate(self._it):
                id = self._get_id(data)
                if id in self._ids:
                    self.skips += 1
                    if self.skips % 1000 == 0:
                        print(" ... skipped {} ...".format(self.skips))
                    continue

                yield data
                self._ids.add(id)
                f.write("{}\n".format(id))

                if i % self._flush_freq == 0:
                    f.flush()
