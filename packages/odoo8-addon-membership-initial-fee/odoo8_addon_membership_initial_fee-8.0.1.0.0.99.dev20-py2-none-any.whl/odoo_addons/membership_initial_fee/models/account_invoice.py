# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingenieria S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _prepare_initial_fee_vals(self, invoice_line):
        product = invoice_line.product_id
        product_fee = invoice_line.product_id.product_fee
        line_vals = {
            'product_id': product_fee.id,
            'quantity': 1.0,
            'invoice_id': invoice_line.invoice_id.id,
            'account_analytic_id': invoice_line.account_analytic_id.id,
        }
        line_dict = self.product_id_change(
            product_fee.id, False, line_vals['quantity'], '',
            'out_invoice', invoice_line.invoice_id.partner_id.id,
            invoice_line.invoice_id.fiscal_position.id)
        line_vals.update(line_dict['value'])
        if product.initial_fee == 'fixed':
            line_vals['price_unit'] = product.fixed_fee
        elif product.initial_fee == 'percentage':
            line_vals['price_unit'] = (
                product.percentage_fee * invoice_line.price_unit / 100)
        line_vals['name'] = _('Membership initial fee')
        if line_vals.get('invoice_line_tax_id', False):
            line_vals['invoice_line_tax_id'] = [
                (6, 0, line_vals['invoice_line_tax_id'])]
        return line_vals

    @api.model
    def initial_fee_create_check(self, product, invoice_line):
        """Inherit this method to implement a custom method
           to decide whether or not to create the initial fee
        """
        if not product.membership or product.initial_fee == 'none':
            return False
        # See if partner has any membership line to decide whether or not
        # to create the initial fee
        member_lines = self.env['membership.membership_line'].search([
            ('partner', '=', invoice_line.invoice_id.partner_id.id),
            ('account_invoice_line', 'not in', (invoice_line.id, )),
            ('state', 'not in', ['none', 'canceled']),
        ])
        return not bool(member_lines)

    @api.model
    def create(self, vals):
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        product = self.env['product.product'].browse(
            vals.get('product_id'))
        if self.initial_fee_create_check(product, invoice_line):
            # Charge initial fee
            self.create(self._prepare_initial_fee_vals(invoice_line))
        return invoice_line
