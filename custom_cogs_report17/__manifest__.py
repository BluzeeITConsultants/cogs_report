{
    'name': 'Custom COGS Report',
    'version': '17.0.1.0.0',
    'category': 'Accounting',

    'author': 'Bluzee IT Consultants',
    'website': 'https://www.bluzee.xyz',
    'summary': 'Compute Cost of Goods Sold and Profit for Sales and POS',
    'description': """Module to calculate COGS and Profit for POS and Sales separately with daily, monthly, or custom date range filters""",

    'depends': [
        'base',
        'sale',
        'point_of_sale',
        'product',
        'account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/cogs_report_views.xml',
        'views/cogs_report_menus.xml',
        'reports/cogs_report_qweb.xml',
        'reports/cogs_report_action.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
