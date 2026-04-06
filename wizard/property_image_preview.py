# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ImagePreview(models.TransientModel):
    _name = 'property.image.preview'
    _description = 'Previsualizador de imagenes'

    property_id = fields.Many2one('verticali.property', string='Propiedad')
    image_ids = fields.One2many(related='property_id.image_ids', string='Imagenes')