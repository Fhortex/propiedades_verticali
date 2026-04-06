# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
import logging
import base64

_logger = logging.getLogger(__name__)


class UploadImageLine(models.TransientModel):
    _name = 'upload.images.line'
    _description = 'Línea de imagen a subir'
    _order = 'sequence'

    wizard_id = fields.Many2one('upload.images', string='Wizard', ondelete='cascade')
    sequence = fields.Integer(string='Secuencia', default=10)
    name = fields.Char(string='Nombre')
    image = fields.Binary(string='Imagen', required=True, attachment=False)


class UploadImages(models.TransientModel):
    _name = 'upload.images'
    _description = 'Subir imágenes'

    property_id = fields.Many2one('verticali.property', string='Propiedad', required=True)
    image_line_ids = fields.One2many('upload.images.line', 'wizard_id', string='Imágenes')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_id'):
            res['property_id'] = self.env.context['active_id']
        elif self.env.context.get('default_property_id'):
            res['property_id'] = self.env.context['default_property_id']
        return res

    def action_upload(self):
        """Sube las imágenes al registro de propiedad."""
        self.ensure_one()
        if not self.property_id:
            raise UserError('Debe seleccionar una propiedad.')
        if not self.image_line_ids:
            raise UserError('Debe agregar al menos una imagen.')

        existing_count = len(self.property_id.image_ids)
        for idx, line in enumerate(self.image_line_ids):
            self.env['verticali.property.image'].create({
                'property_id': self.property_id.id,
                'image': line.image,
                'name': line.name or f'Imagen {existing_count + idx + 1}',
                'sequence': existing_count + idx + 1,
            })

        _logger.info(
            'Se subieron %d imágenes a la propiedad ID %s',
            len(self.image_line_ids),
            self.property_id.id,
        )

        return {'type': 'ir.actions.act_window_close'}