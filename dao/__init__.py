#! /usr/bin/env python
# -*- coding: utf-8 -*- 
# 这里只做数据持久化操作（广义持久化，包括增删改，也包括查询），不要有任何业务逻辑在里面：
# 1，只有原子操作：增删改查，从接口命名上，就是 get_xxx/ update_xxx/ delete_xxx/ add _xxx，举个例子命名不是 change_money ，而是 update_user_deposit，因为前者是业务理解（金额变动），后者就是中规中矩的持久化操作（修改user_deposit的一条记录）。
# 2，返回值就是 orm 接口返回值，比如 get_xxx 就是可能返回一个 query_object，而不能去根据业务需要解析出一个 json 返回。
# 3，不同 dao 文件之间不能出现互相调用，如果有join操作，比如 table_a join table_b，那么新建一个 dao 文件，叫做 table_a_b，并把 table_a 和 table_b 的持久化操作放到其中。
