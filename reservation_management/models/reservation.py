from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Reservation(models.Model):
    _name = 'reservation.reservation'
    _description = 'Gestion des Réservations'
    _inherit = ['mail.thread','portal.mixin']

    name = fields.Char(string="Reference", required=True,copy=False, readonly=True, default=lambda self: 'Nouvelle Réservation')
    date_reservation = fields.Date(string="Date de Réservation", required=True)
    date_end_reservation = fields.Date(string="Date de Fin de Réservation", required=True)
    partner_id = fields.Many2one('res.partner', string="Client", required=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée')
    ], default='draft', string="Statut",tracking=True)

    line_ids = fields.One2many('reservation.line', 'reservation_id', string="Lignes de Réservation")
    sale_order_id = fields.Many2one('sale.order', string="Devis Lié", readonly=True)
    amount_total = fields.Float(string="Montant Total", compute="_compute_amount_total")
    description= fields.Text(string="Description")


    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('price_subtotal'))

    @api.constrains('date_reservation')
    def _check_date_reservation(self):
        for record in self:
            if record.date_reservation < fields.Date.today():
                raise ValidationError(_("La date de réservation n'est pas valide."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouvelle Réservation') == 'Nouvelle Réservation':
                # On appelle la séquence via son 'code' défini dans le XML
                vals['name'] = self.env['ir.sequence'].next_by_code('reservation.reservation') or _('Nouvelle Réservation')
        return super(Reservation, self).create(vals_list)
    
    def action_confirm(self):
        for reservation in self:
            if not reservation.line_ids:
                raise ValidationError(_("Une réservation doit avoir au moins une ligne."))
            
            # 1. Préparer les lignes de commande
            order_lines = []
            for line in reservation.line_ids:
                order_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'name': line.product_id.display_name, # Champ requis sur sale.order.line
                }))

            # 2. Créer le devis (Sale Order)
            sale_order = self.env['sale.order'].create({
                'partner_id': reservation.partner_id.id,
                'date_order': fields.Date.today(),
                'origin': reservation.name,
                'order_line': order_lines, # On crée les lignes en même temps que le devis
            })

            # 3. Mettre à jour la réservation
            reservation.write({
                'sale_order_id': sale_order.id,
                'state': 'confirmed',
            })
        return True
    def action_cancel(self):
        for reservation in self:
            reservation.state = 'cancelled'
        for reservation in self:
            reservation.write({'state': 'cancelled'})


    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Devis associé',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }
    def action_imprimer_reservation(self):
        self.ensure_one()
        return self.env.ref('reservation_management.action_reservation_report').report_action(self)
        
