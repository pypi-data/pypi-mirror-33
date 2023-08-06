# -*- coding: utf-8 -*-
import argparse
import os
import re
import sys
import traceback
import subprocess
import arrow
import thread
from threading import Timer

import time
from log4python.Log4python import log
from multiprocessing import Process, current_process

reload(sys)
logger = log("utils_time")
sys.setdefaultencoding('utf8')


def run_with_timeout(timeout, default, f, *args, **kwargs):
    if not timeout:
        return f(*args, **kwargs)
    timeout_timer = Timer(timeout, thread.interrupt_main)
    try:
        timeout_timer.start()
        result = f(*args, **kwargs)
        return result
    except KeyboardInterrupt:
        return default
    finally:
        timeout_timer.cancel()


def exec_cmd(cmd, work_path):
    exec_shell_with_pipe(cmd, work_path=work_path)


def worker(cmd, work_path):
    p = Process(target=exec_cmd, args=(cmd, work_path))
    p.start()
    os._exit(1)


def exec_external_cmd_background(cmd, work_path=""):
    p = Process(target=worker, args=(cmd, work_path))
    p.start()
    p.join()


def file_is_used(monitor_file):
    # fuser or lsof to check file's status
    cmd = "lsof %s" % monitor_file
    ret = exec_shell_with_pipe(cmd)
    if not ret:
        return True
    else:
        return False


def exec_shell_with_pipe(cmd, timeout=0, work_path=""):
    """exeShellWithPipe("grep 'processor' /proc/cpuinfo | sort -u | wc -l")
    :param work_path:
    :param timeout:
    :param cmd:  exec command
    """
    result = []
    none_num = 0
    if cmd == "" or cmd is None:
        return "No Cmd Input"
    if work_path == "":
        scan_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        scan_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work_path)
    while True:
        if none_num > 3:
            break
        if timeout != 0:
            ret = run_with_timeout(timeout, None, scan_process.stdout.readline)
        else:
            ret = scan_process.stdout.readline()
        if ret == "" or ret is None:
            none_num += 1
        else:
            result.append(ret.strip())
            none_num = 0
    return result


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("logFile", type=str, help="specify the log file's path")
        args = parser.parse_args()
        print(args.logFile)
    except Exception, ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())