#! /usr/bin/env python

import sys, time, string
from calendrical import *

def cal(m, y):
    sys.stdout.write('   %s %d\n' % (month_names[m], y))
    sys.stdout.write(' S  M Tu  W Th  F  S\n')
    fst = gregorian_to_rd(y, m, 1)
    sys.stdout.write('   ' * rd_to_day_of_week(fst))
    days = gregorian_last_day_of_month(y, m)
    for i in range(1, 1 + days):
        sys.stdout.write('%2d' % i)
        if rd_to_day_of_week(fst + i) != 0:
            sys.stdout.write(' ')
        else:
            sys.stdout.write('\n')
    if ((rd_to_day_of_week(fst) + days) / 7) < 5:
        sys.stdout.write('\n')
    sys.stdout.write('\n')

def main():
    if len(sys.argv[1:]) > 2:
        sys.stderr.write('usage: cal [ month [year] ]\n')
        sys.exit(1)
    (y, m) = time.localtime(time.time())[0:2]
    if len(sys.argv[1:]) >= 1:
        m = int(sys.argv[1])
    if len(sys.argv[1:]) >= 2:
        y = int(sys.argv[2])
    cal(m, y)

main()
