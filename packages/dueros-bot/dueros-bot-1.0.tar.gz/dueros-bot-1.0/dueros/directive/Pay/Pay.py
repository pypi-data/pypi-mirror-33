#!/usr/bin/env python3
# -*- encoding=utf-8 -*-

# description:
# author:jack
# create_time: 2018/7/2

"""
    desc:pass
"""

from dueros.directive.BaseDirective import BaseDirective

class Pay(BaseDirective):

    def __init__(self, amount, sellerOrderId, productName, description):
        super(Pay, self).__init__("Connections.SendRequest")
        self.data['name'] = 'Charge'
        self.data.token = self.genToken()
        self.data['amount'] = amount
        self.data['sellerOrderId'] = sellerOrderId
        self.data['productName'] = productName
        self.data['description'] = description
    pass


if __name__ == '__main__':
    pass