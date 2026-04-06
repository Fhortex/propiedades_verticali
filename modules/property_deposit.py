from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyDeposit(models.Model):
    _name = 'property.deposit'
    _description = 'Deposito'
    
    name = fields.Char(string='Nombre', required=True)