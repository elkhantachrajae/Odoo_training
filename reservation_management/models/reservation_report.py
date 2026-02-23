from odoo import fields, models, tools

class ReservationReport(models.Model):
    _name = 'reservation.report'
    _description = "Analyse des Réservations"
    _auto = False
    _rec_name = 'name'

    # --- Champs du rapport ---
    name = fields.Char(string='Référence', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Client', readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
    ], string='État', readonly=True)
    
    # Mesures
    nbr_lignes = fields.Integer(string='Nb de Lignes', readonly=True)
    total_quantite = fields.Float(string='Quantité Totale', readonly=True, aggregator="sum")
    total_montant = fields.Float(string='Montant Total', readonly=True, aggregator="sum")

    # --- Construction de la requête SQL ---

    def _select(self):
        #min(l.id) est utilisé pour éviter les doublons dans le cas où une réservation a plusieurs lignes
        return """
            SELECT
                min(l.id) as id,
                r.name as name,
                r.partner_id as partner_id,
                r.state as state,
                count(l.id) as nbr_lignes,
                sum(l.quantity) as total_quantite,
                sum(l.price_subtotal) as total_montant
        """

    def _from(self):
        return """
            reservation_reservation r
            JOIN reservation_line l ON r.id = l.reservation_id
        """

    def _group_by(self):
        return """
            GROUP BY
                r.id,
                r.name,
                r.partner_id,
                r.state
        """

    def init(self):
        # Création de la vue PostgreSQL
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                FROM %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._group_by()))