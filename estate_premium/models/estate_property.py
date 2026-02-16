from odoo import models, fields

class EstateProperty(models.Model):
    _inherit = "real.estate"

    commission = fields.Float(string="Commission (%)", default=5.0)
    is_premium = fields.Boolean(string="Est Premium ?")