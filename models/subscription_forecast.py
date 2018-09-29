# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, timedelta, time
import dateutil.parser
# import datetime
# import time
from odoo.tools import format_date


from dateutil.relativedelta import relativedelta

class SubscriptionForecast(models.Model):
    """ Subscription Forecast Report Analysis """

    _name = "subscription.forecast"
    _description = "Subscription Forecast Report Analysis "

    subscription_id = fields.Many2one('sale.subscription', 'Subscription')
    name = fields.Char('Name', related="subscription_id.name", store=True)

    recurring_amount_total = fields.Float('Total',related="subscription_id.recurring_amount_total", store=True)
    date = fields.Date('Date Invoice')


    @api.constrains('subscription_id')
    def _check_subscrition(self):
        for sub in self:
            if not sub.subscription_id:
                sub.unlink()

class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    subscription_forecast_ids = fields.One2many('subscription.forecast','subscription_id','Subscription Forecast'
                                                , compute='subscription_forecast_report',store=True)
    # @api.multi
    @api.depends('recurring_next_date')
    def subscription_forecast_report(self):
        sub_forecast = []
        today = datetime.today().strftime('%Y-%m-%d')
        today_year = '%02d' % datetime.strptime(today, '%Y-%m-%d').year

        for subscription in self:
            if subscription.state == 'open':
                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                new_date = subscription.recurring_next_date or self.default_get(['recurring_next_date'])[
                    'recurring_next_date']
                months = '%02d' % datetime.strptime(new_date, '%Y-%m-%d').month
                years = '%02d' % datetime.strptime(new_date, '%Y-%m-%d').year

                if years == today_year:
                    sub_forecast.append((0, 0, {
                        'subscription_id': self.id,
                        'date': new_date,

                    }))

                while int(months) < 12 and years == today_year:
                    new_date = (fields.Date.from_string(new_date) + relativedelta(
                        **{periods[subscription.recurring_rule_type]: subscription.recurring_interval})).strftime('%Y-%m-%d')

                    months = '%02d' % datetime.strptime(str(new_date), '%Y-%m-%d').month
                    years = '%02d' % datetime.strptime(str(new_date), '%Y-%m-%d').year

                    if years == today_year:
                        sub_forecast.append((0, 0, {
                            'subscription_id': self.id,
                            'date': new_date,

                        }))
                self.subscription_forecast_ids = sub_forecast


    @api.multi
    def process_forecast(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['sale.subscription'].browse(active_ids):
            record.subscription_forecast_report()