# -*- encoding: utf-8 -*-

"""
 ═══════════════════════════════════════════════════════════════════════

 ███████╗██╗     ██████╗  ██████╗  ██████╗  ██████╗
 ██╔════╝██║     ██╔══██╗██╔═══██╗██╔═══██╗██╔═══██╗
 █████╗  ██║     ██████╔╝██║   ██║██║   ██║██║   ██║
 ██╔══╝  ██║     ██╔══██╗██║   ██║██║   ██║██║▄▄ ██║
 ███████╗███████╗██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝
 ╚══════╝╚══════╝╚═════╝  ╚═════╝  ╚═════╝  ╚══▀▀═╝

 Copyright © 2018 elbooq. All rights reserved.

 ═══════════════════════════════════════════════════════════════════════
"""

import requests
import uuid
import time
import json


# We have created BooqServiceClient for easy of use, we highly recommending you to use it without modifying
# feel free to modify based on your need

class BooqServiceClient:
    merchantUserId = ''
    merchantBooqId = ''
    applicationId = ''
    masterKey = ''

    language = 'EN'
    mode = 'sandbox'  # or 'production'

    def __init__(self,language='EN',mode='sandbox'):
        self.language = language
        self.mode = mode


    # RFC 4211 COMPLIANT Universally Unique Identifiers (UUID)
    # Version 4
    def get_uuid(self):
        return str(uuid.uuid4())

    def get_timestamp(self):
        return int(time.time() * 1000)

    def get_authorization_keys(self):
        json = {'securityKeyHM': {'entry': [{
            'key': '2',
            'value': {'value': self.applicationId}
        }, {
            'key': '3',
            'value': {'value': self.masterKey}
        }
        ]}}
        return json

    def get_headers(self):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': self.language,
            'Cache-Control': 'no-cache'
        }
        return headers

    def get_base_url(self):
        host = 'http://uat.elbooq.net:7001'
        if (self.mode == 'production'):
            host = 'https://elbooq.bankboubyan.com'
        else:
            pass

        path = '/GPNRS/rs/merchantsIntegration/'
        return ("{}{}".format(host, path))

    def post(self, service, payload):
        url = self.get_base_url() + service + '/'
        return requests.post(url, json=payload, headers=self.get_headers())

    def initPayment(self, order_no, amount, user_secure_token, post_back_url, type, account_number=None):
        payload = {
            'createdByUserId': self.merchantUserId,
            'clientTimeStamp': self.get_timestamp(),
            'clientUUID': self.get_uuid(),
            'transfer': {
                'toAccount': {'owner': {'booqId': self.merchantBooqId}},
                'transAmount': amount,
                'referenceOne': order_no,
                'paymentOptions': type,
                'includeQRPayment': False
            },
            'authorization': self.get_authorization_keys()
        }

        if account_number:
            payload['transfer']['toAccount']['accountNumber'] = account_number

        payload['authorization']['userSecureToken'] = user_secure_token
        payload['authorization']['postBackUrl'] = post_back_url
        return json.loads(self.post("initPayment", payload).text)

    def checkPayment(self, order_no):
        payload = {
            'createdByUserId': self.merchantUserId,
            'clientTimeStamp': self.get_timestamp(),
            'clientUUID': self.get_uuid(),
            'transfer': {
                'createdByUserId': self.merchantUserId,
                'referenceOne': order_no
            },
            'authorization': self.get_authorization_keys()
        }

        return json.loads(self.post("checkPayment", payload).text)


