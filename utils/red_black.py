#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 红黑树实现，功能包括：查找，插入节点，删除节点。
# 巨人的肩膀：https://www.jianshu.com/p/e136ec79235c

COLOR_BLACK = 0
COLOR_RED = 1


class RBNode(object):
    def __init__(self, color=COLOR_BLACK, key=None, value=None, parent=None, left=None, right=None):
        """红黑节点"""
        self.color = color
        self.key = key
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right


class RBTree(object):
    def __init__(self, root_node=None):
        self.root = root_node

    def search(self, key):
        if self.root is None:  # 空红黑树
            return None
        if self.root.key is None:  # 叶子节点
            return None
        if self.root.key == key:
            return self.root.value
        if self.root.key > key:
            return RBTree(self.root.left).search(key)
        if self.root.key < key:
            return RBTree(self.root.right).search(key)

    def insert(self, node):
        pass

    def delete(self, key):
        pass
