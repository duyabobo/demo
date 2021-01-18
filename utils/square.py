#! /usr/bin/env python
# -*- coding: utf-8 -*- 
# 开平方
import time


class NumberNode(object):
    def __init__(self, num):
        self.num = num
        self.square_result = 0
        self.current_target_number = 0
        self.square_result_str = ''
        self.finished = False

    @property
    def data_list(self):
        """对num从低位向高位，每两位划分在一起，对num拆分成数组。
        这么拆分的原因是，每次求根号的下一位，最大不会超过一百，所以向下获取两位用来求的开平方的下一位"""
        number = self.num
        divisor = 100
        _data_list = []
        while number:
            remainder = number % divisor
            _data_list.append(remainder)
            number = number / divisor
        return _data_list

    @property
    def data_list_len(self):
        return len(self.data_list)

    def get_target_number(self, index):
        if index < self.data_list_len:
            return self.data_list[self.data_list_len-1-index]
        return 0

    def get_reducer(self, index_ret):
        return (self.square_result * 10 * 2 + index_ret) * index_ret

    def reload_result(self, index_ret):
        self.square_result = self.square_result * 10 + index_ret
        ret_str_list = list(str(self.square_result))
        ret_str_list.insert(self.data_list_len, '.')
        self.square_result_str = ''.join(ret_str_list)

    def reload_current_target_number(self, index, index_ret):
        minute_ret = self.current_target_number - self.get_reducer(index_ret)
        self.current_target_number = minute_ret * 100 + self.get_target_number(index)
        if not self.current_target_number and index == self.data_list_len:
            self.finished = True

    def get_index_ret(self):
        for i in range(9, -1, -1):
            if self.get_reducer(i) <= self.current_target_number:
                return i
        return 0

    def square(self):
        """计算开平方结果，主要理论依据是：(a.b)**2 == (a+0.b)**2 = a**2 + (0.b)**2 + 2*a*(0.b)"""
        index = 0
        index_ret = 0
        self.reload_current_target_number(index, index_ret)
        self.reload_result(index_ret)
        while not self.finished:
            index_ret = self.get_index_ret()

            index += 1
            self.reload_current_target_number(index, index_ret)
            self.reload_result(index_ret)

            print index_ret
            print self.square_result_str
            time.sleep(0.1)

        print index_ret
        print self.square_result_str


if __name__ == '__main__':
    number = int(input('number:'))
    num_node = NumberNode(number)
    num_node.square()
