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
Views for 'receiving' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import re

import six
import sqlalchemy as sa

from rattail import pod
from rattail.db import model, api
from rattail.gpc import GPC
from rattail.time import localtime
from rattail.util import pretty_quantity, prettify, OrderedDict
from rattail.vendors.invoices import iter_invoice_parsers, require_invoice_parser

import colander
from deform import widget as dfwidget
from pyramid import httpexceptions
from webhelpers2.html import tags, HTML

from tailbone import forms, grids
from tailbone.views.purchasing import PurchasingBatchView


class MobileItemStatusFilter(grids.filters.MobileFilter):

    value_choices = ['incomplete', 'unexpected', 'damaged', 'expired', 'all']

    def filter_equal(self, query, value):

        # NOTE: this is only relevant for truck dump
        if value == 'received':
            return query.filter(sa.or_(
                model.PurchaseBatchRow.cases_received != 0,
                model.PurchaseBatchRow.units_received != 0))

        # TODO: is this accurate (enough) ?
        if value == 'incomplete':
            return query.filter(sa.or_(model.PurchaseBatchRow.cases_ordered != 0, model.PurchaseBatchRow.units_ordered != 0))\
                        .filter(model.PurchaseBatchRow.status_code != model.PurchaseBatchRow.STATUS_OK)

        if value == 'unexpected':
            return query.filter(sa.and_(
                sa.or_(
                    model.PurchaseBatchRow.cases_ordered == None,
                    model.PurchaseBatchRow.cases_ordered == 0),
                sa.or_(
                    model.PurchaseBatchRow.units_ordered == None,
                    model.PurchaseBatchRow.units_ordered == 0)))

        if value == 'damaged':
            return query.filter(sa.or_(
                model.PurchaseBatchRow.cases_damaged != 0,
                model.PurchaseBatchRow.units_damaged != 0))

        if value == 'expired':
            return query.filter(sa.or_(
                model.PurchaseBatchRow.cases_expired != 0,
                model.PurchaseBatchRow.units_expired != 0))

        return query

    def iter_choices(self):
        for value in self.value_choices:
            yield value, prettify(value)


