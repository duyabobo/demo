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

    def update(self, color=None, key=None, value=None, parent=None, left=None, right=None):
        if color is not None:
            self.color = color
        if key is not None:
            self.key = key
        if value is not None:
            self.value = value
        if parent is not None:
            self.parent = parent
        if left is not None:
            self.left = left
        if right is not None:
            self.right = right

    def set_leaf(self):
        left = RBNode()
        left.parent = self
        self.left = left

        right = RBNode()
        right.parent = self
        self.right = right


class RBTree(object):
    def __init__(self, root_node):
        self.root = root_node

    @classmethod
    def build(cls):
        node = RBNode()
        node.set_leaf()
        return cls(node)

    def search(self, key):
        if self.root is None:  # 空红黑树
            self.root = RBTree.build().root
            return self.root
        if self.root.key is None:  # 叶子节点
            return self.root
        if self.root.key == key:
            return self.root
        if self.root.key > key:
            return RBTree(self.root.left).search(key)
        if self.root.key < key:
            return RBTree(self.root.right).search(key)

    def revolve(self):
        """todo 最小子树，需要旋转保持平衡"""
        pass

    def insert(self, node):
        target_node = self.search(node.key)
        if target_node.key == node.key:
            target_node.update(value=node.value)
        else:  # 叶子节点
            node.set_leaf()
            target_node.update(color=COLOR_RED, key=node.key, value=node.value, left=node.left, right=node.left)
            RBTree(target_node.parent).revolve()

    def delete(self, key):
        pass
