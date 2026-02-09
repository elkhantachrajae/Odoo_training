from datetime import timedelta
from odoo import api,models,fields #ignore
from odoo.exceptions import ValidationError  
class EstateOffer(models.Model):
    _name="estate.offer"
    _description="Estate Offer Model"
    price=fields.Float(required=True)
    status=fields.Selection([
        ('accepted','Accepted'),
        ('refused','Refused')],default='refused',required=True)
    partner_id=fields.Many2one("res.partner", string="Partner", required=True)
    estate_id=fields.Many2one("real.estate", string="Real Estate", required=True)
    type_id=fields.Many2one(related="estate_id.type_id", string="Property Type", store=True)
    validity = fields.Integer(string="Validity", default=7)
    date_deadline=fields.Date(string="Offer Deadline", compute="_compute_date_deadline",inverse="_inverse_date_deadline")

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline=fields.Date.today() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity=(record.date_deadline - fields.Date.today()).days
    
    def action_accept_offer(self):
        self.ensure_one()  # Ensure that only one offer is being accepted
        if "accepted" in self.estate_id.offers_ids.mapped("status"):
            raise ValidationError("An offer has already been accepted for this property.")
        self.status="accepted"
        self.estate_id.selling_price=self.price
        return True
    def action_refuse_offer(self):
        self.ensure_one()
        self.status = "refused"
        return True
    @api.constrains('price')
    def _check_offer_price(self):
        for record in self:
            if record.price <0:
                raise ValidationError("The offer price must be higher than or equal to 0.")
