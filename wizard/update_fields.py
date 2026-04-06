# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PropertyUpdateFields(models.TransientModel):
    _name = 'property.update.fields'
    _description = 'Actualizar campos propiedades'

    def apply(self):

        # actualizar verticali.property
        view_name = 'verticali.property.custom.fields'
        view_id = self.env['ir.ui.view'].search([('name','=',view_name)])

        view_id.unlink()

        view_detailed_name = 'verticali.property.custom.fields'
        view_detailed_id = self.env['ir.ui.view'].search([('name','=',view_name)])

        view_detailed_id.unlink()

        view_dev_name = 'verticali.property.development.custom.fields'
        view_dev_id = self.env['ir.ui.view'].search([('name','=',view_dev_name)])

        view_dev_id.unlink()

        view_report = 'property.verticali.reports.without.user'
        view_report_id = self.env['ir.ui.view'].search([('name','=',view_report)])
        view_report_id.unlink()

        view_report = 'property.verticali.reports.with.user'
        view_report_id = self.env['ir.ui.view'].search([('name','=',view_report)])
        view_report_id.unlink()

        all_fields = self.env['property.fields'].search([])
        # elimpiar campos
        # to_delete = all_fields.mapped('field_id')
        # to_delete |= all_fields.mapped('dev_field_id')
        # to_delete.unlink()

        model_id = self.env.ref('property_custom.model_verticali_property')
        # crear campos faltantes en el modelo
        for field in all_fields.filtered(lambda x: not x.field_id):
            data = {"name": f"x_{field.name}",
                    "field_description": field.field_description,
                    "help": field.help,
                    "ttype": "boolean",
                    "store": True,
                    "model_id": model_id.id,
                    "required": False,
                    "copied": False}
            field_id = self.env['ir.model.fields'].create(data)
            _logger.error(field_id)
            field.write({"field_id": field_id.id})

        # update views
        property_characteristics_services = ''
        for f in all_fields.filtered(lambda x: x.group_id == 'property_characteristics_services'):
            property_characteristics_services += f"<field name='x_{f.name}'/>"

        property_characteristics_delivery_time = ''
        for f in all_fields.filtered(lambda x: x.group_id == 'property_characteristics_delivery_time'):
            property_characteristics_delivery_time += f"<field name='x_{f.name}'/>"

        property_characteristics_attributes = ''
        for f in all_fields.filtered(lambda x: x.group_id == 'property_characteristics_attributes'):
            property_characteristics_attributes += f"<field name='x_{f.name}'/>"

        development_characteristics_services = ''
        for f in all_fields.filtered(lambda x: x.group_id == 'development_characteristics_services'):
            development_characteristics_services += f"<field name='x_{f.name}'/>"

        development_characteristics_attributes = ''
        for f in all_fields.filtered(lambda x: x.group_id == 'development_characteristics_attributes'):
            development_characteristics_attributes += f"<field name='x_{f.name}'/>"

        development_characteristics_amenidades = ''
        for f in all_fields.filtered(lambda x: x.group_id == 'development_characteristics_amenidades'):
            development_characteristics_amenidades += f"<field name='x_{f.name}'/>"

        arch_base = f'''<?xml version="1.0"?>
                        <data>
                            <xpath expr="//group[@name='property_characteristics_services']" position="replace">
                                <group string="Servicios" name="property_characteristics_services">
                                    <group col="4">
                                        {property_characteristics_services}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='property_characteristics_delivery_time']" position="replace">
                                <group string="Tipo de entrega" name="property_characteristics_delivery_time">
                                    <group col="4">
                                        {property_characteristics_delivery_time}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='property_characteristics_attributes']" position="replace">
                                <group string="Atributos" name="property_characteristics_attributes">
                                    <group col="4">
                                    {property_characteristics_attributes}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='development_characteristics_services']" position="replace">
                                <group string="Servicios" name="development_characteristics_services">
                                    <group col="4">
                                        {development_characteristics_services}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='development_characteristics_attributes']" position="replace">
                                <group string="Atributos" name="development_characteristics_attributes">
                                    <group col="4">
                                        {development_characteristics_attributes}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='development_characteristics_amenidades']" position="replace">
                                <group string="Amenidades" name="development_characteristics_amenidades">
                                    <group col="4">
                                    {development_characteristics_amenidades}
                                    </group>
                                </group>
                            </xpath>
                        </data>'''
        self.env['ir.ui.view'].create({"name": view_name,
                                        "type": "form",
                                        "model": "verticali.property",
                                        "inherit_id": self.env.ref('property_custom.view_verticali_property_form').id,
                                        "arch_base": arch_base})
        
        self.env['ir.ui.view'].create({"name": view_detailed_name,
                                        "type": "form",
                                        "model": "verticali.property",
                                        "inherit_id": self.env.ref('property_custom.view_verticali_property_owner_detail_form').id,
                                        "arch_base": arch_base})
        
        self.env['ir.ui.view'].create({"name": view_detailed_name,
                                        "type": "form",
                                        "model": "verticali.property",
                                        "inherit_id": self.env.ref('property_custom.view_verticali_property_detail_form').id,
                                        "arch_base": arch_base})
        
        model_id = self.env.ref('property_custom.model_property_development')
        # update models
        for field in all_fields.filtered(lambda x: not x.dev_field_id):

            data = {"name": f"x_{field.name}",
                    "field_description": field.field_description,
                    "help": field.help,
                    "ttype": "boolean",
                    "store": True,
                    "model_id": model_id.id,
                    "required": False,
                    "copied": False}
            field_id = self.env['ir.model.fields'].create(data)
            _logger.error(field_id)
            field.write({"dev_field_id": field_id.id})

        

        arch_base = f'''<?xml version="1.0"?>
                        <data>
                            <xpath expr="//group[@name='development_characteristics_services']" position="replace">
                                <group string="Servicios" name="development_characteristics_services">
                                    <group col="4">
                                        {development_characteristics_services}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='development_characteristics_attributes']" position="replace">
                                <group string="Atributos" name="development_characteristics_attributes">
                                    <group col="4">
                                        {development_characteristics_attributes}
                                    </group>
                                </group>
                            </xpath>
                            <xpath expr="//group[@name='development_characteristics_amenidades']" position="replace">
                                <group string="Amenidades" name="development_characteristics_amenidades">
                                    <group col="4">
                                    {development_characteristics_amenidades}
                                    </group>
                                </group>
                            </xpath>
                        </data>'''
        self.env['ir.ui.view'].create({"name": view_dev_name,
                                        "type": "form",
                                        "model": "property.development",
                                        "inherit_id": self.env.ref('property_custom.property_development_view_form').id,
                                        "arch_base": arch_base})
        
        # reports
        development_characteristics_amenidades = '<ul>'
        for f in all_fields.filtered(lambda x: x.group_id == 'development_characteristics_amenidades'):
            development_characteristics_amenidades += f"<t t-if='o.x_{f.name}'><li>{f.field_description}</li></t>"
        development_characteristics_amenidades += '</ul>'

        arch_base = f'''<?xml version="1.0"?>
                        <data>
                            <xpath expr="//div[@name='development_characteristics_amenidades']" position="replace">
                                <div name="development_characteristics_amenidades">
                                    {development_characteristics_amenidades}
                                </div>
                            </xpath>
                        </data>'''
        _logger.error(arch_base)
        
        self.env['ir.ui.view'].create({"name": 'property.verticali.reports.without.user',
                                        "type": "qweb",
                                        "inherit_id": self.env.ref('property_custom.property_report_without_user').id,
                                        "arch_base": arch_base})
        self.env['ir.ui.view'].create({"name": 'property.verticali.reports.with.user',
                                        "type": "qweb",
                                        "inherit_id": self.env.ref('property_custom.property_report_with_user').id,
                                        "arch_base": arch_base})