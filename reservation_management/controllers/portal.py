from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http

class ReservationPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # Affiche le nombre de réservations sur la page d'accueil du portail
        values['reservation_count'] = request.env['reservation.reservation'].search_count([])
        return values

    @http.route(['/my/reservations', '/my/reservations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_reservations(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        reservation_obj = request.env['reservation.reservation']
        
        # Sécurité : On ne montre que les réservations du client connecté !
        domain = [('partner_id', '=', request.env.user.partner_id.id)]
        
        # Gestion de la pagination
        res_count = reservation_obj.search_count(domain)
        pager = portal_pager(url="/my/reservations", total=res_count, page=page, step=10)
        
        reservations = reservation_obj.search(domain, limit=10, offset=pager['offset'])
        values.update({
            'reservations': reservations,
            'pager': pager,
            'default_url': '/my/reservations',
        })
        return request.render("reservation_management.portal_my_reservations_template", values)
    
    @http.route(['/my/reservations/<int:res_id>'], type='http', auth="user", website=True)
    def portal_reservation_page(self, res_id, **kw):
        """Affiche le détail d'une réservation spécifique."""
        try:
            # Sécurité : on vérifie que la réservation existe et appartient au client
            # On utilise sudo() si l'utilisateur portal n'a pas les droits en lecture directe
            res_sudo = self._document_check_access('reservation.reservation', res_id)
        except Exception:
            # Si accès refusé ou ID inexistant, retour à la liste
            return request.redirect('/my/reservations')

        values = {
            'res': res_sudo, # La variable 'res' utilisée dans ton XML
            'page_name': 'reservation',
        }
        
        # On retourne le template de détail
        return request.render("reservation_management.portal_reservation_page", values)