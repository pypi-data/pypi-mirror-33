# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Handler for purchase order batches
"""

from __future__ import unicode_literals, absolute_import

import logging

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.batch import BatchHandler
from rattail.time import make_utc
from rattail.vendors.invoices import require_invoice_parser


log = logging.getLogger(__name__)


class PurchaseBatchHandler(BatchHandler):
    """
    Handler for purchase order batches.
    """
    batch_model_class = model.PurchaseBatch

    # set this to True for handler to skip various "case" logic
    ignore_cases = False

    def should_populate(self, batch):
        # TODO: this probably should change soon, for now this works..
        return batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)

    def populate(self, batch, progress=None):
        assert batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)

        def append(item, i):
            row = model.PurchaseBatchRow()
            row.item = item
            row.product = item.product
            row.cases_ordered = item.cases_ordered
            row.units_ordered = item.units_ordered
            row.cases_received = item.cases_received
            row.units_received = item.units_received
            row.po_unit_cost = item.po_unit_cost
            row.po_total = item.po_total
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
                row.invoice_unit_cost = item.invoice_unit_cost
                row.invoice_total = item.invoice_total
            self.add_row(batch, row)

        self.progress_loop(append, batch.purchase.items, progress,
                           message="Adding initial rows to batch")

        # TODO: should(n't) this be handled elsewhere?
        session = orm.object_session(batch)
        session.flush()
        self.refresh_batch_status(batch)

    def populate_from_truck_dump_invoice(self, batch, progress=None):
        parser = require_invoice_parser(batch.invoice_parser_key)

        session = orm.object_session(batch)
        parser.session = session

        parser.vendor = api.get_vendor(session, parser.vendor_key)
        if parser.vendor is not batch.vendor:
            raise RuntimeError("Parser is for vendor '{}' but batch is for: {}".format(
                parser.vendor_key, batch.vendor))

        path = batch.filepath(self.config, batch.invoice_file)
        batch.invoice_date = parser.parse_invoice_date(path)

        def append(invoice_row, i):
            row = model.PurchaseBatchRow()
            row.upc = invoice_row.upc
            row.vendor_code = invoice_row.vendor_code
            row.brand_name = invoice_row.brand_name
            row.description = invoice_row.description
            row.size = invoice_row.size
            row.case_quantity = invoice_row.case_quantity
            row.cases_ordered = invoice_row.ordered_cases
            row.units_ordered = invoice_row.ordered_units
            row.cases_shipped = invoice_row.shipped_cases
            row.units_shipped = invoice_row.shipped_units
            row.invoice_unit_cost = invoice_row.unit_cost
            row.invoice_total = invoice_row.total_cost
            row.invoice_case_cost = invoice_row.case_cost
            self.add_row(batch, row)

        self.progress_loop(append, list(parser.parse_rows(path)), progress,
                           message="Adding initial rows to batch")

        self.make_truck_dump_claims_for_child_batch(batch, progress=progress)
        self.refresh_batch_status(batch.truck_dump_batch)

    def make_truck_dump_claims_for_child_batch(self, batch, progress=None):
        """
        Make all "claims" against a truck dump, for the given child batch.
        This assumes no claims exist for the child batch at time of calling,
        and that the truck dump batch is complete and not yet executed.
        """
        session = orm.object_session(batch)
        truck_dump_rows = batch.truck_dump_batch.active_rows()
        child_rows = batch.active_rows()

        # organize truck dump by product and UPC
        truck_dump_by_product = {}
        truck_dump_by_upc = {}
        for row in truck_dump_rows:
            if row.product:
                truck_dump_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                truck_dump_by_upc.setdefault(row.upc, []).append(row)

        # organize child batch by product and UPC
        child_by_product = {}
        child_by_upc = {}
        for row in child_rows:
            if row.product:
                child_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                child_by_upc.setdefault(row.upc, []).append(row)

        # first pass looks only for exact product and quantity match
        for uuid, child_product_rows in six.iteritems(child_by_product):
            if uuid not in truck_dump_by_product:
                continue

            # inspect truck dump to find exact match on child 'ordered' count
            index = 0
            truck_dump_product_rows = truck_dump_by_product[uuid]
            for truck_dump_row in list(truck_dump_product_rows):
                matched_child_rows = None

                # Note: A possibility we do not address here is one where the
                # truck dump quantity would match against a certain aggregation
                # of child rows but not *all* child rows.  E.g. if the child
                # contained 3 rows but only 2 of them should (combined) match
                # the truck dump row.  As of this writing this is a
                # hypothetical edge case but it will probably happen at some
                # point.  We can maybe assess the situation then.

                available = self.get_units_available(truck_dump_row)

                # first look at each child row individually (first match wins)
                for child_row in child_product_rows:
                    ordered = self.get_units_ordered(child_row)
                    if ordered == available:
                        matched_child_rows = [child_row]
                        break

                # maybe also look at the aggregate child counts
                if not matched_child_rows:
                    ordered = sum([self.get_units_ordered(row)
                                   for row in child_product_rows])
                    if ordered == available:
                        matched_child_rows = child_product_rows

                # did we find a match?
                claims = False
                if matched_child_rows:

                    # make some truck dump claim(s)
                    claims = self.make_truck_dump_claims(truck_dump_row, matched_child_rows)

                if claims:

                    # remove truck dump row from working set
                    truck_dump_product_rows.pop(index)
                    if not truck_dump_product_rows:
                        del truck_dump_by_product[uuid]

                    # filter working set of child batch rows, removing any
                    # which contributed to the match
                    remaining = []
                    for child_row in child_product_rows:
                        matched = False
                        for match_row in matched_child_rows:
                            if match_row is child_row:
                                matched = True
                                break
                        if not matched:
                            remaining.append(child_row)
                    child_product_rows = remaining

                # if no match, shift index so future list pops work
                else:
                    index += 1

        # TODO: second pass to look for inexact and UPC matches, yes?

    def make_truck_dump_claims(self, truck_dump_row, child_rows):

        avail_received = self.get_units_received(truck_dump_row) - self.get_units_claimed_received(truck_dump_row)
        avail_damaged = self.get_units_damaged(truck_dump_row) - self.get_units_claimed_damaged(truck_dump_row)
        avail_expired = self.get_units_expired(truck_dump_row) - self.get_units_claimed_expired(truck_dump_row)

        claims = []
        for child_row in child_rows:

            ordered = self.get_units_ordered(child_row)

            # TODO: must look into why this can happen...
            # assert ordered, "child row has no ordered count: {}".format(child_row)
            if not ordered:
                continue

            # TODO: should we ever use case quantity from truck dump instead?
            case_quantity = child_row.case_quantity

            claim = model.PurchaseBatchRowClaim()
            claim.claiming_row = child_row
            truck_dump_row.claims.append(claim)

            # if "received" can account for all we ordered, use only that
            if ordered <= avail_received:
                child_row.cases_received = claim.cases_received = child_row.cases_ordered
                child_row.units_received = claim.units_received = child_row.units_ordered
                self.refresh_row(child_row)

            # if "damaged" can account for all we ordered, use only that
            elif ordered <= avail_damaged:

                matched = False
                for credit in truck_dump_row.credits:
                    if credit.credit_type == 'damaged':
                        shorted = self.get_units_shorted(credit)
                        if shorted == ordered:
                            child_row.cases_damaged = claim.cases_damaged = credit.cases_shorted
                            child_row.units_damaged = claim.units_damaged = credit.units_shorted
                            self.clone_truck_dump_credit(credit, child_row)
                            self.refresh_row(child_row)
                            matched = True
                            break

                assert matched, "could not find matching 'damaged' credit to clone for {}".format(truck_dump_row)

            # if "expired" can account for all we ordered, use only that
            elif ordered <= avail_expired:

                matched = False
                for credit in truck_dump_row.credits:
                    if credit.credit_type == 'expired':
                        shorted = self.get_units_shorted(credit)
                        if shorted == ordered:
                            child_row.cases_expired = claim.cases_expired = credit.cases_shorted
                            child_row.units_expired = claim.units_expired = credit.units_shorted
                            self.clone_truck_dump_credit(credit, child_row)
                            self.refresh_row(child_row)
                            matched = True
                            break

                assert matched, "could not find matching 'expired' credit to clone for {}".format(truck_dump_row)

            else: # things are a bit trickier in this scenario

                # TODO: should we ever use case quantity from truck dump instead?

                if ordered and avail_received:
                    cases, units = self.calc_best_fit(avail_received, case_quantity)
                    total = self.get_units(cases, units, case_quantity)
                    assert total == avail_received, "total units doesn't match avail_received for {}".format(truck_dump_row)
                    child_row.cases_received = claim.cases_received = cases or None
                    child_row.units_received = claim.units_received = units or None
                    self.refresh_row(child_row)
                    avail_received -= total
                    ordered -= total

                if ordered and avail_damaged:
                    assert ordered >= avail_damaged
                    possible_credits = [credit for credit in truck_dump_row.credits
                                        if credit.credit_type == 'damaged']
                    possible_shorted = sum([self.get_units_shorted(credit)
                                            for credit in possible_credits])
                    if possible_shorted == avail_damaged:
                        cases = sum([credit.cases_shorted or 0
                                     for credit in possible_credits])
                        units = sum([credit.units_shorted or 0
                                     for credit in possible_credits])
                        child_row.cases_damaged = claim.cases_damaged = cases or None
                        child_row.units_damaged = claim.units_damaged = units or None
                        for credit in possible_credits:
                            self.clone_truck_dump_credit(credit, child_row)
                        self.refresh_row(child_row)
                        ordered -= avail_damaged
                        avail_damaged = 0
                    else:
                        raise NotImplementedError

                # TODO: need to add support for credits to this one
                if ordered and avail_expired:
                    cases, units = self.calc_best_fit(avail_expired, case_quantity)
                    total = self.get_units(cases, units, case_quantity)
                    assert total == avail_expired, "total units doesn't match avail_expired for {}".format(truck_dump_row)
                    child_row.cases_expired = claim.cases_expired = cases or None
                    child_row.cases_expired = claim.units_expired = units or None
                    self.refresh_row(child_row)
                    avail_expired -= total
                    ordered -= total

                if ordered:
                    raise NotImplementedError("TODO: can't yet handle match with mixture of received/damaged/expired (?)")

            self.refresh_row(truck_dump_row)
            claims.append(claim)

        return claims

    def clone_truck_dump_credit(self, truck_dump_credit, child_row):
        """
        Clone a credit record from a truck dump, onto the given child row.
        """
        child_batch = child_row.batch
        child_credit = model.PurchaseBatchCredit()
        self.copy_credit_attributes(truck_dump_credit, child_credit)
        child_credit.date_ordered = child_batch.date_ordered
        child_credit.date_shipped = child_batch.date_shipped
        child_credit.date_received = child_batch.date_received
        child_credit.invoice_date = child_batch.invoice_date
        child_credit.invoice_number = child_batch.invoice_number
        child_credit.invoice_line_number = child_row.invoice_line_number
        child_credit.invoice_case_cost = child_row.invoice_case_cost
        child_credit.invoice_unit_cost = child_row.invoice_unit_cost
        child_credit.invoice_total = child_row.invoice_total
        child_row.credits.append(child_credit)
        return child_credit

    # TODO: surely this should live elsewhere
    def calc_best_fit(self, units, case_quantity):
        case_quantity = case_quantity or 1
        if case_quantity == 1:
            return 0, units
        cases = units // case_quantity
        if cases:
            return cases, units % cases
        return 0, units

    def refresh(self, batch, progress=None):
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            batch.po_total = 0
        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            batch.invoice_total = 0
        return super(PurchaseBatchHandler, self).refresh(batch, progress=progress)

    def refresh_batch_status(self, batch):
        rows = batch.active_rows()
        if any([not row.product_uuid for row in rows]):
            batch.status_code = batch.STATUS_UNKNOWN_PRODUCT
        elif batch.truck_dump:
            if any([row.status_code == row.STATUS_TRUCKDUMP_UNCLAIMED for row in rows]):
                batch.status_code = batch.STATUS_TRUCKDUMP_UNCLAIMED
            else:
                batch.status_code = batch.STATUS_TRUCKDUMP_CLAIMED
        else:
            batch.status_code = batch.STATUS_OK

    def refresh_row(self, row, initial=False):
        """
        Refreshing a row will A) assume that ``row.product`` is already set to
        a valid product, and B) update various other fields on the row
        (description, size, etc.)  to reflect the current product data.  It
        also will adjust the batch PO total per the row PO total.
        """
        batch = row.batch
        product = row.product
        if not product:
            if row.upc:
                session = orm.object_session(row)
                product = api.get_product_by_upc(session, row.upc)
            if not product:
                # TODO: should we do more stuff here..?
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return
            row.product = product

        cost = row.product.cost_for_vendor(batch.vendor) or row.product.cost
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        if product.department:
            row.department_number = product.department.number
            row.department_name = product.department.name
        else:
            row.department_number = None
            row.department_name = None
        row.vendor_code = cost.code if cost else None
        new_case_quantity = cost.case_size if cost else None
        if new_case_quantity:
            row.case_quantity = new_case_quantity

        self.refresh_totals(row, cost, initial)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.status_code = row.STATUS_OK

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if (row.cases_received is None and row.units_received is None and
                row.cases_damaged is None and row.units_damaged is None and
                row.cases_expired is None and row.units_expired is None and
                row.cases_mispick is None and row.units_mispick is None):
                row.status_code = row.STATUS_INCOMPLETE
            else:
                if batch.truck_dump:
                    confirmed = self.get_units_confirmed(row)
                    claimed = self.get_units_claimed(row)
                    if claimed == confirmed:
                        row.status_code = row.STATUS_TRUCKDUMP_CLAIMED
                    elif claimed < confirmed:
                        row.status_code = row.STATUS_TRUCKDUMP_UNCLAIMED
                    elif claimed > confirmed:
                        row.status_code = row.STATUS_TRUCKDUMP_OVERCLAIMED
                    else:
                        raise NotImplementedError
                else: # not truck_dump
                    if self.get_units_ordered(row) != self.get_units_accounted_for(row):
                        row.status_code = row.STATUS_ORDERED_RECEIVED_DIFFER
                    else:
                        row.status_code = row.STATUS_OK

        else:
            raise NotImplementedError("can't refresh row for batch of mode: {}".format(
                self.enum.PURHASE_BATCH_MODE.get(batch.mode, "unknown ({})".format(batch.mode))))

    def remove_row(self, row):
        """
        When removing a row from purchase batch, (maybe) must also update some
        totals for the batch.
        """
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if row.cases_ordered or row.units_ordered:
                raise NotImplementedError
            if row.invoice_total:
                batch.invoice_total -= row.invoice_total

        super(PurchaseBatchHandler, self).remove_row(row)

    def refresh_totals(self, row, cost, initial):
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.po_unit_cost = self.get_unit_cost(row.product, batch.vendor)
            if row.po_unit_cost:
                row.po_total = row.po_unit_cost * self.get_units_ordered(row)
                batch.po_total = (batch.po_total or 0) + row.po_total
            else:
                row.po_total = None

        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            row.invoice_unit_cost = (cost.unit_cost if cost else None) or row.po_unit_cost
            if row.invoice_unit_cost:
                row.invoice_total = row.invoice_unit_cost * self.get_units_accounted_for(row)
                batch.invoice_total = (batch.invoice_total or 0) + row.invoice_total
            else:
                row.invoice_total = None

    def get_unit_cost(self, product, vendor):
        """
        Must return the PO unit cost for the given product, from the given vendor.
        """
        cost = product.cost_for_vendor(vendor) or product.cost
        if cost:
            return cost.unit_cost

    def get_units(self, cases, units, case_quantity):
        case_quantity = case_quantity or 1
        return (units or 0) + case_quantity * (cases or 0)

    def get_units_ordered(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_ordered, row.units_ordered, case_quantity)

    # TODO: we now have shipped quantities...should return sum of those instead?
    def get_units_shipped(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        units_damaged = (row.units_damaged or 0) + case_quantity * (row.cases_damaged or 0)
        units_expired = (row.units_expired or 0) + case_quantity * (row.cases_expired or 0)
        return self.get_units_received(row) + units_damaged + units_expired

    def get_units_received(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_received, row.units_received, case_quantity)

    def get_units_damaged(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_damaged, row.units_damaged, case_quantity)

    def get_units_expired(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_expired, row.units_expired, case_quantity)

    def get_units_confirmed(self, row, case_quantity=None):
        received = self.get_units_received(row, case_quantity=case_quantity)
        damaged = self.get_units_damaged(row, case_quantity=case_quantity)
        expired = self.get_units_expired(row, case_quantity=case_quantity)
        return received + damaged + expired

    def get_units_mispick(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_mispick, row.units_mispick, case_quantity)

    def get_units_accounted_for(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        mispick = self.get_units_mispick(row, case_quantity=case_quantity)
        return confirmed + mispick

    def get_units_shorted(self, obj, case_quantity=None):
        case_quantity = case_quantity or obj.case_quantity or 1
        if hasattr(obj, 'cases_shorted'):
            # obj is really a credit
            return self.get_units(obj.cases_shorted, obj.units_shorted, case_quantity)
        else:
            # obj is a row, so sum the credits
            return sum([self.get_units(credit.cases_shorted, credit.units_shorted, case_quantity)
                        for credit in obj.credits])

    def get_units_claimed(self, row, case_quantity=None):
        return sum([self.get_units_confirmed(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_received(self, row, case_quantity=None):
        return sum([self.get_units_received(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_damaged(self, row, case_quantity=None):
        return sum([self.get_units_damaged(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_expired(self, row, case_quantity=None):
        return sum([self.get_units_expired(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_available(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        claimed = self.get_units_claimed(row, case_quantity=case_quantity)
        return confirmed - claimed

    def update_order_counts(self, purchase, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                inventory.on_order = (inventory.on_order or 0) + (item.units_ordered or 0) + (
                    (item.cases_ordered or 0) * (item.case_quantity or 1))

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def update_receiving_inventory(self, purchase, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                count = (item.units_received or 0) + (item.cases_received or 0) * (item.case_quantity or 1)
                if count:
                    if (inventory.on_order or 0) < count:
                        raise RuntimeError("Received {} units for {} but it only had {} on order".format(
                            count, item.product, inventory.on_order or 0))
                    inventory.on_order -= count
                    inventory.on_hand = (inventory.on_hand or 0) + count

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def why_not_execute(self, batch):
        """
        This method should return a string indicating the reason why the given
        batch should not be considered executable.  By default it returns
        ``None`` which means the batch *is* to be considered executable.

        Note that it is assumed the batch has not already been executed, since
        execution is globally prevented for such batches.
        """
        # not all receiving batches are executable
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            if batch.truck_dump_batch:
                return ("Can't directly execute batch which is child of a truck dump "
                        "(must execute truck dump instead)")

    def execute(self, batch, user, progress=None):
        """
        Default behavior for executing a purchase batch will create a new
        purchase, by invoking :meth:`make_purchase()`.
        """
        session = orm.object_session(batch)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            purchase = self.make_purchase(batch, user, progress=progress)
            self.update_order_counts(purchase, progress=progress)
            return purchase

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if self.allow_truck_dump and batch.truck_dump:
                self.execute_truck_dump(batch, user, progress=progress)
                return True
            else:
                with session.no_autoflush:
                    return self.receive_purchase(batch, progress=progress)

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            # TODO: finish this...
            # with session.no_autoflush:
            #     return self.cost_purchase(batch, progress=progress)
            purchase = batch.purchase
            purchase.invoice_date = batch.invoice_date
            purchase.status = self.enum.PURCHASE_STATUS_COSTED
            return purchase

        assert False

    def execute_truck_dump(self, batch, user, progress=None):
        now = make_utc()
        for child in batch.truck_dump_children:
            if not self.execute(child, user, progress=progress):
                raise RuntimeError("Failed to execute child batch: {}".format(child))
            child.executed = now
            child.executed_by = user

    def make_credits(self, batch, progress=None):
        session = orm.object_session(batch)
        mapper = orm.class_mapper(model.PurchaseBatchCredit)

        def copy(row, i):
            for batch_credit in row.credits:
                credit = model.PurchaseCredit()
                for prop in mapper.iterate_properties:
                    if isinstance(prop, orm.ColumnProperty) and hasattr(credit, prop.key):
                        setattr(credit, prop.key, getattr(batch_credit, prop.key))
                credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                session.add(credit)

        return self.progress_loop(copy, batch.active_rows(), progress,
                                  message="Creating purchase credits")

    def make_purchase(self, batch, user, progress=None):
        """
        Effectively clones the given batch, creating a new Purchase in the
        Rattail system.
        """
        session = orm.object_session(batch)
        purchase = model.Purchase()

        # TODO: should be smarter and only copy certain fields here
        skip_fields = [
            'date_received',
        ]
        for prop in orm.object_mapper(batch).iterate_properties:
            if prop.key in skip_fields:
                continue
            if hasattr(purchase, prop.key):
                setattr(purchase, prop.key, getattr(batch, prop.key))

        def clone(row, i):
            item = model.PurchaseItem()
            # TODO: should be smarter and only copy certain fields here
            for prop in orm.object_mapper(row).iterate_properties:
                if hasattr(item, prop.key):
                    setattr(item, prop.key, getattr(row, prop.key))
            purchase.items.append(item)

        with session.no_autoflush:
            self.progress_loop(clone, batch.active_rows(), progress,
                               message="Creating purchase items")

        purchase.created = make_utc()
        purchase.created_by = user
        purchase.status = self.enum.PURCHASE_STATUS_ORDERED
        session.add(purchase)
        batch.purchase = purchase
        return purchase

    def receive_purchase(self, batch, progress=None):
        """
        Update the purchase for the given batch, to indicate received status.
        """
        session = orm.object_session(batch)
        purchase = batch.purchase
        if not purchase:
            batch.purchase = purchase = model.Purchase()

            # TODO: should be smarter and only copy certain fields here
            skip_fields = [
                'date_received',
            ]
            for prop in orm.object_mapper(batch).iterate_properties:
                if prop.key in skip_fields:
                    continue
                if hasattr(purchase, prop.key):
                    setattr(purchase, prop.key, getattr(batch, prop.key))

        purchase.invoice_number = batch.invoice_number
        purchase.invoice_date = batch.invoice_date
        purchase.invoice_total = batch.invoice_total
        purchase.date_received = batch.date_received

        # determine which fields we'll copy when creating new purchase item
        copy_fields = []
        for prop in orm.class_mapper(model.PurchaseItem).iterate_properties:
            if hasattr(model.PurchaseBatchRow, prop.key):
                copy_fields.append(prop.key)

        def update(row, i):
            item = row.item
            if not item:
                row.item = item = model.PurchaseItem()
                for field in copy_fields:
                    setattr(item, field, getattr(row, field))
                purchase.items.append(item)

            item.cases_received = row.cases_received
            item.units_received = row.units_received
            item.cases_damaged = row.cases_damaged
            item.units_damaged = row.units_damaged
            item.cases_expired = row.cases_expired
            item.units_expired = row.units_expired
            item.invoice_line_number = row.invoice_line_number
            item.invoice_case_cost = row.invoice_case_cost
            item.invoice_unit_cost = row.invoice_unit_cost
            item.invoice_total = row.invoice_total

        with session.no_autoflush:
            self.progress_loop(update, batch.active_rows(), progress,
                               message="Updating purchase line items")

        purchase.status = self.enum.PURCHASE_STATUS_RECEIVED
        return purchase

    def clone_row(self, oldrow):
        newrow = super(PurchaseBatchHandler, self).clone_row(oldrow)

        for oldcredit in oldrow.credits:
            newcredit = model.PurchaseBatchCredit()
            self.copy_credit_attributes(oldcredit, newcredit)
            newrow.credits.append(newcredit)

        return newrow

    def copy_credit_attributes(self, source_credit, target_credit):
        mapper = orm.class_mapper(model.PurchaseBatchCredit)
        for prop in mapper.iterate_properties:
            if prop.key not in ('uuid', 'row_uuid'):
                if isinstance(prop, orm.ColumnProperty):
                    setattr(target_credit, prop.key, getattr(source_credit, prop.key))
