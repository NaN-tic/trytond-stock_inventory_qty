# This file is part of the stock_inventory_qty module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class StockInventoryQtyTestCase(ModuleTestCase):
    'Test Stock Inventory Qty module'
    module = 'stock_inventory_qty'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        StockInventoryQtyTestCase))
    return suite