from odoo import models,fields

class EstateTag(models.Model):
    _name="estate.tag"
    _description="Estate Tag Model"

    name=fields.Char(string="Tag Name", required=True)
    color=fields.Integer(string="Color Index")
    property_id=fields.Many2many("real.estate", string="Properties")
    property_type_id=fields.Many2one("estate.type", related="property_id.type_id", string="Property Type", store=True)
    _name_uniq = models.Constraint(
        'unique(name)',
        'A tag with the same name already exists.',
    )