# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_order_type(self):
        if not self._context.get('type') in ('in_invoice', 'in_refund'):
            return self.env['sale.order.type'].search([], limit=1)

    sale_type_id = fields.Many2one(
        comodel_name='sale.order.type',
        string='Sale Type', default=_get_order_type)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            if self.partner_id.sale_type:
                self.sale_type_id = self.partner_id.sale_type.id

    @api.onchange('sale_type_id')
    def onchange_sale_type_id(self):
        if self.sale_type_id.payment_term_id:
            self.payment_term = self.sale_type_id.payment_term_id.id
        if self.sale_type_id.journal_id:
            self.journal_id = self.sale_type_id.journal_id.id
