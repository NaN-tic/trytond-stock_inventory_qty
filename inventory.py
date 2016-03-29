# This file is part stock_inventory_qty module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Inventory', 'InventoryLine']


class Inventory:
    __metaclass__ = PoolMeta
    __name__ = 'stock.inventory'

    @classmethod
    def __setup__(cls):
        super(Inventory, cls).__setup__()
        cls._buttons.update({
                'update_lines': {
                    'readonly': Eval('state') != 'draft',
                    },
                })

    @classmethod
    def copy(cls, inventories, default=None):
        'Copy inventories updating lines instead of completing new lines'
        with Transaction().set_context(copy_inventory=True):
            new_inventories = super(Inventory, cls).copy(inventories,
                    default=default)
        cls.update_lines(new_inventories)
        return new_inventories

    @classmethod
    def complete_lines(cls, inventories, fill=False):
        if Transaction().context.get('copy_inventory', False):
            return
        super(Inventory, cls).complete_lines(inventories, fill)

    @staticmethod
    def update_lines(inventories):
        '''
        Update the inventory lines
        '''
        pool = Pool()
        Line = pool.get('stock.inventory.line')
        Product = pool.get('product.product')

        for inventory in inventories:
            product_ids = []
            for line in inventory.lines:
                product_ids.append(line.product.id)

            if not product_ids:
                continue

            # Compute product quantities
            with Transaction().set_context(stock_date_end=inventory.date):
                pbl = Product.products_by_location([inventory.location.id],
                        product_ids)

            # Index some data
            product2uom = {}
            product2type = {}
            product2consumable = {}
            for product in Product.browse([line[1] for line in pbl]):
                product2uom[product.id] = product.default_uom.id
                product2type[product.id] = product.type
                product2consumable[product.id] = product.consumable

            product_qty = {}
            for (location, product), quantity in pbl.iteritems():
                product_qty[product] = (quantity, product2uom[product])

            # Update existing lines
            for line in inventory.lines:
                # Refresh line (inventories with lot of lines fails read lines)
                line = Line(line.id)
                if not (line.product.active and
                        line.product.type == 'goods'
                        and not line.product.consumable):
                    Line.delete([line])
                    continue
                if line.product.id in product_qty:
                    quantity, uom_id = product_qty.pop(line.product.id)
                else:
                    quantity = 0.0
                values = line.update_values4complete(quantity)
                if values:
                    Line.write([line], values)


class InventoryLine:
    __metaclass__ = PoolMeta
    __name__ = 'stock.inventory.line'

    @staticmethod
    def default_quantity():
        return 0.
