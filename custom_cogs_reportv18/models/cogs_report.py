from odoo import models, fields, api


class CogsReport(models.TransientModel):
    _name = 'cogs.report'
    _description = 'COGS Report Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    order_type = fields.Selection([
        ('sales', 'Sales'),
        ('pos', 'POS')
    ], string='Order Type', required=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    total_sales_sales = fields.Float(string='Total Sales (Sales)', readonly=True)
    total_cogs_sales = fields.Float(string='Total COGS (Sales)', readonly=True)
    total_profit_sales = fields.Float(string='Total Profit (Sales)', readonly=True)
    gross_profit_percent_sales = fields.Float(string='Profit % (Sales)', readonly=True)

    total_sales_pos = fields.Float(string='Total Sales (POS)', readonly=True)
    total_cogs_pos = fields.Float(string='Total COGS (POS)', readonly=True)
    total_profit_pos = fields.Float(string='Total Profit (POS)', readonly=True)
    gross_profit_percent_pos = fields.Float(string='Profit % (POS)', readonly=True)

    report_lines = fields.One2many('cogs.report.line', 'report_id', string='Report Lines')

    def compute_report(self):
        """Compute COGS, Sales, Profit, and Gross Profit %"""
        for wizard in self:
            wizard.report_lines = [(5, 0, 0)]

            total_sales_amount = total_sales_cogs = total_sales_profit = 0
            total_pos_amount = total_pos_cogs = total_pos_profit = 0
            product_dict = {}

            if wizard.order_type == 'sales':
                sale_orders = self.env['sale.order'].search([
                    ('state', 'in', ['sale', 'done']),
                    ('date_order', '>=', wizard.date_from),
                    ('date_order', '<=', wizard.date_to),
                    ('company_id', '=', wizard.company_id.id),
                ])
                for order in sale_orders:
                    for line in order.order_line:
                        pid = line.product_id.id
                        pdata = product_dict.setdefault(pid, {
                            'product_id': pid,
                            'qty_sales': 0, 'sale_sales': 0, 'cogs_sales': 0, 'profit_sales': 0,
                            'qty_pos': 0, 'sale_pos': 0, 'cogs_pos': 0, 'profit_pos': 0,
                        })

                        cogs = line.product_id.standard_price * line.product_uom_qty
                        sale_price = line.price_total
                        profit = sale_price - cogs

                        pdata['qty_sales'] += line.product_uom_qty
                        pdata['sale_sales'] += sale_price
                        pdata['cogs_sales'] += cogs
                        pdata['profit_sales'] += profit

                        total_sales_amount += sale_price
                        total_sales_cogs += cogs
                        total_sales_profit += profit








            elif wizard.order_type == 'pos':

                from datetime import datetime, time

                date_from_dt = datetime.combine(wizard.date_from, time.min)

                date_to_dt = datetime.combine(wizard.date_to, time.max)

                pos_orders = self.env['pos.order'].search([

                    ('state', '=', 'done'),

                    ('session_id.state', '=', 'closed'),

                    ('date_order', '>=', date_from_dt),

                    ('date_order', '<=', date_to_dt),

                    ('company_id', '=', wizard.company_id.id),

                ])

                for order in pos_orders:

                    for line in order.lines:

                        if not line.product_id:
                            continue

                        pid = line.product_id.id

                        pdata = product_dict.setdefault(pid, {

                            'product_id': pid,

                            'qty_sales': 0, 'sale_sales': 0, 'cogs_sales': 0, 'profit_sales': 0,

                            'qty_pos': 0, 'sale_pos': 0, 'cogs_pos': 0, 'profit_pos': 0,

                        })

                        qty = line.qty or 0.0

                        # 🔥 IMPORTANT: Use subtotal incl tax

                        line_sale = line.price_subtotal_incl

                        # 🔥 ADD TO TOTAL POS SALES FROM LINES (NOT ORDER)

                        total_pos_amount += line_sale

                        # COGS

                        cogs = line.product_id.standard_price * abs(qty)

                        profit = line_sale - cogs

                        pdata['qty_pos'] += qty

                        pdata['sale_pos'] += line_sale

                        pdata['cogs_pos'] += cogs

                        pdata['profit_pos'] += profit

                        total_pos_cogs += cogs

                        total_pos_profit += profit

            # Add report lines
            wizard.report_lines = [(0, 0, {
                'product_id': pdata['product_id'],
                'qty_sold_sales': pdata['qty_sales'],
                'sale_price_sales': pdata['sale_sales'],
                'cogs_sales': pdata['cogs_sales'],
                'profit_sales': pdata['profit_sales'],
                'qty_sold_pos': pdata['qty_pos'],
                'sale_price_pos': pdata['sale_pos'],
                'cogs_pos': pdata['cogs_pos'],
                'profit_pos': pdata['profit_pos'],
            }) for pdata in product_dict.values()]

            # Update totals
            wizard.total_sales_sales = total_sales_amount
            wizard.total_cogs_sales = total_sales_cogs
            wizard.total_profit_sales = total_sales_profit
            wizard.gross_profit_percent_sales = (
                    total_sales_profit / total_sales_amount * 100) if total_sales_amount else 0

            wizard.total_sales_pos = total_pos_amount
            wizard.total_cogs_pos = total_pos_cogs
            wizard.total_profit_pos = total_pos_profit
            wizard.gross_profit_percent_pos = (total_pos_profit / total_pos_amount * 100) if total_pos_amount else 0

    @api.onchange('date_from', 'date_to', 'order_type')
    def _onchange_fields(self):
        if self.date_from and self.date_to and self.order_type:
            self.compute_report()

    def action_download_pdf(self):
        """Generate and return the COGS PDF report"""
        if self.date_from and self.date_to and self.order_type:
            self.compute_report()
        return self.env.ref('custom_cogs_report.action_report_cogs').report_action(self)


class CogsReportLine(models.TransientModel):
    _name = 'cogs.report.line'
    _description = 'COGS Report Line'

    report_id = fields.Many2one('cogs.report', string='Report')
    product_id = fields.Many2one('product.product', string='Product')

    qty_sold_sales = fields.Float(string='Quantity Sold (Sales)')
    sale_price_sales = fields.Float(string='Sales Price (Sales)')
    cogs_sales = fields.Float(string='COGS (Sales)')
    profit_sales = fields.Float(string='Profit (Sales)')

    qty_sold_pos = fields.Float(string='Quantity Sold (POS)')
    sale_price_pos = fields.Float(string='Sales Price (POS)')
    cogs_pos = fields.Float(string='COGS (POS)')
    profit_pos = fields.Float(string='Profit (POS)')
