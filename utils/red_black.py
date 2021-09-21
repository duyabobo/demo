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

    @property
    def is_leaf(self):
        return self.key is None and self.value is None and self.left is None and self.right is None

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

    def clear(self):
        self.color = COLOR_BLACK
        self.key = None
        self.value = None
        self.left = None
        self.right = None

    def set_leaf(self):
        left = RBNode()
        left.parent = self
        self.left = left

        right = RBNode()
        right.parent = self
        self.right = right


class RBTree(object):
    def __init__(self, root_node):
        """红黑树"""
        self.root = root_node

    @classmethod
    def build(cls):
        node = RBNode()
        node.set_leaf()
        return cls(node)

    def search(self, key):
        if self.root is None:
            self.root = RBTree.build().root
            return self.root
        if self.root.is_leaf:
            return self.root

        if self.root.key == key:
            return self.root
        elif self.root.key > key:
            return RBTree(self.root.left).search(key)
        else:  # self.root.key < key:
            return RBTree(self.root.right).search(key)

    def find_replace_node(self, current_node):
        """todo 找到某个节点的'后继'节点"""
        pass

    def rebalance(self):
        """todo 红黑树再平衡，需要旋转+变色保持平衡"""
        pass

    def replace_recursive(self, target_node):
        """递归找到一个非nil的叶子节点，递归替代被删除的节点"""
        current_node = target_node
        while not (current_node.left.is_leaf and current_node.right.is_leaf):
            replace_node = self.find_replace_node(current_node)
            current_node.update(key=replace_node.key, value=replace_node.value)
            current_node = replace_node
        current_node.clear()
        return current_node

    def insert(self, node):
        """关键路径是：找到插入点，插入一个红色节点，最后对插入节点的父节点再平衡"""
        target_node = self.search(node.key)
        if target_node.is_leaf:
            node.set_leaf()
            target_node.update(color=COLOR_RED, key=node.key, value=node.value, left=node.left, right=node.left)
            RBTree(target_node.parent).rebalance()
            return
        elif target_node.key == node.key:
            target_node.update(value=node.value)
            return
        else:
            raise

    def delete(self, key):
        """关键路径是：依次找'后继'节点替换需要当前节点（只更新key/value，不修改当前节点颜色），直到当前节点是最底层节点（左右子节点都是叶子节点），把当前节点修改成叶子节点，最后对再当前节点的父节点平衡"""
        target_node = self.search(key)
        if target_node.is_leaf:  # 没找着
            return
        elif target_node.key == key:
            replace_node = self.replace_recursive(target_node)
            RBTree(replace_node.parent).rebalance()
        else:
            raise
