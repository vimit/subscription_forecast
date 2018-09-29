#-*- coding:utf-8 -*-
from __future__ import division
from odoo import models, fields, api
from datetime import date, datetime, timedelta, time
import dateutil.parser
from odoo.addons import decimal_precision as dp



class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    annual_interest = fields.Float("Interest %", help="Annual Interest Percent")
    second_interest = fields.Float(string="Second Interest %", help="Second Interest applied after 60 days from due date")
    amount_limit_second_interest = fields.Float(string="Lump Amount")

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    number_days = fields.Integer('Delay Days')
    total_interest = fields.Float(string="Total interest", digits=dp.get_precision('Account'))
    annual_interest = fields.Float(string="Interest %", related="payment_term_id.annual_interest", help="Annual Interest Percent")
    second_interest = fields.Float(string="Second interest %", related="payment_term_id.second_interest")
    amount_limit_second_interest = fields.Float(string="Lump Amount", related="payment_term_id.amount_limit_second_interest")

    # This function is called when the scheduler goes on
    @api.model
    def process_scheduler_interest(self):
        self.calcul_interest()

    @api.multi
    def calcul_interest(self):
        account_invoices = self.search([('type', '=', 'out_invoice'),('state', '=', 'open')])
        template_res = self.env['mail.template']
        imd_res = self.env['ir.model.data']
        for account in account_invoices:
            d = datetime.today().strftime('%Y-%m-%d')
            date = dateutil.parser.parse(d).date()
            dd = date.strftime("%Y-%m-%d")
            date1 = datetime.strptime(dd, '%Y-%m-%d').date()
            date2 = datetime.strptime(account.date_due, '%Y-%m-%d').date()
            diff = (date1 - date2).days


            total_interest = 0
            if diff == 20 or diff % 30 == 0:
                total_interest = (account.amount_untaxed * (account.annual_interest/365)  * diff)/100

            if diff >= 60 and diff % 30 == 0:
                second_interest = (account.amount_untaxed * (account.second_interest /365)  * diff)/ 100
                if second_interest < account.amount_limit_second_interest:
                    total_interest = total_interest + account.amount_limit_second_interest
                else:
                    total_interest = total_interest + second_interest
            if total_interest > account.total_interest:
                vals = {
                    'number_days': diff,
                    'total_interest': total_interest,
                    'amount_total': account.amount_untaxed + total_interest + account.amount_tax,
                    'residual': account.amount_untaxed + total_interest + account.amount_tax,
                    'residual_signed': account.amount_untaxed + total_interest + account.amount_tax,
                    'amount_total_company_signed': account.currency_id.compute(
                        account.amount_untaxed + total_interest + account.amount_tax,
                        account.company_id.currency_id),
                    'amount_total_signed': account.amount_untaxed + total_interest + account.amount_tax,
                }
                _, template_id = imd_res.get_object_reference('subscription_forecast',
                                                              'email_invoice_reminder')
                template = template_res.browse(template_id)
                template.send_mail(account.id)

            else:
                vals=({
                    'number_days': diff,
                })



            account.write(vals)

    @api.multi
    def process_manual_interest(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            record.manual_calcul_interest()

    @api.multi
    def manual_calcul_interest(self):
        account = self
        if self.state=='open' and self.type=='out_invoice':
            d = datetime.today().strftime('%Y-%m-%d')
            date = dateutil.parser.parse(d).date()
            dd = date.strftime("%Y-%m-%d")
            date1 = datetime.strptime(dd, '%Y-%m-%d').date()
            date2 = datetime.strptime(self.date_due, '%Y-%m-%d').date()
            diff = (date1 - date2).days

            total_interest = 0
            if diff == 20 or diff // 30 > 0:
                total_interest = (self.amount_untaxed * (self.annual_interest/365)  * diff)/100

            if diff >= 60:
                second_interest = (self.amount_untaxed * (self.second_interest/365) * diff) / 100
                print('---ss----',(self.second_interest/365) * 60)
                if second_interest < self.amount_limit_second_interest:
                    total_interest = total_interest + self.amount_limit_second_interest
                else:
                    total_interest = total_interest + second_interest
            if total_interest > self.total_interest:
                vals = {
                    'number_days': diff,
                    'total_interest': total_interest,
                    'amount_total': self.amount_untaxed + total_interest + self.amount_tax,
                    'residual': self.amount_untaxed + total_interest + self.amount_tax,
                    'residual_signed': self.amount_untaxed + total_interest + self.amount_tax,
                    'amount_total_company_signed': self.currency_id.compute(
                        self.amount_untaxed + total_interest + self.amount_tax,
                        self.company_id.currency_id),
                    'amount_total_signed': self.amount_untaxed + total_interest + self.amount_tax,
                }
            else:
                vals = ({
                    'number_days': diff,
                })

            self.write(vals)