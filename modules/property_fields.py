from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

GROUPS = [('property_characteristics_services','Servicios (Características de la propiedad)'),
          ('property_characteristics_delivery_time','Tipo de entrega (Características de la propiedad)'),
          ('property_characteristics_attributes','Atributos (Características de la propiedad)'),
          ('development_characteristics_services','Servicios (Características del desarrollo)'),
          ('development_characteristics_attributes','Atributos (Características del desarrollo)'),
          ('development_characteristics_amenidades','Amenidades (Características del desarrollo)')]

class PropertyFields(models.Model):
    _name = 'property.fields'
    _description = 'Campos propiedades'
    
    name = fields.Char(string='Nombre', required=True)
    field_description = fields.Char(string='Etiqueta', required=True)
    help = fields.Char(string='Ayuda')
    # type = fields.Selection([('boolean','Boolean')], string='Tipo', default='boolean', required=True)
    field_id = fields.Many2one('ir.model.fields', string='Campo', readonly=True, ondelete="set null")
    dev_field_id = fields.Many2one('ir.model.fields', string='Campo (desarrollo)', readonly=True, ondelete="set null")
    group_id = fields.Selection(GROUPS, string='Sección de la vista', required=True)
    active = fields.Boolean(string='Activo', default=True)

    def _create_ir_model_field(self, model_xmlid, field_name, field_description, help_text):
        """Crea un campo boolean en ir.model.fields para el modelo indicado."""
        try:
            model_id = self.env.ref(model_xmlid)
        except ValueError:
            _logger.warning('No se encontró el modelo %s, omitiendo creación de campo.', model_xmlid)
            return False

        # Verificar si el campo ya existe en el modelo
        existing = self.env['ir.model.fields'].search([
            ('model_id', '=', model_id.id),
            ('name', '=', f'x_{field_name}'),
        ], limit=1)
        if existing:
            return existing

        data = {
            "name": f"x_{field_name}",
            "field_description": field_description,
            "help": help_text or False,
            "ttype": "boolean",
            "store": True,
            "model_id": model_id.id,
            "required": False,
            "copied": False,
        }
        ir_field = self.env['ir.model.fields'].create(data)
        _logger.info('Campo ir.model.fields creado: %s en modelo %s', ir_field.name, model_xmlid)
        return ir_field

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        try:
            # Llama al wizard de actualización automáticamente tras crear para que regenere
            # los ir.model.fields y todas las vistas XML (las pestañas).
            self.env['property.update.fields'].create({}).apply()
        except Exception as e:
            _logger.exception("Error actualizando campos automáticamente: %s", str(e))
        return records

    def write(self, vals):
        res = super().write(vals)
        # Si se modifica el nombre, descripción, sección o activo, regeneramos las vistas
        if any(k in vals for k in ['name', 'field_description', 'group_id', 'active']):
            try:
                self.env['property.update.fields'].create({}).apply()
            except Exception as e:
                _logger.exception("Error actualizando vistas tras modificación: %s", str(e))
        return res

    def unlink(self):
        # Al eliminar un campo de la base de datos, asegurarse de que se actualicen las vistas para que desaparezca
        res = super().unlink()
        try:
            self.env['property.update.fields'].create({}).apply()
        except Exception as e:
            _logger.exception("Error actualizando vistas tras eliminación: %s", str(e))
        return res