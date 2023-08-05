# -*- coding: utf-8 -*-
#
#    Author: Romain Deheele
#    Copyright 2014-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import logging
import time

from openerp import fields, osv
from openerp.osv import orm
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT
from openerp.addons.logistic_requisition.model.logistic_requisition import (
    LogisticsRequisition as base_logistic_requisition
)

_logger = logging.getLogger(__name__)


class logistic_requisition(orm.Model):
    _inherit = "logistic.requisition"

    _columns = {
        'total_budget': osv.fields.function(
            lambda self, *args, **kwargs: self._get_amount(*args, **kwargs),
            digits_compute=dp.get_precision('Account'),
            string='Total Budget',
            store={
                'logistic.requisition': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['line_ids'], 20),
                'logistic.requisition.line': (
                    lambda self, *a, **kw: self._store_get_requisition_ids(
                        *a, **kw),
                    ['requested_qty', 'budget_unit_price',
                     'budget_tot_price', 'requisition_id'], 20),
            }),
        'budget_holder_id': osv.fields.many2one(
            'res.users',
            states=base_logistic_requisition.REQ_STATES,
            string='Budget Holder'),
        'date_budget_holder': osv.fields.datetime(
            'Budget Holder Validation Date',
            states=base_logistic_requisition.REQ_STATES),
        'budget_holder_remark': osv.fields.text(
            'Budget Holder Remark',
            states=base_logistic_requisition.REQ_STATES),
        'finance_officer_id': osv.fields.many2one(
            'res.users',
            string='Finance Officer',
            states=base_logistic_requisition.REQ_STATES),
        'date_finance_officer': osv.fields.datetime(
            'Finance Officer Validation Date',
            states=base_logistic_requisition.REQ_STATES),
        'finance_officer_remark': osv.fields.text(
            'Finance Officer Remark',
            states=base_logistic_requisition.REQ_STATES),
    }

    requester_validator_id = fields.Many2one(
        'res.partner',
        string='Requester',
        states=base_logistic_requisition.REQ_STATES)
    date_requester_validation = fields.Datetime(
        'Requester Validation Date',
        states=base_logistic_requisition.REQ_STATES)
    requester_remark = fields.Text(
        'Requester Remark',
        states=base_logistic_requisition.REQ_STATES)

    def _get_amount(self, cr, uid, ids, name, args, context=None):
        """Compute the requisition total budget"""
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            res[requisition.id] = sum(line.budget_tot_price for line
                                      in requisition.line_ids)
        return res

    def _do_draft(self, cr, uid, ids, context=None):
        """Cancel LR and related budget"""
        super(logistic_requisition, self)._do_draft(cr, uid, ids,
                                                    context=context)
        vals = {'state': 'draft',
                'budget_holder_id': False,
                'date_budget_holder': False,
                'finance_officer_id': False,
                'date_finance_officer': False,
                'cancel_reason_id': False,
                }
        self.write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, record_id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'budget_holder_id': False,
            'date_budget_holder': False,
            'finance_officer_id': False,
            'date_finance_officer': False,
        })
        return super(logistic_requisition, self
                     ).copy(cr,
                            uid,
                            record_id,
                            default=default,
                            context=context)

    def onchange_validate(self, cr, uid, ids, validate_id,
                          date_validate, date_field_name, context=None):
        values = {}
        if validate_id and not date_validate:
            values[date_field_name] = time.strftime(DT_FORMAT)
        return {'value': values}


class logistic_requisition_line(orm.Model):
    _inherit = "logistic.requisition.line"

    REQUEST_STATES = {'assigned': [('readonly', True)],
                      'sourced': [('readonly', True)],
                      'quoted': [('readonly', True)],
                      }
    STATES = [('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('assigned', 'Assigned'),
              ('sourced', 'Sourced'),
              ('quoted', 'Quoted'),
              ('cancel', 'Cancelled')
              ]

    _columns = {
        'budget_tot_price': osv.fields.float(
            'Budget Total Price',
            states=REQUEST_STATES,
            digits_compute=dp.get_precision('Account')),
        'budget_unit_price': osv.fields.function(
            lambda self, *args, **kwargs: self._get_unit_amount_line(
                *args, **kwargs),
            string='Budget Unit Price',
            type="float",
            digits_compute=dp.get_precision('Account'),
            store=True),
    }

    def _get_unit_amount_line(self, cr, uid, ids, prop, unknow_none,
                              unknow_dict, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.budget_tot_price / line.requested_qty
            res[line.id] = price
        return res
