CREATE TABLE `user` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '用户名',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COMMENT='用户基本信息表';

CREATE TABLE `user_deposit` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `user_id` int unsigned NOT NULL DEFAULT 0 COMMENT 'user_id',
  `money` smallint unsigned NOT NULL DEFAULT 0 COMMENT '余额（分）',
  `deposit_type` smallint unsigned NOT NULL DEFAULT 0 COMMENT '账户类型：0 普通储蓄，1 企业客户，2 个人vip，3 政府机构，4 黑卡用户，5 银行特别账户',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COMMENT='用户基本信息表';

CREATE TABLE `user_deposit_changes` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `user_id` int unsigned NOT NULL DEFAULT 0 COMMENT 'user_id',
  `partner_uid` int unsigned NOT NULL DEFAULT 0 COMMENT 'partner_uid，与 user_id 发生交易的对方 user_id',
  `deal_type` smallint unsigned NOT NULL DEFAULT 0 COMMENT '变动类型：0 收款，2 付款，为了简单，不实现存钱/取钱逻辑',
  `deal_money` smallint unsigned NOT NULL DEFAULT 0 COMMENT '余额变动（分）',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COMMENT='用户基本信息表';
