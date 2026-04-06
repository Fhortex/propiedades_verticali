from odoo import models, fields, _, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PropertyContracts(models.Model):
    _name = 'property.contracts'
    _description = 'Contratos de renta'
    
    property_id = fields.Many2one('verticali.property',string='Propiedad', required=True, ondelete="cascade")
    partner_id = fields.Many2one('res.partner', string='Inquilino', required=True)
    email = fields.Char(string='Correo electrónico', required=True)
    phone = fields.Char(string='Teléfono', required=True)
    date_from = fields.Date(string='Fecha de inicio', required=True)
    date_to = fields.Date(string='Fecha de finalización', required=True)
    filename = fields.Char(string='Nombre archivo')
    file = fields.Binary(string='Archivo')

    @api.onchange('partner_id')
    def _check_partner_id(self):
        for r in self:
            r.email = r.partner_id.email
            r.phone = r.partner_id.phone
            
                
    @api.constrains('filename')
    @api.onchange('filename')
    def _check_file_extension(self):
        allowed_extensions = ['.doc', '.pdf']
        for record in self:
            if record.filename:
                if not any(record.filename.lower().endswith(ext) for ext in allowed_extensions):
                    raise ValidationError("Sólo se permiten contratos con archivos .doc y .pdf.")

    def _notify_due_dates(self):
        _logger.error('_notify_due_dates')
        date = fields.Date.today() + timedelta(days=30)
        target_contracts = self.search([('date_to','=',date)])
        _logger.error(date)
        _logger.error(target_contracts)
        _logger.error(target_contracts.mapped('property_id'))
        _logger.error(target_contracts.mapped('property_id.partner_id'))
        for user in target_contracts.mapped('property_id.partner_id'):
            _logger.error(user)
            adviser = user
            if user.user_id:
                adviser = user.user_id.partner_id
            contracts = target_contracts.filtered(lambda x: x.property_id.partner_id == user)
            content = ''
            for c in contracts:
                content  += 'Propiedad: {} (Inquilino: {})<br/>'.format(c.property_id.title, c.partner_id.name)
            _logger.error(content)
            if content:
                # Buscar la plantilla
                template = self.env.ref('property_custom.email_template_contract_due_dates')  # Reemplaza con el m  dulo y el ID de tu plantilla

                if not template:
                    raise ValueError("No se encontr   la plantilla de correo.")

                email_values = {
                    'subject': 'Contratos: pr  ximos vencimientos',
                    'email_to': adviser.email,
                    'body_html': f"""
                        <p>Estimado,</p>
                        <p>A continuaci  n encontrar   un listado de propiedades cuyo contrato de renta vencer   en 30 d  as.</p>
                        <p>{content}</p>
                    """,
                }
                id = self.search([],limit=1).id
                template.send_mail(res_id=id, force_send=True, raise_exception=True, email_values=email_values)
