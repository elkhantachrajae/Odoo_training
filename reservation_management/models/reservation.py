from odoo import models, fields, api

class Reservation(models.Model):
    _name = 'reservation.reservation'
    _description = 'Gestion des Réservations'

    name = fields.Char(string="Reference", required=True,copy=False, readonly=True, default=lambda self: 'Nouvelle Réservation')
    date_reservation = fields.Date(string="Date de Réservation", required=True)
    partner_id = fields.Many2one('res.partner', string="Client", required=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée')
    ], default='draft', string="Statut")

    line_ids = fields.One2many('reservation.line', 'reservation_id', string="Lignes de Réservation")
    sale_order_id = fields.Many2one('sale.order', string="Devis Lié", readonly=True)
    amount_total = fields.Float(string="Montant Total", compute="_compute_amount_total")

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouvelle Réservation') == 'Nouvelle Réservation':
            # On appelle la séquence via son 'code' défini dans le XML
            vals['name'] = self.env['ir.sequence'].next_by_code('reservation.reservation') or 'Nouvelle Réservation'
        return super(Reservation, self).create(vals)