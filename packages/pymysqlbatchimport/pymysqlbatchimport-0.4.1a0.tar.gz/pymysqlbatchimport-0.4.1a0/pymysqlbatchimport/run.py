import os
import shutil
import configparser
import inspect
import pathlib

from .mysqlimport import LoadDataInFile
from .file import FileBench


class App():

    DEFAULT_CONFIG_FILE = "import.cnf"
    DEFAULT_DATA_DIR = "data"
    DEFAULT_CACHED_DIR = "cached"
    DEFAULT_FINISHED_DIR = "finished"

    SCRIPT_CMD = "cmd"
    SCRIPT_HOST = "host"
    SCRIPT_USER = "user"
    SCRIPT_PASSWORD = "password"
    SCRIPT_DB_TABLE = "db_table"
    SCRIPT_DB_DBNAME = "db_dbname"
    SCRIPT_DATA_DIR = 'data_dir'
    SCRIPT_CACHE_DIR = 'cache_dir'
    SCRIPT_FINISHED_DIR = 'finished_dir'

    CNF_SCRIPT = "SCRIPT"
    CNF_MYSQLIMPORT = "MYSQLIMPORT"
    CNF_LOAD_DATA_INFILE = "LOAD_DATA_INFILE"

    @staticmethod
    def run(cnf_file=DEFAULT_CONFIG_FILE):

        cnf_parser = configparser.ConfigParser()
        cnf_parser.read(cnf_file)

        cnf_script = cnf_parser[App.CNF_SCRIPT]
        cnf_load_data_infile = cnf_parser[App.CNF_LOAD_DATA_INFILE]

        visitor = LoadDataInFile(
            cnf_script[App.SCRIPT_CACHE_DIR],
            cnf_script[App.SCRIPT_DB_DBNAME],
            cnf_script[App.SCRIPT_DB_TABLE],
            cnf_load_data_infile
        )

        filebench = FileBench(
            cnf_script[App.SCRIPT_DATA_DIR],
            cnf_script[App.SCRIPT_FINISHED_DIR])

        iterator = iter(filebench.get_unprocessed_files())

        with LoadDataInFile.context(
            host=cnf_script[App.SCRIPT_HOST],
            database=cnf_script[App.SCRIPT_DB_DBNAME],
            user=cnf_script[App.SCRIPT_USER],
            password=cnf_script[App.SCRIPT_PASSWORD],
            autocommit=True,
            allow_local_infile=True
        ) as ctx_obj:
            for file in iterator:
                file.process(visitor, ctx_obj)

    @staticmethod
    def prepare():
        os.mkdir(App.DEFAULT_DATA_DIR)
        os.mkdir(App.DEFAULT_CACHED_DIR)
        os.mkdir(App.DEFAULT_FINISHED_DIR)

        module = inspect.getfile(App)
        module_path = os.path.dirname(module)

        import_cnf = pathlib.PurePath(module_path, App.DEFAULT_CONFIG_FILE)

        shutil.copy(import_cnf, App.DEFAULT_CONFIG_FILE)
