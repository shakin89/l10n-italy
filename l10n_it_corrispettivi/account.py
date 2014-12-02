# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, exceptions, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_account(self):
        is_corrispettivo = self._context.get('corrispettivo', False)
        res = False
        if is_corrispettivo:
            partner_obj = self.env['res.partner']
            partner_ids = partner_obj.search(self._cr, self._uid, [('corrispettivi', '=', True)])
            if not partner_ids:
                raise exceptions.except_orm(_('Error!'), 
                     _('No partner "corrispettivi" found'))
            partner = partner_obj.browse(self._cr, self._uid, partner_ids[0])
            res = partner.property_account_receivable.id
        return res

    def _get_partner_id(self):
        is_corrispettivo = self._context.get('corrispettivo', False)
        res = False
        if is_corrispettivo:
            partner_obj = partner_ids = self.env['res.partner']
            partner_ids=partner_obj.search(self._cr, self._uid, [('corrispettivi', '=', True)])
            if not partner_ids:
                raise exceptions.except_orm(_('Error!'), 
                     _('No partner "corrispettivi" found'))
            res = partner_ids[0]
        return res

    #set default option on inherited field
    corrispettivo = fields.Boolean(string='Corrispettivo')
    account_id = fields.Many2one(default=_get_account)

    def onchange_company_id(self, company_id, part_id, type, invoice_line, currency_id):
        journal_obj = self.env['account.journal']
        
        res = super(AccountInvoice, self).onchange_company_id(company_id, part_id, type, invoice_line, currency_id)
        is_corrispettivo = self._context.get('corrispettivo', False)
        corr_journal_ids = journal_obj.search(self._cr, self._uid, [('corrispettivi','=', True), ('company_id','=', company_id)])

        # if it is a "corrispettivo" and the company has at least one journal "corrispettivi"
        if is_corrispettivo and corr_journal_ids:
            res['value']['journal_id']  = corr_journal_ids[0]

        # if the company has at least one journal "corrispettivi" but the invoice it isn't a corrispettivo
        elif corr_journal_ids and corr_journal_ids[0] in res['domain']['journal_id'][0][2]:
            # if invoice's on_change has set journal corrispettivi
            if corr_journal_ids[0] == res['value']['journal_id'] and len(res['domain']['journal_id'][0][2]) > 1:
                for j_id in res['domain']['journal_id'][0][2]:
                    if corr_journal_ids[0] != j_id:
                        res['value']['journal_id'] = j_id
                        break
        return res

    def onchange_corrispettivo(self, corrispettivo=False):
        res = {}
        user_obj = self.env['res.users']
        journal_obj = self.env['account.journal']
        company_id = user_obj.browse(self._cr,self._uid,self._uid).company_id.id
        corr_journal_ids = journal_obj.search(self._cr, self._uid, [('corrispettivi','=', True), ('company_id','=', company_id)])
        if corr_journal_ids and corrispettivo:
            res = {'value': {'journal_id': corr_journal_ids[0]}}
        return res

    _defaults = {
        'partner_id': _get_partner_id,
        #'account_id': _get_account,
        }

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    corrispettivi = fields.Boolean(string='Corrispettivi')

class ResPartner(models.Model):
    _inherit = 'res.partner'
    corrispettivi = fields.Boolean(string='Corrispettivi')
