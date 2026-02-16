from datetime import timedelta
from odoo import models,fields,api
from odoo.exceptions import ValidationError  

class RealEstate(models.Model):
    _name="real.estate"
    _description="Real Estate Model"
    _order="selling_price" #order by selling price 
    _inherit=["mail.thread","mail.activity.mixin"] #to add chatter to the model

    active=fields.Boolean(default=True)
    name=fields.Char(default="House", required=True,tracking=True) #tracking to track changes in the name field in the chatter
    price=fields.Float()
    state=fields.Selection([
        ('new','New'),
        ('sold','Sold'),
        ('offer_received', 'Offer Received'),
        ('cancelled','Cancelled')],default='new',required=True,tracking=True)
    currency_id=fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id)
    
    def _default_date_availability(self):
        return fields.Date.today()
    postcode=fields.Char()
    date_availability=fields.Date(default=_default_date_availability,tracking=True)
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
    offer_high_count=fields.Integer(string="Number of Offers", compute="_compute_offer_high_count")

    def _compute_offer_high_count(self):
        for record in self:
            # On compte uniquement les offres liées dont le prix > 5000
            offers = self.env['estate.offer'].search_count([
                ('price', '>', 5000),
                ('estate_id', '=', record.id)
            ])
            record.offer_high_count = offers

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
            

    def action_show_offers(self):
        max_offer = self.env['estate.offer'].search(
        [('price', '>', 5000),('estate_id', '=', self.id)], 
        order='price desc', 
        limit=1
        )
        # 2. On définit le prix par défaut (le max trouvé, ou 5001 si rien n'existe)
        default_price = max_offer.price if max_offer else 5001
        return {
            "type": "ir.actions.act_window",
            "name": "Offers",
            "res_model": "estate.offer",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("price", ">", 5000),("estate_id", "=", self.id)],
            "context": {"default_price": default_price,"default_estate_id": self.id,"enable_decoration": True,"status":"accepted"},
        }
    def write(self, vals):
        # 1. On exécute la sauvegarde standard et on récupère le résultat
        res = super(RealEstate, self).write(vals)

        # 2. On vérifie si le champ 'state' est dans les valeurs modifiées
        # et si sa nouvelle valeur est 'offer_received'
        if 'state' in vals and vals['state'] == 'offer_received':
            for record in self:
                # 3. Création de l'activité
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary="Nouvelle offre à vérifier",
                    note=f"L'état de {record.name} est passé en Offre Reçue. Veuillez analyser les documents.",
                    user_id=record.create_uid.id,  # Assigner à l'utilisateur qui a créé l'enregistrement
                    date_deadline=fields.Date.today()
                )
        
        return res
    def action_open_email_wizard(self):
        self.ensure_one()        
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new', # Ouvre dans une fenêtre pop-up
            'context': {
                #'default_model': 'real.estate',
                'default_res_ids': self.ids,
                'default_use_template': True,
                #'active_model': 'real.estate',
                 #'default_template_id': template.id if template else False,
                'default_composition_mode': 'comment',
                'force_email': True,
            },
        }
    