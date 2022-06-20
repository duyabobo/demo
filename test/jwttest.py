#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

import jwt
import requests as requests
import base64

PRIVATE_KEY_TOKEN = '''-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg0bHZOfEPTc5OIcNv
yHnMgDuTbf/s2WaKCeTks9HD0uSgCgYIKoZIzj0DAQehRANCAARI0jwm2xpLlx0p
29SgSkTrIDGb9wVRpb6GROv/qslRydOodu9snJnz4lDKL3C8lYv4HlATz6jkO79W
7NrFnnPW
-----END PRIVATE KEY-----
'''  # 认证服务独有


def get_token():
    return jwt.encode(
        payload={
          "iss": "7190e770-fe6b-4974-8000-ad39537f4b90",
          "iat": time.time() - 10,
          "exp": time.time() + 3500,
          "aud": "appstoreconnect-v1",
          "bid": "cn.hundun.hundunyanxishe"
        },
        key=PRIVATE_KEY_TOKEN,
        headers={
            "alg": "ES256",
            "kid": "UTK3GWQN7B",
            "typ": "JWT"
        },
        algorithm="ES256"
    )


def get_signedTransactions(order_id):
    url = 'https://api.storekit.itunes.apple.com/inApps/v1/lookup/%s' % order_id
    access_token = get_token()  # 获取jwt令牌
    resp = requests.get(url, headers={"Authorization": "Bearer %s" % access_token}, timeout=3)
    if resp.status_code != 200:
        print '请求失败 resp.status_code=%d' % resp.status_code
        return []
    resp_data = resp.json()
    if resp_data['status'] != 0:
        print '请求错误 resp_data.status=%d' % resp_data['status']
        return []
    return resp_data['signedTransactions']


def parse_transaction_ids(signedTransactions):
    transaction_ids = []
    for signedTransaction in signedTransactions:
        split_strs = signedTransaction.split('.')
        if len(split_strs) != 3:
            print '请求的 signedTransactions不对'
            continue
        pay_load_str = base64.b64decode("%s%s" % (split_strs[1].encode(), "=="))
        pay_load = json.loads(pay_load_str)
        transaction_ids.append(pay_load.get('transactionId', ''))
    return transaction_ids


if __name__ == '__main__':
    order_id = "MQ954NH6KW"
    signedTransactions = get_signedTransactions(order_id)  # 根据orderid查询signedTransactions
    transaction_ids = parse_transaction_ids(signedTransactions)  # 解析出transaction_ids
    print transaction_ids