class ReceivingBatchView(PurchasingBatchView):
    """
    Master view for receiving batches
    """
    route_prefix = 'receiving'
    url_prefix = '/receiving'
    model_title = "Receiving Batch"
    model_title_plural = "Receiving Batches"
    index_title = "Receiving"
    downloadable = True
    rows_editable = True
    mobile_creatable = True
    mobile_rows_filterable = True
    mobile_rows_creatable = True

    allow_from_po = False
    allow_from_scratch = True
    allow_truck_dump = False

    labels = {
        'truck_dump_batch': "Truck Dump Parent",
        'invoice_parser_key': "Invoice Parser",
    }

    grid_columns = [
        'id',
        'vendor',
        'truck_dump',
        'department',
        'buyer',
        'date_ordered',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'batch_type',
        'description',
        'store',
        'vendor',
        'truck_dump',
        'truck_dump_children',
        'truck_dump_batch',
        'invoice_file',
        'invoice_parser_key',
        'department',
        'purchase',
        'vendor_email',
        'vendor_fax',
        'vendor_contact',
        'vendor_phone',
        'date_ordered',
        'date_received',
        'po_number',
        'po_total',
        'invoice_date',
        'invoice_number',
        'invoice_total',
        'notes',
        'created',
        'created_by',
        'status_code',
        'rowcount',
        'complete',
        'executed',
        'executed_by',
    ]

    mobile_form_fields = [
        'vendor',
        'truck_dump',
        'department',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        # 'item_id',
        'brand_name',
        'description',
        'size',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        # 'po_total',
        'invoice_total',
        'credits',
        'status_code',
    ]

    row_form_fields = [
        'upc',
        'item_id',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
        'cases_mispick',
        'units_mispick',
        'po_line_number',
        'po_unit_cost',
        'po_total',
        'invoice_line_number',
        'invoice_unit_cost',
        'invoice_total',
        'status_code',
        'credits',
    ]

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_RECEIVING

    def row_editable(self, row):
        batch = row.batch
        if batch.truck_dump_batch:
            return False
        return True

    def row_deletable(self, row):
        batch = row.batch
        if batch.truck_dump:
            return True
        return False

    def configure_form(self, f):
        super(ReceivingBatchView, self).configure_form(f)
        batch = f.model_instance

        # batch_type
        if self.creating:
            f.set_enum('batch_type', OrderedDict([
                ('from_scratch', "New from Scratch"),
            ]))
        else:
            f.remove_field('batch_type')

        # truck_dump*
        if self.allow_truck_dump:

            # truck_dump
            if self.creating:
                f.remove_field('truck_dump')
            elif batch.truck_dump_batch:
                f.remove_field('truck_dump')
            else:
                f.set_readonly('truck_dump')

            # truck_dump_children
            if self.viewing:
                if batch.truck_dump:
                    f.set_renderer('truck_dump_children', self.render_truck_dump_children)
                else:
                    f.remove_field('truck_dump_children')
            else:
                f.remove_field('truck_dump_children')

            # truck_dump_batch
            if self.creating:
                f.replace('truck_dump_batch', 'truck_dump_batch_uuid')
                batches = self.Session.query(model.PurchaseBatch)\
                                      .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)\
                                      .filter(model.PurchaseBatch.truck_dump == True)\
                                      .filter(model.PurchaseBatch.complete == True)\
                                      .filter(model.PurchaseBatch.executed == None)\
                                      .order_by(model.PurchaseBatch.id)
                batch_values = [(b.uuid, "({}) {}, {}".format(b.id_str, b.date_received, b.vendor))
                                for b in batches]
                batch_values.insert(0, ('', "(please choose)"))
                f.set_widget('truck_dump_batch_uuid', forms.widgets.JQuerySelectWidget(values=batch_values))
                f.set_label('truck_dump_batch_uuid', "Truck Dump Parent")
            elif batch.truck_dump:
                f.remove_field('truck_dump_batch')
            elif batch.truck_dump_batch:
                f.set_readonly('truck_dump_batch')
                f.set_renderer('truck_dump_batch', self.render_truck_dump_batch)
            else:
                f.remove_field('truck_dump_batch')

            # truck_dump_vendor
            if self.creating:
                f.set_label('truck_dump_vendor', "Vendor")
                f.set_readonly('truck_dump_vendor')
                f.set_renderer('truck_dump_vendor', self.render_truck_dump_vendor)

        else:
            f.remove_fields('truck_dump',
                            'truck_dump_children',
                            'truck_dump_batch')

        # invoice_file
        if self.creating:
            f.set_type('invoice_file', 'file')
        else:
            f.set_readonly('invoice_file')
            f.set_renderer('invoice_file', self.render_downloadable_file)

        # invoice_parser_key
        if self.creating:
            parsers = sorted(iter_invoice_parsers(), key=lambda p: p.display)
            parser_values = [(p.key, p.display) for p in parsers]
            parser_values.insert(0, ('', "(please choose)"))
            f.set_widget('invoice_parser_key', forms.widgets.JQuerySelectWidget(values=parser_values))
        else:
            f.remove_field('invoice_parser_key')

        # store
        if self.creating:
            store = self.rattail_config.get_store(self.Session())
            f.set_widget('store_uuid', forms.widgets.ReadonlyWidget())
            f.set_default('store_uuid', store.uuid)
            f.set_hidden('store_uuid')

        # purchase
        if self.creating:
            f.remove_field('purchase')

        # department
        if self.creating:
            f.remove_field('department_uuid')

    def template_kwargs_create(self, **kwargs):
        kwargs = super(ReceivingBatchView, self).template_kwargs_create(**kwargs)
        if self.allow_truck_dump:
            vmap = {}
            batches = self.Session.query(model.PurchaseBatch)\
                                  .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)\
                                  .filter(model.PurchaseBatch.truck_dump == True)\
                                  .filter(model.PurchaseBatch.complete == True)
            for batch in batches:
                vmap[batch.uuid] = batch.vendor_uuid
            kwargs['batch_vendor_map'] = vmap
        return kwargs

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(ReceivingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        if not mobile:
            batch_type = self.request.POST['batch_type']
            if batch_type == 'from_scratch':
                kwargs.pop('truck_dump_batch', None)
                kwargs.pop('truck_dump_batch_uuid', None)
            elif batch_type.startswith('truck_dump_child'):
                truck_dump = self.get_instance()
                kwargs['store'] = truck_dump.store
                kwargs['vendor'] = truck_dump.vendor
                kwargs['truck_dump_batch'] = truck_dump
            else:
                raise NotImplementedError
        return kwargs

    def delete_instance(self, batch):
        """
        Delete all data (files etc.) for the batch.
        """
        truck_dump = batch.truck_dump_batch
        if batch.truck_dump:
            for child in batch.truck_dump_children:
                self.delete_instance(child)
        super(ReceivingBatchView, self).delete_instance(batch)
        if truck_dump:
            self.handler.refresh(truck_dump)

    def render_truck_dump_batch(self, batch, field):
        truck_dump = batch.truck_dump_batch
        if not truck_dump:
            return ""
        text = six.text_type(truck_dump)
        url = self.request.route_url('receiving.view', uuid=truck_dump.uuid)
        return tags.link_to(text, url)

    def render_truck_dump_vendor(self, batch, field):
        truck_dump = self.get_instance()
        vendor = truck_dump.vendor
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_truck_dump_children(self, batch, field):
        contents = []
        children = batch.truck_dump_children
        if children:
            items = []
            for child in children:
                text = six.text_type(child)
                url = self.request.route_url('receiving.view', uuid=child.uuid)
                items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
            contents.append(HTML.tag('ul', c=items))
        if batch.complete and not batch.executed:
            buttons = self.make_truck_dump_child_buttons(batch)
            if buttons:
                buttons = HTML.literal(' ').join(buttons)
                contents.append(HTML.tag('div', class_='buttons', c=[buttons]))
        if not contents:
            return ""
        return HTML.tag('div', c=contents)

    def make_truck_dump_child_buttons(self, batch):
        return [
            tags.link_to("Add from Invoice File", self.get_action_url('add_child_from_invoice', batch), class_='button autodisable'),
        ]

    def add_child_from_invoice(self):
        """
        View for adding a child batch to a truck dump, from invoice file.
        """
        batch = self.get_instance()
        if not batch.truck_dump:
            self.request.session.flash("Batch is not a truck dump: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        if batch.executed:
            self.request.session.flash("Batch has already been executed: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        if not batch.complete:
            self.request.session.flash("Batch is not marked as complete: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        self.creating = True
        form = self.make_child_from_invoice_form(self.get_model_class())
        return self.create(form=form)

    def make_child_from_invoice_form(self, instance, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        kwargs['configure'] = self.configure_child_from_invoice_form
        return self.make_form(instance=instance, **kwargs)

    def configure_child_from_invoice_form(self, f):
        assert self.creating
        truck_dump = self.get_instance()

        self.configure_form(f)

        f.set_fields([
            'batch_type',
            'truck_dump_parent',
            'truck_dump_vendor',
            'invoice_file',
            'invoice_parser_key',
            'description',
            'notes',
        ])

        # batch_type
        f.set_widget('batch_type', forms.widgets.ReadonlyWidget())
        f.set_default('batch_type', 'truck_dump_child_from_invoice')

        # truck_dump_batch_uuid
        f.set_readonly('truck_dump_parent')
        f.set_renderer('truck_dump_parent', self.render_truck_dump_parent)

    def render_truck_dump_parent(self, batch, field):
        truck_dump = self.get_instance()
        text = six.text_type(truck_dump)
        url = self.request.route_url('receiving.view', uuid=truck_dump.uuid)
        return tags.link_to(text, url)

    def render_mobile_listitem(self, batch, i):
        title = "({}) {} for ${:0,.2f} - {}, {}".format(
            batch.id_str,
            batch.vendor,
            batch.po_total or 0,
            batch.department,
            batch.created_by)
        return title

    def make_mobile_row_filters(self):
        """
        Returns a set of filters for the mobile row grid.
        """
        batch = self.get_instance()
        filters = grids.filters.GridFilterSet()
        if batch.truck_dump:
            value_choices = ['received', 'damaged', 'expired', 'all']
            default_status = 'all'
        else:
            value_choices = ['incomplete', 'unexpected', 'damaged', 'expired', 'all']
            default_status = 'incomplete'
        filters['status'] = MobileItemStatusFilter('status',
                                                   value_choices=value_choices,
                                                   default_value=default_status)
        return filters

    def mobile_create(self):
        """
        Mobile view for creating a new receiving batch
        """
        mode = self.batch_mode
        data = {'mode': mode}

        form = forms.Form(schema=MobileNewReceivingBatch(), request=self.request)
        if form.validate(newstyle=True):

            if form.validated['workflow'] == 'truck_dump':
                if not self.allow_truck_dump:
                    raise NotImplementedError("Requested workflow not supported: truck_dump")
                batch = self.model_class()
                batch.store = self.rattail_config.get_store(self.Session())
                batch.mode = mode
                batch.truck_dump = True
                batch.vendor = self.Session.merge(form.validated['vendor'])
                batch.created_by = self.request.user
                batch.date_received = localtime(self.rattail_config).date()
                kwargs = self.get_batch_kwargs(batch, mobile=True)
                batch = self.handler.make_batch(self.Session(), **kwargs)
                return self.redirect(self.request.route_url('mobile.receiving.view', uuid=batch.uuid))

            else:
                raise NotImplementedError("Requested workflow not supported: {}".format(form.validated['workflow']))

        vendor = None
        if self.request.method == 'POST' and self.request.POST.get('vendor'):
            vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor'])
            if vendor:
                data['vendor'] = vendor

                if self.request.POST.get('purchase'):
                    purchase = self.get_purchase(self.request.POST['purchase'])
                    if purchase:

                        batch = self.model_class()
                        batch.mode = mode
                        batch.vendor = vendor
                        batch.store = self.rattail_config.get_store(self.Session())
                        batch.buyer = self.request.user.employee
                        batch.created_by = self.request.user
                        kwargs = self.get_batch_kwargs(batch, mobile=True)
                        batch = self.handler.make_batch(self.Session(), **kwargs)
                        if self.handler.should_populate(batch):
                            self.handler.populate(batch)
                        return self.redirect(self.request.route_url('mobile.receiving.view', uuid=batch.uuid))

        data['mode_title'] = self.enum.PURCHASE_BATCH_MODE[mode].capitalize()
        if vendor:
            purchases = self.eligible_purchases(vendor.uuid, mode=mode)
            data['purchases'] = [(p['key'], p['display']) for p in purchases['purchases']]
        return self.render_to_response('create', data, mobile=True)

    def configure_mobile_form(self, f):
        super(ReceivingBatchView, self).configure_mobile_form(f)
        batch = f.model_instance

        # truck_dump
        if not self.creating:
            if not batch.truck_dump:
                f.remove_field('truck_dump')

        # department
        if not self.creating:
            if batch.truck_dump:
                f.remove_field('department')

    def configure_row_form(self, f):
        super(ReceivingBatchView, self).configure_row_form(f)
        f.set_readonly('cases_ordered')
        f.set_readonly('units_ordered')
        f.set_readonly('po_unit_cost')
        f.set_readonly('po_total')
        f.set_readonly('invoice_total')

    def render_mobile_row_listitem(self, row, i):
        description = row.product.full_description if row.product else row.description
        return "({}) {}".format(row.upc.pretty(), description)

    # TODO: this view can create new rows, with only a GET query.  that should
    # probably be changed to require POST; for now we just require the "create
    # batch row" perm and call it good..
    def mobile_lookup(self):
        """
        Locate and/or create a row within the batch, according to the given
        product UPC, then redirect to the row view page.
        """
        batch = self.get_instance()
        row = None
        upc = self.request.GET.get('upc', '').strip()
        upc = re.sub(r'\D', '', upc)
        if not upc:
            self.request.session.flash("Invalid UPC: {}".format(self.request.GET.get('upc')), 'error')
            return self.redirect(self.get_action_url('view', batch, mobile=True))

        # first try to locate existing batch row by UPC match
        provided = GPC(upc, calc_check_digit=False)
        checked = GPC(upc, calc_check_digit='upc')
        rows = self.Session.query(model.PurchaseBatchRow)\
                           .filter(model.PurchaseBatchRow.batch == batch)\
                           .filter(model.PurchaseBatchRow.upc.in_((provided, checked)))\
                           .filter(model.PurchaseBatchRow.removed == False)\
                           .all()

        if rows:
            if len(rows) > 1:
                log.warning("found multiple UPC matches for {} in batch {}: {}".format(
                    upc, batch.id_str, batch))
            row = rows[0]

        else:

            # try to locate general product by UPC; add to batch if found
            product = api.get_product_by_upc(self.Session(), provided)
            if not product:
                product = api.get_product_by_upc(self.Session(), checked)
            if product:
                row = model.PurchaseBatchRow()
                row.product = product
                self.handler.add_row(batch, row)

            # check for "bad" upc
            elif len(upc) > 14:
                self.request.session.flash("Invalid UPC: {}".format(upc), 'error')
                return self.redirect(self.get_action_url('view', batch, mobile=True))

            # product in system, but sane upc, so add to batch anyway
            else:
                row = model.PurchaseBatchRow()
                row.upc = provided # TODO: why not checked? how to know?
                row.description = "(unknown product)"
                batch.add_row(row)
                self.handler.refresh_row(row)
                self.handler.refresh_batch_status(batch)

        self.Session.flush()
        return self.redirect(self.mobile_row_route_url('view', uuid=row.batch_uuid, row_uuid=row.uuid))

    def mobile_view_row(self):
        """
        Mobile view for receiving batch row items.  Note that this also handles
        updating a row.
        """
        self.viewing = True
        row = self.get_row_instance()
        batch = row.batch
        permission_prefix = self.get_permission_prefix()
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'batch': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': pod.get_image_url(self.rattail_config, row.upc),
            'form': form,
        }

        if self.request.has_perm('{}.create_row'.format(permission_prefix)):
            schema = MobileReceivingForm().bind(session=self.Session())
            update_form = forms.Form(schema=schema, request=self.request)
            if update_form.validate(newstyle=True):
                row = self.Session.query(model.PurchaseBatchRow).get(update_form.validated['row'])

                # TODO: surely this (delete_row) should be split out to a separate view
                if update_form.validated['delete_row']:
                    if not self.request.has_perm('{}.delete_row'.format(permission_prefix)):
                        raise httpexceptions.HTTPForbidden()
                    self.handler.remove_row(row)
                    return self.redirect(self.get_action_url('view', batch, mobile=True))

                else: # not delete_row
                    mode = update_form.validated['mode']
                    cases = update_form.validated['cases']
                    units = update_form.validated['units']
                    if cases:
                        setattr(row, 'cases_{}'.format(mode),
                                (getattr(row, 'cases_{}'.format(mode)) or 0) + cases)
                    if units:
                        setattr(row, 'units_{}'.format(mode),
                                (getattr(row, 'units_{}'.format(mode)) or 0) + units)

                    # if mode in ('damaged', 'expired', 'mispick'):
                    if mode in ('damaged', 'expired'):
                        self.attach_credit(row, mode, cases, units,
                                           expiration_date=update_form.validated['expiration_date'],
                                           # discarded=update_form.data['trash'],
                                           # mispick_product=shipped_product)
                        )

                    # first undo any totals previously in effect for the row, then refresh
                    if row.invoice_total:
                        batch.invoice_total -= row.invoice_total
                    self.handler.refresh_row(row)

                    return self.redirect(self.get_action_url('view', batch, mobile=True))

        if not row.cases_ordered and not row.units_ordered and not batch.truck_dump:
            self.request.session.flash("This item was NOT on the original purchase order.", 'receiving-warning')
        return self.render_to_response('view_row', context, mobile=True)

    def attach_credit(self, row, credit_type, cases, units, expiration_date=None, discarded=None, mispick_product=None):
        batch = row.batch
        credit = model.PurchaseBatchCredit()
        credit.credit_type = credit_type
        credit.store = batch.store
        credit.vendor = batch.vendor
        credit.date_ordered = batch.date_ordered
        credit.date_shipped = batch.date_shipped
        credit.date_received = batch.date_received
        credit.invoice_number = batch.invoice_number
        credit.invoice_date = batch.invoice_date
        credit.product = row.product
        credit.upc = row.upc
        credit.vendor_item_code = row.vendor_code
        credit.brand_name = row.brand_name
        credit.description = row.description
        credit.size = row.size
        credit.department_number = row.department_number
        credit.department_name = row.department_name
        credit.case_quantity = row.case_quantity
        credit.cases_shorted = cases
        credit.units_shorted = units
        credit.invoice_line_number = row.invoice_line_number
        credit.invoice_case_cost = row.invoice_case_cost
        credit.invoice_unit_cost = row.invoice_unit_cost
        credit.invoice_total = row.invoice_total
        credit.product_discarded = discarded
        if credit_type == 'expired':
            credit.expiration_date = expiration_date
        elif credit_type == 'mispick' and mispick_product:
            credit.mispick_product = mispick_product
            credit.mispick_upc = mispick_product.upc
            if mispick_product.brand:
                credit.mispick_brand_name = mispick_product.brand.name
            credit.mispick_description = mispick_product.description
            credit.mispick_size = mispick_product.size
        row.credits.append(credit)
        return credit

    @classmethod
    def _receiving_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        model_key = cls.get_model_key()
        permission_prefix = cls.get_permission_prefix()

        # mobile lookup (note perm; this view can create new rows)
        config.add_route('mobile.{}.lookup'.format(route_prefix), '/mobile{}/{{{}}}/lookup'.format(url_prefix, model_key))
        config.add_view(cls, attr='mobile_lookup', route_name='mobile.{}.lookup'.format(route_prefix),
                        renderer='json', permission='{}.create_row'.format(permission_prefix))

        if cls.allow_truck_dump:
            config.add_route('{}.add_child_from_invoice'.format(route_prefix), '{}/{{{}}}/add-child-from-invoice'.format(url_prefix, model_key))
            config.add_view(cls, attr='add_child_from_invoice', route_name='{}.add_child_from_invoice'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

    @classmethod
    def defaults(cls, config):
        cls._receiving_defaults(config)
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)


class MobileNewReceivingBatch(colander.MappingSchema):

    vendor = colander.SchemaNode(forms.types.VendorType())

    workflow = colander.SchemaNode(colander.String(),
                                   validator=colander.OneOf([
                                       'from_po',
                                       'from_scratch',
                                       'truck_dump',
                                   ]))


# TODO: this is a stopgap measure to fix an obvious bug, which exists when the
# session is not provided by the view at runtime (i.e. when it was instead
# being provided by the type instance, which was created upon app startup).
@colander.deferred
def valid_purchase_batch_row(node, kw):
    session = kw['session']
    def validate(node, value):
        row = session.query(model.PurchaseBatchRow).get(value)
        if not row:
            raise colander.Invalid(node, "Batch row not found")
        if row.batch.executed:
            raise colander.Invalid(node, "Batch has already been executed")
        return row.uuid
    return validate


class MobileReceivingForm(colander.MappingSchema):

    row = colander.SchemaNode(colander.String(),
                              validator=valid_purchase_batch_row)

    mode = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf([
                                   'received',
                                   'damaged',
                                   'expired',
                                   # 'mispick',
                               ]))

    cases = colander.SchemaNode(colander.Decimal(), missing=None)

    units = colander.SchemaNode(colander.Decimal(), missing=None)

    expiration_date = colander.SchemaNode(colander.Date(),
                                          widget=dfwidget.TextInputWidget(),
                                          missing=colander.null)

    delete_row = colander.SchemaNode(colander.Boolean())


def includeme(config):
    ReceivingBatchView.defaults(config)
