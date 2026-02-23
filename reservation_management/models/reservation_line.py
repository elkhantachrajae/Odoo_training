from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class ReservationLine(models.Model):
    _name = 'reservation.line'
    _description = 'Ligne de Réservation'

    reservation_id = fields.Many2one('reservation.reservation', string="Réservation", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Produit", required=True)
    quantity = fields.Float(string="Quantité", required=True, default=1.0)
    price_unit = fields.Float(string="Prix Unitaire", required=True)
    price_subtotal = fields.Float(string="Sous-Total", compute="_compute_price_subtotal",store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.constrains('quantity')
    def _check_quantity(self):
        if self.quantity < 0:
            raise ValidationError(_("La quantité ne peut pas être négative pour le produit."))   

    @api.constrains('price_unit')
    def check_price_unit(self):
        if self.price_unit < 0:
            raise ValidationError(_("Le prix unitaire ne peut pas être négative."))