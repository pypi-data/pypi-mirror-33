Sale stock exception
--------------------

This addon adds two new sales exceptions to be used by the `sale_exception`
addon:

* The first one ensures that an order line can be delivered on the delivery
  date if it is in MTS. Validation is done by using the order line location via
  related shop and using the line delay.

* The second one will create a sales exception if the current SO will break a
  sales order already placed in the future.

The second test will only look for stock moves that pass by the line location,
so if your stock have children or if you have configured automated stock
actions they must pass by the location related to the SO line, else they will
be ignored.

If the module sale_owner_stock_sourcing is installed, each sale order line can
specify a stock owner. In that case, the owner will be used when computing the
virtual stock availability. For this to work correctly,
https://github.com/odoo/odoo/issues/5814 needs to be fixed (fixes are proposed
both for odoo and OCB).

**Warning:**

The second test is a workaround to compensate the lack of
stock reservation process in OpenERP. This can be a performance killer
and should not be be used if you have hundreds of simultaneous open SO.


