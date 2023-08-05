import os
import pathlib
import filecmp


class File():

    def __init__(self, filename, current_dir, data_dir, finished_dir):
        self._filename = filename
        self._current_dir = current_dir
        self._data_dir = data_dir
        self._finished_dir = finished_dir

    @property
    def filename(self):
        return self._filename

    @property
    def filepath(self):
        return str(pathlib.PurePath(os.getcwd(),
                                    self._current_dir,
                                    self._filename))

    def finish(self):
        finished = pathlib.PurePath(
            os.getcwd(), self._finished_dir, self._filename)
        os.open(finished, os.O_CREAT | os.O_TRUNC)

    def process(self, visitor, ctx_obj=None):
        return_code = visitor.run(self, ctx_obj)

        if __debug__ and not return_code:
            raise AssertionError

        self.finish()

        print("{filename} finished - {return_code}".format(
            filename=self._filename,
            return_code=return_code
        ))


class FileIterator():

    def __init__(self, current_dir, data_dir, finished_dir, filenames):
        self._current_dir = current_dir
        self._data_dir = data_dir
        self._finished_dir = finished_dir
        self._filenames = filenames

    def __next__(self):
        if len(self._filenames) == 0:
            raise StopIteration()
        filename = self._filenames.pop()
        file = File(filename,
                    self._current_dir,
                    self._data_dir,
                    self._finished_dir)
        return file

    def __iter__(self):
        return self


class FileBench():

    def __init__(self, data_dir, finished_dir):
        self._data_dir = data_dir
        self._finished_dir = finished_dir

    def get_unprocessed_files(self):
        filenames = filecmp.dircmp(
            self._data_dir, self._finished_dir).left_only
        iterator = FileIterator(
            self._data_dir, self._data_dir, self._finished_dir, filenames)
        return iterator

    def get_processed_files(self):
        filenames = filecmp.dircmp(
            self._data_dir, self._finished_dir).common_files
        iterator = FileIterator(
            self._finished_dir, self._data_dir, self._finished_dir, filenames)
        return iterator