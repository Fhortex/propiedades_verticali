from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyCustomerProfile(models.Model):
    _name = 'property.customer.profile'
    _description = 'Perfil de cliente'
    
    name = fields.Char(string='Nombre', required=True)