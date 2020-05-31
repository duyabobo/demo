#! /usr/bin/env python
# -*- coding: utf-8 -*-

# 网上解释

# -- 贫血模型：是指 model 层只有 get 和 set 方法，或者包含少量的 CRUD 方法，所有的业务逻辑都不包含在内而是放在 service 层。
# ---- 优点：层次分明
# ---- 缺点：面向过程，service 层过重

# -- 充血模型：层次结构和上面的差不多，不过大多业务逻辑和持久化放在 model层 里面，service 层只是简单封装部分业务逻辑以及控制事务、权限等。
# ---- 优点：面向对象，自洽程度很高
# ---- 缺点：model/service 层边界划分需要很高的业务认知和技术经验


# 个人理解

# 一个简单稳定，边界清晰的 model 底层设计，能够非常容易在团队内达成共识，也有助于 service 上层的扩展开发。
# 1，分层之间职责清晰，划分规则要尽可能简单准确，而不是一千个成员有一千个理解。
# 2，同层之间做好隔离，不互相调用，把涉及同层多个对象的操作逻辑提升到上层编排调度。
# 3，底层 model 类边界尽可能稳定，每个 model 类内部，`仅包括且包括全部`当前 model 对象操作和属性的定义。

# 贫血模型
# -- model 层边界定义：
# -- 1，-- 数据表映射关系，划分到 model 层。
# -- 2，-- dao 层也就是广义数据持久层（增删改查逻辑），可以划分为 model 逻辑，也可以单独拆分出去，这里划分到 model 层。
# -- 3，-- 与当前数据模型的一条数据记录相关的业务逻辑（与持久化无关的业务逻辑），可以直接作为 model 对象的属性实现，也划分到 model 层。
# -- service 层边界定义：
# -- 4，-- 与一个数据模型的多条数据记录相关的业务逻辑（与持久化逻辑有关的业务逻辑），划分到 service 中。
# -- 5，-- 与多个数据模型相关的业务逻辑（与持久化逻辑有关的业务逻辑），划分到 service 中。
# -- 6，-- 权限控制，事务控制逻辑，划分到 service 中。

# 充血模型
# -- model 层边界定义：
# -- 1，-- 数据表映射关系，划分到 model 层。
# -- 2，-- dao 层也就是广义数据持久层（增删改查逻辑），可以划分为 model 逻辑，也可以单独拆分出去，这里划分到 model 层。
# -- 3，-- 与当前数据模型的一条数据记录相关的业务逻辑（与持久化无关的业务逻辑），可以直接作为 model 对象的属性实现，也划分到 model 层。
# -- 4，-- 与当前数据模型的多条数据记录相关的业务逻辑（与持久化逻辑有关的业务逻辑），划分到 model 中。
# -- service 层边界定义：
# -- 5，-- 与多个数据模型相关的业务逻辑（与持久化逻辑有关的业务逻辑），划分到 service 中。
# -- 6，-- 权限控制，事务控制逻辑，划分到 service 中。


# 以上 model 边界划分，并不严格符合`领域驱动设计`（ddd）思想，或可以称之为是一种非常极端的 ddd，或是一种极其简单的 ddd。
# 1，每一个实体（ddd中的概念）对应一个数据表，而不是 ddd 推荐的可能需要`一对一`或者`一对多`或者`多对一`关系。
# 2，每个实体都是一个聚合（每个实体都是聚合根），而不是根据`领域驱动设计`思想，从实体中找到聚合根，再去聚合与聚合根紧密关联的多个实体。
# 3，由于每个实体划分一个聚合，那么就不存在领域层服务（实现`一个聚合内多个实体操作逻辑`的地方），直接是应用层服务（实现`多个聚合的操作逻辑`的地方）。
# 4，ddd 对水平拆分是友好的，但是对于一个几乎不可能再次水平拆分的微服务内部实现来说，明确又简单的垂直分层是明智的。

# model 层的多个实体之间的 join 操作，可能必须要打破同层之间不互相调用的隔离。
# 1，在 dao 层独立实现的时候，不会有这种困扰，因为涉及多个底层 model 对象的 join 操作，可以提到上层 dao 层处理。
# 2，在严格的 ddd 设计思想中，也不会有这种困扰，因为 ddd 推荐把业务耦合紧密的多个实体（或值对象）聚合，一个聚合内的多个实体的 join 操作可以放到聚合根中实现。
# 3，在`每个实体都是聚合根`设计思想下，可以根据 join 的主从关系，在`主实体`中实现 join 查询操作。
# 4，另外，join 操作一般不会太多，拆分也是一个解决方法，数据表冗余设计（反范式设计）也是一种解决方法。