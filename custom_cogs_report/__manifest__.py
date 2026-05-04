{
    'name': 'custom_cogs',
    'version': '1.0',
    'category': 'Accounting',
    'website':'https://www.bluzee.xyz',
    'summary': 'Compute Cost of Goods Sold and Profit for Sales and POS',
    'description': """Module to calculate COGS and Profit for POS and Sales separately with daily, monthly, or custom date range filters""",
    'depends': ['base', 'sale', 'point_of_sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/cogs_report_views.xml',
        'views/cogs_report_menus.xml',
        'reports/cogs_report_qweb.xml',
        'reports/cogs_report_action.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'price': 0,  # change if paid
    'currency': 'USD',
    'auto_install': False,
}
