# -*- coding: utf-8 -*-
import argparse
import os
import sys
import time
from os.path import dirname
from log4python.Log4python import log
import traceback
from unipath import Path

from toolkits.system.shellHelper import exec_shell_with_pipe, file_is_used

path_cur = os.path.dirname(os.path.realpath(__file__))
path_parent = "%s/../" % path_cur
sys.path.append(path_parent)
# from system.shellHelper import exec_shell_with_pipe, file_is_used

reload(sys)
logger = log("HiveCmd")
sys.setdefaultencoding('utf8')


class HiveCmd:
    def __init__(self, file_name, sql, db_name, yarn_queue):
        self.file_name = file_name
        self.sql = sql
        self.hive_hql_file = "%s.hql" % self.file_name
        self.hive_err_file = "%s.err" % self.file_name
        # "use sec_ods;\nset mapred.job.queue.name=root.anquanbu-yewuanquanbu.default; "
        self.hive_info = "use %s;\nset mapred.job.queue.name=%s; \n" % (db_name, yarn_queue)
        logger.debug("HiveCmd:filename[%s]; sql[%s]" % (self.file_name, self.sql))

        path_to_check = dirname(self.file_name)
        if not Path(path_to_check).exists():
            Path(path_to_check).mkdir(True)

    def query(self):
        hql_content = self.hive_info + "%s"
        hql_cmd = "nohup hive -f %s 2> %s > %s &"
        Path(self.hive_hql_file).write_file(hql_content % self.sql)
        cmd = hql_cmd % (self.hive_hql_file, self.hive_err_file, self.file_name)
        exec_shell_with_pipe(cmd)

    def query_is_finished(self):
        return file_is_used(self.file_name)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("fileName", type=str, help="specify the sql output file's path")
        parser.add_argument("sql", type=str, help="specify the sql to query")
        args = parser.parse_args()

        hive_cmd = HiveCmd(args.fileName, args.sql, "sec_ods", "root.anquanbu-yewuanquanbu.default")
        hive_cmd.query()
        while True:
            if hive_cmd.query_is_finished():
                break
            else:
                time.sleep(1)
    except Exception, ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())
