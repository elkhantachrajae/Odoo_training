from datetime import timedelta
from odoo import models,fields,api
from odoo.exceptions import ValidationError  

class RealEstate(models.Model):
    _name="real.estate"
    _description="Real Estate Model"
    _order="selling_price" #order by selling price 
    active=fields.Boolean(default=True)
    name=fields.Char(default="House", required=True)
    price=fields.Float()
    state=fields.Selection([
        ('new','New'),
        ('sold','Sold'),
        ('offer_received', 'Offer Received'),
        ('cancelled','Cancelled')],default='new',required=True)
    currency_id=fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id)
    
    def _default_date_availability(self):
        return fields.Date.today()
    postcode=fields.Char()
    date_availability=fields.Date(default=_default_date_availability)
    expected_price=fields.Float(currency_field="currency_id")
    selling_price=fields.Float(currency_field="currency_id",readonly=True)
    best_offer_price=fields.Float(string="Best Offer Price", compute="_compute_best_offer_price",store=True)
    bedrooms=fields.Integer(string="Number of Bedrooms", default=2)
    garden=fields.Boolean(string="Has Garden?",default=False)
    living_area=fields.Integer(string="Living Area")
    garden_area=fields.Integer(string="Garden Area")
    orientation=fields.Char(string="Garden Orientation")
    description=fields.Text(string="Description")
    type_id=fields.Many2one("estate.type", string="Type")
    offers_ids=fields.One2many("estate.offer","estate_id", string="Offers") #estate.offer child model, estate_id :parent id
    tag_ids=fields.Many2many("estate.tag", string="Tags")
    total_area=fields.Integer(string="Total Area", compute="_compute_total_area")
    description=fields.Text(string="Description")

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area=record.living_area + record.garden_area
    
    @api.depends("offers_ids.price")
    def _compute_best_offer_price(self):
        for record in self:
            if record.offers_ids:
                record.best_offer_price=max(record.offers_ids.mapped("price")) #mapped : to get the price field from the offers_ids recordset and return a list of prices, then max to get the maximum price
            else:
                record.best_offer_price=0.0
    
    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if not record.garden:
                record.garden_area=0
                record.orientation=None
    
    @api.onchange("date_availability")
    def _onchange_date_availability(self):
        for record in self:
            if record.date_availability and record.date_availability < fields.Date.today():
                return {
                    "warning":{
                        "title":"Date Availability Changed",
                        "message":"The date availability is in the past."
                        }
                }
    @api.constrains("selling_price")
    def _check_selling_price(self):
        for rec in self:
            if rec.selling_price < 0:
                raise ValidationError("The selling price must be positive.")
    
    @api.constrains("expected_price")
    def _check_expected_price(self):
        for rec in self:
            if rec.expected_price < 0:
                raise ValidationError("The expected price must be positive.")