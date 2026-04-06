from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyTypeTraining(models.Model):
    _name = 'property.type.training'
    _description = 'Tipo de entrenamiento'
    
    name = fields.Char(string='Nombre', required=True)