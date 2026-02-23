import io
import base64
import logging
import xlsxwriter
from odoo import models,fields
from odoo.exceptions import ValidationError


class ReservationExcelWizard(models.TransientModel):
    _name = 'reservation.excel.wizard'
    _description = 'Wizard Export Excel Réservations'

    filtre_date = fields.Date(string="Date", required=True)

    def action_generate_excel(self):
        active_ids = self.env.context.get('active_ids')
        reservations = self.env['reservation.reservation'].browse(active_ids)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet_created= False
        for res in reservations:
            logging.info(f"Traitement de la réservation : {res.name} avec date {res.date_reservation}")
            if not self.filtre_date:
                    raise ValidationError("Veuillez sélectionner une date pour filtrer les réservations.")
            if  self.filtre_date>= res.date_reservation and self.filtre_date<= res.date_end_reservation:
                # 1. Nettoyer le nom de la feuille 
                clean_name = "".join(c for c in res.name if c not in r"\/?*[]")[:31]
                # 2. Création de l'onglet
                sheet = workbook.add_worksheet(clean_name)
                sheet_created = True
                # 3. Définir les formats (Styles)
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
                text_format = workbook.add_format({'border': 1})
                num_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})

                # 4. Écrire les en-têtes
                headers = ['Référence', 'Client', 'Produit', 'Quantité', 'Total Ligne']
                for col, header in enumerate(headers):
                    sheet.write(0, col, header, header_format)

                # 5. Remplir les données
                row = 1
                for line in res.line_ids:
                    logging.info(f"  Ligne : {line.product_id.name}, Quantité : {line.quantity}, Sous-total : {line.price_subtotal}")
                    sheet.write(row, 0, res.name, text_format)
                    sheet.write(row, 1, res.partner_id.name, text_format)
                    sheet.write(row, 2, line.product_id.name, text_format)
                    sheet.write(row, 3, line.quantity, text_format)
                    sheet.write(row, 4, line.price_subtotal, num_format)
                    row += 1
        if not sheet_created:
            workbook.close()
            raise ValidationError("Aucune réservation ne correspond à la date sélectionnée.")
        workbook.close()
        output.seek(0)

        # 6. Créer l'attachement pour le téléchargement
        file_base64 = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Rapport_Reservations.xlsx',
            'type': 'binary',
            'datas': file_base64,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # 7. Lancer le téléchargement automatique
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }