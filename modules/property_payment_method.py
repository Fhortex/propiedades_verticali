from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyPaymentMethod(models.Model):
    _name = 'property.payment.method'
    _description = 'Forma de pago'
    
    name = fields.Char(string='Nombre', required=True)