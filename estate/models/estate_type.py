from odoo import _, models, fields,api

class EstateType(models.Model):
    _name = "estate.type"
    _description = "Estate Type Model"

    name = fields.Char(string="Type Name", required=True)
    property_ids = fields.One2many("real.estate", "type_id", string="Properties")
    lines_count = fields.Integer(compute="_compute_lines_count")
    @api.depends("property_ids")
    def _compute_lines_count(self):
        for record in self:
            record.lines_count = len(record.property_ids)
    def action_open_properties(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Properties"),
            "res_model": "real.estate",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("type_id", "=", self.id)],
            "context":{"default_type_id": self.id},
        }