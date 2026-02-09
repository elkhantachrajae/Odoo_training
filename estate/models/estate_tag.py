from odoo import models,fields

class EstateTag(models.Model):
    _name="estate.tag"
    _description="Estate Tag Model"

    name=fields.Char(string="Tag Name", required=True)
    color=fields.Integer(string="Color Index")
    property_id=fields.Many2many("real.estate", string="Properties")
    property_type_id=fields.Many2one("estate.type", related="property_id.type_id", string="Property Type", store=True)
    _sql_constraints=[("unique_name","unique(name)","Tag name must be unique.")]
    _sql_constraints=[("unique_type_name","unique(property_type_id,name)","Tag name must be unique for each property type.")]