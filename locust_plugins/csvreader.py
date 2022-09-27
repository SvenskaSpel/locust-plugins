import csv


class CSVReader:
    "Read test data from csv file using an iterator"

    def __init__(self, file, **kwargs):
        try:
            file = open(file)
        except TypeError:
            pass  # "file" was already a pre-opened file-like object
        self.file = file
        self.reader = csv.reader(file, **kwargs)

    def __next__(self):
        try:
            return next(self.reader)
        except StopIteration:
            # reuse file on EOF
            self.file.seek(0, 0)
            return next(self.reader)


class CSVDictReader:
    "Read test data from csv file using an iterator"

    def __init__(self, file, **kwargs):
        try:
            file = open(file)
        except TypeError:
            pass  # "file" was already a pre-opened file-like object
        self.file = file
        self.reader = csv.DictReader(file, **kwargs)

    def __next__(self):
        try:
            return next(self.reader)
        except StopIteration:
            # reuse file on EOF
            self.file.seek(0, 0)
            next(self.reader)  # skip header line
            return next(self.reader)
