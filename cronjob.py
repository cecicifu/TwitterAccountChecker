#!/usr/bin/python3
# coding: utf-8

# Important: Cron only works for Unix-like operating systems and as root

from crontab import CronTab
from sys import platform
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-U", "--username", required=True)
parser.add_argument("-H", "--headless", action='store_true', default=False)
parser.add_argument("-P", "--proxy", action='store_true', default=False)
args = parser.parse_args()

if platform != "linux":
    raise ValueError("Cron only works for Unix-like operating systems")

cron = CronTab(user='root')

if args.proxy:
    job = cron.new(
        command='py account_checker.py -U %s -H -P' % args.username)
else:
    job = cron.new(command='py account_checker.py -U %s -H' %
                   args.username)


# https://crontab.guru/#0_12_15_*_*
job.hour.on(12)
job.minute.on(00)
job.month.on(15)


if job.is_valid() and job.is_enabled():
    cron.write()
