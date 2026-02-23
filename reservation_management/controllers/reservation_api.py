from odoo import http,_
from odoo.http import request

class ReservationApi(http.Controller):

    # 1. CRÉER une réservation (POST)
    @http.route('/api/reservation/create', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def api_reservation_create(self, **kwargs):
        try:
            # Extraction des données a partir de kwargs
            partner_id = kwargs.get('partner_id')
            date_res = kwargs.get('date_reservation')
            date_end_res= kwargs.get('date_end_reservation')
            lines = kwargs.get('reservation_line_ids', [])

            # Création 
            new_res = request.env['reservation.reservation'].create({
                'partner_id': partner_id,
                'date_reservation': date_res,
                'line_ids': lines, 
            })
            return {
                "status": "success",
                "message": _("Réservation créée avec succès"),
                "data": {"id": new_res.id, "name": new_res.name}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # 2. LISTER toutes les réservations
    @http.route('/api/reservations', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def api_reservation_list(self, **kwargs):
        res_list = request.env['reservation.reservation'].search_read(
            [], ['name', 'partner_id', 'date_reservation','date_end_reservation', 'state']
        )
        return {"status": "success", "data": res_list}

    # On utilise kwargs pour récupérer l'ID passé dans le JSON
    @http.route('/api/reservation/detail', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def api_reservation_get(self, **kwargs):
        res_id = kwargs.get('id')
        res = request.env['reservation.reservation'].browse(res_id)
        if not res.exists():
            return {"status": "error", "message": _("Réservation non trouvée")}
        
        return {
            "status": "success",
            "data": {
                "name": res.name,
                "partner": res.partner_id.name,
                "date": res.date_reservation,
                "date_end":res.date_end_reservation,
                "state": res.state
            }
        }

    # 4. CONFIRMER une réservation
    @http.route('/api/reservation/confirm', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def api_reservation_confirm(self, **kwargs):
        res_id = kwargs.get('id')
        res = request.env['reservation.reservation'].sudo().browse(res_id)
        if res.exists():
            res.action_confirm() 
            return {"status": "success", "message": _("Réservation confirmée")}
        return {"status": "error", "message": _("Réservation introuvable")}

    # 5. ANNULER une réservation
    @http.route('/api/reservation/cancel', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def api_reservation_cancel(self, **kwargs):
        res_id = kwargs.get('id')
        res = request.env['reservation.reservation'].sudo().browse(res_id)
        if res.exists():
            res.action_cancel()
            return {"status": "success", "message": _("Réservation annulée")}
        return {"status": "error", "message": _("Réservation introuvable")}