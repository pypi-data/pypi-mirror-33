#! /usr/bin/env python
# coding: utf-8
__author__ = '鹛桑够'


def print_table(t):
    def char_len(c):
        return len(c)

    def calc_tab(l, down=False):
        n = l / 8
        if l % 8 != 0 and down is False:
            n += 1
        return n
    max_len = []
    for line in t:
        for i in range(len(line)):
            l_c = char_len(line[i])
            if i >= len(max_len):
                max_len.append(l_c)
            elif l_c > max_len[i]:
                max_len[i] = l_c
    tabs = []
    for m_item in max_len:
        tabs.append(calc_tab(m_item) + 1)
    for line in t:
        line_s = []
        for i in range(len(line)):
            p_s = line[i] + "\t" * (tabs[i] - calc_tab(char_len(line[i]), down=True))
            line_s.append(p_s)
        print("".join(line_s))