from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_cancel(self):
        # 1. On récupère toutes les réservations liées à ce devis
        reservations = self.env['reservation.reservation'].search([('sale_order_id', 'in', self.ids)])
        
        # 2. On appelle votre méthode d'annulation (declaree sur reservation)
        if reservations:
            reservations.action_cancel()
            
        # 3. On exécute l'annulation standard du devis (super)
        return super(SaleOrder, self).action_cancel()