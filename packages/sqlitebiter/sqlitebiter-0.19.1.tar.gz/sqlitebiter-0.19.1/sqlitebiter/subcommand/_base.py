# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

from simplesqlite import Model
from simplesqlite.query import And, Attr, Where
from sqliteschema import SQLiteSchemaExtractor

from .._common import ResultLogger
from .._const import MAX_VERBOSITY_LEVEL, PROGRAM_NAME, TABLE_NOT_FOUND_MSG_FORMAT
from .._counter import ResultCounter
from .._ipynb_converter import convert_nb
from .._table_creator import TableCreator


class SourceInfo(Model):
    source_id = "INTEGER NOT NULL"
    dir_name = "TEXT"
    base_name = "TEXT NOT NULL"
    format_name = "TEXT NOT NULL"
    dst_table = "TEXT NOT NULL"
    size = "INTEGER"
    mtime = "INTEGER"

    def get_name(self, verbosity_level):
        if verbosity_level == 0 or self.dir_name is None:
            return self.base_name

        return self.dir_name.joinpath(self.base_name)


class TableConverter(object):
    def __init__(self, logger, con, index_list, verbosity_level, format_name=None, encoding=None):
        self._logger = logger
        self._con = con
        self._index_list = index_list
        self._verbosity_level = verbosity_level
        self._format_name = format_name
        self._encoding = encoding

        self._schema_extractor = SQLiteSchemaExtractor(con)
        self._result_counter = ResultCounter()
        self._result_logger = ResultLogger(
            logger, self._schema_extractor, self._result_counter, self._verbosity_level
        )
        self._table_creator = TableCreator(
            logger=self._logger,
            dst_con=con,
            result_logger=self._result_logger,
            verbosity_level=verbosity_level,
        )

        SourceInfo.connection = con
        SourceInfo.hidden = True
        SourceInfo.create()

    def _fetch_source_id(self, source_info):
        where_list = [
            Where("base_name", source_info.base_name),
            Where("format_name", source_info.format_name),
        ]

        if source_info.dir_name:
            where_list.append(Where("dir_name", source_info.dir_name))
        if source_info.size is not None:
            where_list.append(Where("size", source_info.size))
        if source_info.mtime is not None:
            where_list.append(Where("mtime", source_info.mtime))

        return self._con.fetch_value(
            select=Attr("source_id"), table_name=SourceInfo.get_table_name(), where=And(where_list)
        )

    def _fetch_next_source_id(self):
        source_id = self._con.fetch_value(
            select="MAX({})".format("source_id"), table_name=SourceInfo.get_table_name()
        )

        if source_id is None:
            return 1

        return source_id + 1

    def get_return_code(self):
        return self._result_counter.get_return_code()

    def get_success_count(self):
        return self._result_counter.success_count

    def write_completion_message(self):
        logger = self._logger
        database_path_msg = "database path: {:s}".format(self._con.database_path)

        logger.debug("----- {:s} completed -----".format(PROGRAM_NAME))

        log_list = [
            "source={}".format(
                self._con.fetch_value(
                    select="COUNT(DISTINCT({}))".format("source_id"),
                    table_name=SourceInfo.get_table_name(),
                )
            )
        ]
        if self.get_success_count() > 0:
            log_list.append("success={}".format(self.get_success_count()))
        if self._result_counter.fail_count > 0:
            log_list.append("fail={}".format(self._result_counter.fail_count))
        if self._result_counter.skip_count > 0:
            log_list.append("skip={}".format(self._result_counter.skip_count))
        if self._result_counter.created_table_count > 0:
            log_list.append("created-table={}".format(self._result_counter.created_table_count))

        logger.info("converted results: {}".format(", ".join(log_list)))

        if self.get_success_count() > 0:
            output_format, verbosity_level = self.__get_dump_param()
            logger.info(database_path_msg)

            try:
                from textwrap import indent
            except ImportError:
                # for Python 2 compatibility
                def indent(value, _):
                    return value

            logger.debug(
                "----- database schema -----\n{}".format(
                    indent(
                        self._schema_extractor.dumps(
                            output_format=output_format, verbosity_level=verbosity_level
                        ),
                        "    ",
                    )
                )
            )
        else:
            logger.debug(database_path_msg)

    def _convert_nb(self, nb, source_info):
        success_count = self._result_counter.success_count
        created_table_set = convert_nb(
            logger=self._logger,
            source_info=source_info,
            con=self._con,
            result_logger=self._result_logger,
            nb=nb,
        )

        if self._result_counter.success_count == success_count:
            self._logger.warn(TABLE_NOT_FOUND_MSG_FORMAT.format(source_info.base_name))
            return

        return created_table_set

    def _convert_complex_json(self, json_loader, source_info):
        from .._dict_converter import DictConverter

        dict_converter = DictConverter(
            self._logger, self._table_creator, source_info=source_info, index_list=self._index_list
        )

        try:
            dict_converter.to_sqlite_table(json_loader.load_dict(), [])
        except AttributeError:
            pass

        return dict_converter.converted_table_name_set

    def __get_dump_param(self):
        found_ptw = True
        try:
            import pytablewriter  # noqa: W0611
        except ImportError:
            found_ptw = False

        if found_ptw:
            return ("rst_simple_table", self._verbosity_level)

        if self._verbosity_level >= 1:
            return ("text", MAX_VERBOSITY_LEVEL)

        if self._verbosity_level == 0:
            return ("text", 1)

        raise ValueError("invalid verbosity_level: {}".format(self._verbosity_level))
