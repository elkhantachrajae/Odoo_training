from odoo import models, fields

class NegotiationWizard(models.TransientModel):
    _name = 'negotiation.wizard'
    _description = 'Wizard de Négociation'

    new_price = fields.Float(string="Nouveau prix proposé")
    reason = fields.Text(string="Motif de la négociation")

    def action_apply(self):
        property_id = self.env.context.get('active_id')
        print(f"Property ID: {property_id}")
        property_rec = self.env['estate.offer'].browse(property_id)
        
        # On met à jour la propriété
        property_rec.write({
            'price': self.new_price,
        })
        return {'type': 'ir.actions.act_window_close'} 