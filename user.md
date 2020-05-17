# 这里是用户体系数据表设计

# 登录用到的用户表
user 
   |__ id  
   |__ user_id  
   |__ user_group_id  # 用户组 id 
   |__ user_type  # 账户类型：1手机号/2微信/3qq/...
   |__ identifier   #  openid/e_mobile/...
   |__ passwd
   |__ avatar
   |__ st  # 是否可以登陆：1可以，0不可以
   |__ create_time  
   |__ update_time   
     
     
# 一个用户的多个账户，需要合并的用户基本数据，需要用到 user_group_id
# 如果不需要合并的数据，只需要使用 user_id 
user_attr
   |_ id
   |_ user_group_id  
   |_ e_mobile  # 绑定的手机号
   |_ email  
   |_ name
   |_ sex
   |_ birthday
   |_ nick_name
   |_ head_img
   |_ unionid
   |_ profession_id  # 行业方向表id
   |_ company
   |_ title
   |_ location_id  # 省市区表的id
   |_ create_time  
   |_ update_time  
  
  
sku_member  # 用户的 sku 学籍身份信息，代表了用户合并时，只需要维护一条记录，也就是需要合并的表。
   |_ id
   |_ user_group_id
   |_ sku_id  # 对应一个 sku_info 表的 id
   |_ join_time  
   |_ finish_time 
   |_ create_time  
   |_ update_time  
  
  
sku_member_pay  # 用户的 sku 购买流水表，代表了用户合并操作时，不需要合并的表。
   |_ id
   |_ user_id
   |_ sku_id
   |_ pay_id
   |_ create_time  
   |_ update_time  
   