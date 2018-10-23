# Copyright 2018 VIM IT

{
    'name': 'Sale Subscription Forecast',
    'version': '11.1.4',
    'category': 'Customization',
    'license': 'AGPL-3',
    'author': "VIM IT ",
    'website':'vimit.io',
    'depends': ['base', 'sale_subscription'],
    'data': [

        'security/ir.model.access.csv',

        'views/subscription_view.xml',
        'views/subscription_forecast_view.xml',
        'views/invoice_view.xml',
        'views/interest_scheduled_action.xml'

    ],
    'installable': True,
}
