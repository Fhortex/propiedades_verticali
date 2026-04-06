from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyInvoice(models.Model):
    _name = 'property.invoice'
    _description = 'Factura'
    
    name = fields.Char(string='Nombre', required=True)