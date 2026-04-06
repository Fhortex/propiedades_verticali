from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class CommissionShare(models.Model):
    _name = 'property.commission.share'
    _description = 'Compartir comisión'
    
    name = fields.Char(string='Nombre', required=True)