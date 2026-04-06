from odoo import models, fields, _, api
from datetime import datetime
from odoo.exceptions import UserError
from geopy.geocoders import Nominatim
from odoo.http import request
import logging
import urllib.request
import urllib.parse
import json

import requests
from urllib.parse import quote

_logger = logging.getLogger(__name__)

MAPBOX_TOKEN = 'pk.eyJ1IjoiYWxleHNhbmNoZXoyOCIsImEiOiJjbWQ0eDd5eXkwNzJkMnZwcHRkNHY5aXdhIn0.rkOiyAbWigTbooUZadY28w'
BASE_URL = "https://api.verticali.mx/api/locations"

class VerticaliProperty(models.Model):
    _name = 'verticali.property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Propiedades'
    _rec_name = 'title'
    _order = "write_date desc"

    active = fields.Boolean(string='Activo', default=True)
    title = fields.Char(string='Título del anuncio', tracking=True, required=False)
    type_ope = fields.Selection([
        ('Venta', 'Venta'),
        ('Renta', 'Renta'),
        ('Preventa', 'Preventa'),
    ], string='Tipo de operacion', default=False, tracking=True, required=False)
    land_use_id = fields.Many2one('property.land.use', string='Uso del suelo', tracking=True)
    description = fields.Text(string='Descripción anuncio', tracking=True, required=False)
    price = fields.Float(string='Precio', tracking=True, required=False)
    currency_id = fields.Many2one('res.currency', string='Moneda', tracking=True, required=False)

    availability_id = fields.Many2one('property.availability', string='Disponibilidad', tracking=True, required=False)
    status_id = fields.Many2one('property.status', string='Status', tracking=True, required=False)
    investment_property = fields.Selection([('y','Si'),('n','No')], string='Propiedad de inversión')
    maintenance_cost = fields.Float(string='Costo de mtto', tracking=True)
    maintenance_currency_id = fields.Many2one('res.currency', string='Moneda (mtto)', tracking=True)

    commission_share_id = fields.Many2one('property.commission.share', string='Compartir comisión', tracking=True, required=False)

    bedrooms = fields.Integer(string='Recámaras', tracking=True)
    bathrooms = fields.Integer(string='Baños', tracking=True)
    half_baths = fields.Integer(string='Medios baños', tracking=True)
    parking_lot = fields.Integer(string='Estacionamientos', tracking=True)
    constructions = fields.Float(string='Construcción', tracking=True)
    lans = fields.Float(string='Terreno', tracking=True)
    def _default_lans_uom(self):
        return self.env['uom.uom'].search([('name', '=', 'm²')], limit=1).id
    lans_uom_id = fields.Many2one('uom.uom', string='Uom Terreno', tracking=True, default=_default_lans_uom)
    along_terrain = fields.Float(string='Largo del terreno', tracking=True)
    front_of_terrain = fields.Float(string='Frente del terreno', tracking=True)
    id_eb = fields.Char(string='ID Easy Broker', tracking=True)
    id_marketplace = fields.Char(string='ID Marketplace', tracking=True)

    #page: promotion
    inmuebles24 = fields.Boolean(string='Inmuebles24', default=False, tracking=True)
    icasas = fields.Boolean(string='Icasas', default=False, tracking=True)
    inmoxperts = fields.Boolean(string='Inmoxperts', default=False, tracking=True)
    nuroa = fields.Boolean(string='Nuroa', default=False, tracking=True)
    goplaceit = fields.Boolean(string='Goplaceit', default=False, tracking=True)
    mitula = fields.Boolean(string='Mitula', default=False, tracking=True)
    mercadolibre = fields.Boolean(string='Mercadolibre', default=False, tracking=True)
    nestoria = fields.Boolean(string='Nestoria', default=False, tracking=True)
    lamudi = fields.Boolean(string='Lamudi', default=False, tracking=True)
    propiedades_com = fields.Boolean(string='Propiedades.com', default=False, tracking=True)
    trovit = fields.Boolean(string='Trovit', default=False, tracking=True)
    vivanuncios = fields.Boolean(string='Vivanuncios', default=False, tracking=True)
    clasificados = fields.Boolean(string='Clasificados', default=False, tracking=True)
    verticali = fields.Boolean(string='Verticali', default=False, tracking=True)
    whatsapp = fields.Boolean(string='Whatsapp', default=False, tracking=True)
    short_description = fields.Text(string='Descripción corta')

    #page: location
    development_id = fields.Many2one('property.development', string='Desarrollo', tracking=True)
    related_business_unit_ids = fields.Many2many('property.business.unit', related='property_id.business_unit_ids', string='Unidad de negocio (relacionada)')
    business_unit_ids = fields.Many2many('property.business.unit', string='Unidad de negocio', tracking=True)
    development_type_ids = fields.Many2many('property.development.type', string='Tipo de desarrollo', tracking=True)

    def _default_country_mx(self):
        return self.env['res.country'].search([('code', '=', 'MX')], limit=1).id

    country_id = fields.Many2one('res.country', string='País', tracking=True, default=_default_country_mx)
    state_id = fields.Many2one('res.country.state', string='Estado', tracking=True)
    zona_id = fields.Many2one('res.zona', string='Municipio', tracking=True)
    colony_id = fields.Many2one('res.colony', string='Colonia', tracking=True)
    colony_easybroker_id = fields.Many2one('res.colony.easybroker', string='Colonia (Easybroker)', tracking=True)
    street = fields.Char(string='Calle', required=False)
    street2 = fields.Char(string='#', required=False)
    street3 = fields.Char(string='# Interior')
    #zip = fields.Char(string='Codigo postal')
    zipcode_id = fields.Many2one('res.zipcode', string='Código postal', tracking=True)
    municipality_id = fields.Many2one('res.municipality', string='Municipio', tracking=True)
    latitude = fields.Char(string='Latitud', tracking=True)
    longitude = fields.Char(string='Longitude', tracking=True)

    #page: policies
    pet_id = fields.Many2one('pet', string='Mascotas', copy=True, tracking=True)
    smoking_id = fields.Many2one('property.smoking', string='Permitido fumar', tracking=True)
    payment_method_id = fields.Many2one('property.payment.method', string='Forma de pago', tracking=True)
    invoice_id = fields.Many2one('property.invoice', string='Factura', tracking=True)
    giro_id = fields.Many2one('property.giro', string='Giro no permitido', tracking=True)
    grace_time = fields.Integer(string='Tiempo de gracia', tracking=True)
    payment_condition = fields.Text(string='Condiciones de pago')

    #page: conditions
    warranty_ids = fields.Many2many('aval.warranty',string='Garantía', copy=True, tracking=True)

    deposit_id = fields.Many2one('property.deposit',string='Depositos', copy=True, tracking=True)
    minimum_term_id = fields.Many2one('property.term',string='Plazo mínimo', copy=True, tracking=True)
    customer_profile_id = fields.Many2one('property.customer.profile',string='Perfil no admitido', copy=True, tracking=True)
    type_of_training_id = fields.Many2one('property.type.training',string='Tipo de capacitación', copy=True, tracking=True)
    exclusive_time_id = fields.Many2one('property.exclusive.time',string='Tiempo exclusiva', copy=True, tracking=True)
    commision_type = fields.Many2one('property.commission.type', string='Comisión pactada', required=False)
    commision_type_type = fields.Selection(related='commision_type.type', store=True)
    commision_percentage = fields.Char(string='Porcentaje', default=False)
    commision_currency_id = fields.Many2one('res.currency', string='Moneda')

    commision_fixed = fields.Char(string='Monto', default=False)
    commision_months = fields.Selection([('month_half','Medio mes'),
                                         ('month1','1 Mes'),
                                         ('one_half_month','Mes y medio'),
                                         ('month2','Mes 2'),
                                         ('month3','Mes 3'),
                                         ('month4','Mes 4')], string='Mes')
    comments = fields.Text(string='Comentarios')

    #page: owner
    partner_id = fields.Many2one('res.partner', string='Contacto', copy=True, tracking=True, domain="['|',('is_ct_adviser','=',True),('is_ct_owner','=',True)]", required=False)
    email = fields.Char(string='Correo electrónico', copy=True, tracking=True)
    phone = fields.Char(string='Teléfono', copy=True, tracking=True, required=False, default='+52')
    comments_owner = fields.Text(string='Comentarios')
    contact_type_ids = fields.Many2many('res.contact.type', string="Tipo de contacto", domain="[('type','in',('adviser','owner'))]", required=False)
    is_adviser = fields.Boolean(string='¿Es asesor?', compute='_is_adviser', store=True)
    crm_category_id = fields.Many2one('res.partner.crm.category', string='Categoría de contacto', required=False)

    phone_adviser = fields.Char(string='Teléfono asesor', related='adviser_id.phone', store=True)
    adviser_id = fields.Many2one('res.partner', domain=[('is_ct_adviser','=',True)], string='Vendedor', readonly=True)
    user_id = fields.Many2many('res.users', string='Usuario vendedor')
    property_id = fields.Many2one('res.property', string='Propiedad', tracking=True, required=False)
    
    url = fields.Char(string='URL', tracking=True)
    image = fields.Binary(string='Imagen principal', compute='_get_image', store=True)
    image_ids = fields.One2many('verticali.property.image', 'property_id', string='Imágenes', copy=True)

    contracts_ids = fields.One2many('property.contracts', 'property_id', string='Contratos')
    crm_ids = fields.One2many('crm.lead', 'property', string='Clientes interesados')

    days_of_recruitment = fields.Integer(string='Dias de captación', compute='_get_days_of_recruitment')
    assignment_date = fields.Datetime(string='Fecha de asignación', readonly=True)
    displayid = fields.Char(string='Identificador para mostrar', compute='_get_identifier', store=True)
    private_description = fields.Text(string='Descripción privada')
    available = fields.Date(string='Disponible a partir del', required=False)

    is_owner = fields.Boolean(string='¿Es propietario?', compute='_is_owner', store=False)
    show_adviser = fields.Boolean(string='Mostrar asesor', compute='_show_adviser', store=False)
    is_physical_advertising = fields.Boolean(string='¿Anuncio físico?')
    google_maps_url = fields.Char(string='Google Maps URL', compute='_compute_google_maps_url', store=True)

    # Access control fields
    allowed_user_ids = fields.Many2many('res.users', 'property_allowed_users_rel', 'property_id', 'user_id', string='Usuarios permitidos', help="Usuarios que pueden ver esta propiedad")
    allowed_group_ids = fields.Many2many('res.groups', 'property_allowed_groups_rel', 'property_id', 'group_id', string='Grupos permitidos', help="Grupos que pueden ver esta propiedad")

    def create_locations(self):
        _logger.error('create_locations')
        if not self.zona_id:
            raise UserError('''Debe indicar un municipio aantes de consultar colonias de easybroker.''')

        colony_ids = self.env['res.colony.easybroker'].search([('zona_id','=',self.zona_id.id)])
        state_name = self.zona_id.state_id.name
        city_name = self.zona_id.name

        params = {
            "state": state_name,
            "city": city_name,
        }

        url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
        _logger.error(url)

        try:
            with urllib.request.urlopen(url) as response:
                response_data = response.read().decode("utf-8")
                json_data = json.loads(response_data)
                colonies = json_data.get('data', [])
                _logger.error(colonies)
                colony_names = [x.lower().strip() for x in colony_ids.mapped('name')]

                c, total = 0, len(colonies)
                for col in colonies:
                    c+=1
                    _logger.info("🔄 Procesando colonia: %s (%d/%d - %.2f%%)", col.get('name'), c, total, c / total * 100)
                    if col.get('name', '').lower().strip() not in colony_names:
                        colony = self.env['res.colony.easybroker'].sudo().create({
                            "name": col.get('name'),
                            "location": col.get('id'),
                            "zona_id": self.zona_id.id
                        })
                        colony_names.append(col.get('name', '').lower().strip())
                    else:
                        colony_ids.filtered(lambda x: x.name == col.get('name')).write({"location": col.get('id')})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            _logger.error("❌ HTTPError para zona '%s': %s", city_name, error_body)
        except urllib.error.URLError as e:
            _logger.error("❌ URLError para zona '%s': %s", city_name, e.reason)
        except json.JSONDecodeError as e:
            _logger.error("❌ JSON inválido recibido para zona '%s': %s", city_name, str(e))
        except Exception as e:
            _logger.exception("❌ Error inesperado para zona '%s': %s", city_name, str(e))

    def create_all_locations(self, city_ids):
        _logger.error('create_locations')
        if not city_ids:
            raise UserError('''Debe indicar un municipio aantes de consultar colonias de easybroker.''')

        colony_ids = self.env['res.colony.easybroker'].search([])
        colony_ids = colony_ids.filtered(lambda x: x.zona_id in city_ids)
        for zona_id in city_ids:
            state_name = zona_id.state_id.name
            city_name = zona_id.name

            params = {
                "state": state_name,
                "city": city_name,
            }

            url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
            _logger.error(url)

            try:
                with urllib.request.urlopen(url) as response:
                    response_data = response.read().decode("utf-8")
                    json_data = json.loads(response_data)
                    colonies = json_data.get('data', [])
                    _logger.error(colonies)

                    c, total = 0, len(colonies)
                    for col in colonies:
                        c+=1
                        _logger.info("🔄 Procesando colonia: %s (%d/%d - %.2f%%)", col.get('name'), c, total, c / total * 100)
                        if col.get('name') not in colony_ids.mapped('name'):
                            self.env['res.colony.easybroker'].sudo().create({
                                "name": col.get('name'),
                                "location": col.get('id'),
                                "zona_id": zona_id.id
                            })
                        else:
                            colony_ids.filtered(lambda x: x.name == col.get('name')).write({"location": col.get('id')})
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                _logger.error("❌ HTTPError para zona '%s': %s", city_name, error_body)
            except urllib.error.URLError as e:
                _logger.error("❌ URLError para zona '%s': %s", city_name, e.reason)
            except json.JSONDecodeError as e:
                _logger.error("❌ JSON inválido recibido para zona '%s': %s", city_name, str(e))
            except Exception as e:
                _logger.exception("❌ Error inesperado para zona '%s': %s", city_name, str(e))
    
    # location = fields.Char(string='Ubicacion')
    
    image_count = fields.Integer(
        string="# imágenes",
        compute="_compute_image_count",
        store=False
    )

    def action_view_images(self):
        action = self.env.ref('property_custom.verticali_property_image_action').read()[0]
        action['domain'] = [('property_id', '=', self.id)]
        return action

    @api.depends('image_ids')  # no depende de campos concretos si usamos read_group
    def _compute_image_count(self):
        for r in self:
            r.image_count = len(r.image_ids)
    
    #@api.constrains('title','image_ids','title','type_ope','description','price','currency_id','availability_id','status_id','commission_share_id','partner_id',
    #                  'phone','crm_category_id','property_id','available','commision_type')
    def check_fields(self):
        _logger.info('check_fields called (relaxed)')
        for r in self:
            # Validación de longitud del título
            if r.title and len(r.title) >= 150:
                raise UserError('El título del anuncio debe contener menos de 150 caracteres.')
            
            # Validaciones de comisión (Solo si el tipo está seleccionado)
            if r.commision_type_type == 'fixed' and not r.commision_fixed:
                raise UserError('Debe establecer una comisión fija.')
            if r.commision_type_type == 'percentage' and not r.commision_percentage:
                raise UserError('Debe establecer una % de comisión.')
            if r.commision_type_type == 'months' and not r.commision_months:
                raise UserError('Debe establecer los meses de la comision pactada.')
            
            # Validar UoM solo si hay valor en terreno
            if r.lans and not r.lans_uom_id:
                # Intentar auto-asignar m² si está vacío
                m2_uom = self.env['uom.uom'].search([('name', '=', 'm²')], limit=1)
                if m2_uom:
                    r.lans_uom_id = m2_uom.id
                else:
                    raise UserError('Debe establecer la unidad de medición del terreno, m2 o ha.')

            if r.maintenance_cost and not r.maintenance_currency_id:
                raise UserError('Debe establecer la moneda del costo de mantenimiento.')

            # Lista mínima de campos realmente críticos para guardar un borrador
            msg = ''
            for k in ['title', 'type_ope', 'price', 'currency_id', 'partner_id']:
                if not r[k]:
                    field_label = r.fields_get([k])[k].get('string', k)
                    msg += '\n- {}'.format(field_label)
            
            if msg:
                raise UserError('Para guardar, al menos debes completar los siguientes campos básicos: {}'.format(msg))

    
    def action_open_mapbox_map(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/property/mapbox?model=verticali.property&id={self.id}',
            'target': 'self',
        }

    def save_map_location(self, location_data):
        """
        Called from the JS map widget after reverse geocoding.
        Receives location_data dict with:
          - latitude, longitude
          - state_name, municipality_name, colony_name, postcode
          - street, country_name
        Matches or creates records for state, municipality (zona), colony, zipcode.
        """
        self.ensure_one()
        vals = {
            'latitude': location_data.get('latitude', ''),
            'longitude': location_data.get('longitude', ''),
        }

        # 1. Match Country
        if not self.country_id:
            country_name = location_data.get('country_name', 'México')
            country = self.env['res.country'].search([
                ('name', 'ilike', country_name)
            ], limit=1)
            if not country:
                country = self.env['res.country'].search([('code', '=', 'MX')], limit=1)
            if country:
                vals['country_id'] = country.id
        else:
            country = self.country_id

        # 2. Match State (res.country.state)
        if not self.state_id:
            state_name = location_data.get('state_name', '')
            state = False
            if state_name and country:
                state = self.env['res.country.state'].search([
                    ('name', 'ilike', state_name),
                    ('country_id', '=', country.id),
                ], limit=1)
                if not state:
                    # Try partial match
                    state = self.env['res.country.state'].search([
                        ('name', 'ilike', '%' + state_name.split()[-1] + '%'),
                        ('country_id', '=', country.id),
                    ], limit=1)
                if state:
                    vals['state_id'] = state.id
        else:
            state = self.state_id

        # 3. Match Municipality / Zona (res.zona)
        if not self.zona_id:
            municipality_name = location_data.get('municipality_name', '')
            zona = False
            if municipality_name:
                domain = [('name', 'ilike', municipality_name)]
                if state:
                    domain.append(('state_id', '=', state.id))
                zona = self.env['res.zona'].search(domain, limit=1)
                if not zona and state:
                    # Try without state filter
                    zona = self.env['res.zona'].search([
                        ('name', 'ilike', municipality_name)
                    ], limit=1)
                if zona:
                    vals['zona_id'] = zona.id
        else:
            zona = self.zona_id

        # 4. Match Colony (res.colony)
        if not self.colony_id:
            colony_name = location_data.get('colony_name', '')
            colony = False
            if colony_name:
                domain = [('name', 'ilike', colony_name)]
                if zona:
                    domain.append(('zona_id', '=', zona.id))
                colony = self.env['res.colony'].search(domain, limit=1)
                if colony:
                    vals['colony_id'] = colony.id
                    # Also set zipcode from colony if available
                    if colony.zipcode_id and not self.zipcode_id:
                        vals['zipcode_id'] = colony.zipcode_id.id
        else:
            colony = self.colony_id

        # 5. Match Zipcode (res.zipcode) if not already set
        if not self.zipcode_id and 'zipcode_id' not in vals:
            postcode = location_data.get('postcode', '')
            if postcode:
                zipcode = self.env['res.zipcode'].search([
                    ('name', '=', postcode),
                ], limit=1)
                if zipcode:
                    vals['zipcode_id'] = zipcode.id

        # 6. Set street if provided
        street = location_data.get('street', '')
        if street:
            vals['street'] = street

        _logger.info('Map location data saving: %s', vals)
        self.write(vals)
        return True

    def close_map(self):
        return {'type': 'ir.actions.reload'}
    
    @api.depends('latitude', 'longitude')
    def _compute_google_maps_url(self):
        for rec in self:
            if rec.latitude and rec.longitude:
                rec.google_maps_url = f"https://www.google.com/maps?q={rec.latitude},{rec.longitude}"
            else:
                rec.google_maps_url = ""
                                

    def _is_owner(self):
        for r in self:
            r.is_owner = True if r.adviser_id.id == self.env.user.partner_id.id or self.env.user.has_group('sales_team.group_sale_manager') else False

    def _show_adviser(self):
        for r in self:
            r.show_adviser = True if not r.crm_category_id or r.crm_category_id.show_adviser else False

    @api.depends('image_ids')
    def _get_image(self):
        for r in self:
            r.image = r.image_ids and r.image_ids[0].image or False

    @api.depends('title')
    def _get_identifier(self):
        for r in self:
            r.displayid = 'VE - {}'.format(str(r.id).zfill(4))

    @api.depends('contact_type_ids')
    def _is_adviser(self):
        for r in self:
            r.is_adviser = True if r.contact_type_ids.filtered(lambda x: x.type == 'adviser') else False

    @api.model
    def get_images_for_gallery(self):
        images = []
        for attachment in self.image_ids:
            if attachment.datas:
                images.append(attachment.datas)  # 'datas' contiene la imagen en base64
        return images

    # @api.onchange('commision_type')
    # def onchange_commision_type(self):
    #     for r in self:
    #         r.commision_percentage = False
    #         r.commision_fixed = False
    #         r.commision_type_alt = r.commision_type
    #         if r.commision_type:
    #             r.commision_type_alt = False

    # @api.onchange('commision_type_alt')
    # def onchange_commision_type_alt(self):
    #     for r in self:
    #         r.commision_type = False
    #         r.commision_percentage = False
    #         r.commision_fixed = False

    def _get_days_of_recruitment(self):
        for r in self:
            r.days_of_recruitment = (fields.Date.today() - r.create_date.date()).days

    def action_duplicate(self):
        return self.copy()

    def action_share(self):
        action = self.env.ref('property_custom.action_property_share').read()[0]
        action['context'] = {"default_url": self.url, "default_is_owner": self.is_owner}
        return action
    
    def action_change(self):
        action = self.env.ref('property_custom.action_property_change').read()[0]
        action['context'] = self.env.context
        return action
    
    def action_inactive(self):
        self.active = False

    def action_personal_edit(self):
        return self.action_edit()
    
    def action_go_back(self):
        res_id = self.id
        current_page = request.session['current_page']
        return {
            'type': 'ir.actions.act_url',
            'url': f'/property/view/detail/{res_id}/{current_page}', #f'/web#&action={action_id}&cids=1&menu_id={menu_id}',
            'target': 'self',
        }
        
    def action_go_back_to_list(self):
        action = self.env.ref('property_custom.action_property').sudo().read()[0].copy()
        ctx = eval(action['context'])
        ctx.update({"keep_session": True})
        action['context'] = ctx
        return action
    
    def action_edit(self):
        res_id = self.id
        action_id = self.env.ref('property_custom.verticali_property_action').id
        menu_id = self.env.ref('property_custom.menu_verticali_property_act').id
        url = f'/web#id={res_id}&action={action_id}&model=verticali.property&view_type=form&cids=1&menu_id={menu_id}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    @api.onchange('colony_id')
    def onchange_colony(self):
        for r in self:
            r.zipcode_id = r.colony_id.zipcode_id
            r.zona_id = r.colony_id.zona_id
            r.state_id = r.zona_id.state_id
            r.country_id = r.state_id.country_id
            
    @api.onchange('development_id')
    def onchange_development(self):
        _logger.error('onchange_development')
        for r in self:
            r.business_unit_ids = r.development_id.business_unit_ids
            r.development_type_ids = r.development_id.development_type_ids
            # r.country_id = r.development_id.country_id
            # r.state_id = r.development_id.state_id
            r.zona_id = r.development_id.zona_id
            r.colony_id = r.development_id.colony_id
            r.street = r.development_id.street
            r.street2 = r.development_id.street2
            r.street3 = r.development_id.street3
            # r.zip = r.development_id.zip

            fields = self.env['property.fields'].search([])

            for f in fields.filtered(lambda x: x.group_id in ('development_characteristics_services','development_characteristics_attributes','development_characteristics_amenidades')):
                field = 'x_{}'.format(f.name)
                if field in self._fields and field in self.env['property.development']._fields:
                    r[field] = r.development_id[field]
                else:
                    _logger.warning('Campo dinámico %s no encontrado en el modelo, omitiendo.', field)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """Extend search to also show properties where the user is in allowed_user_ids or allowed_group_ids."""
        if not self.env.is_superuser() and not self.env.user.has_group('sales_team.group_sale_manager'):
            # Add OR conditions for allowed_user_ids and allowed_group_ids
            extra_domain = [
                '|', '|',
                ('create_uid', '=', self.env.uid),
                ('allowed_user_ids', 'in', [self.env.uid]),
                ('allowed_group_ids.users', 'in', [self.env.uid]),
            ]
            domain = extra_domain + list(domain)
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['adviser_id'] = self.env.user.partner_id.id
        records = super(VerticaliProperty, self).create(vals_list)
        for rec in records:
            _logger.info('Ejecutando check_fields en create para registro ID: %s', rec.id)
            rec.check_fields()
        return records

    def write(self, vals):
        # if 'status_id' not in vals.keys():
        #     vals['status_id'] = False
        res = super(VerticaliProperty, self).write(vals)
        _logger.info('Ejecutando check_fields en write para registros: %s', [r.id for r in self])
        self.check_fields()
        for r in self:
            if 'adviser_id' in vals.keys():
                r.assignment_date = datetime.now()
            r.partner_id.sudo().write({"crm_category_id": r.crm_category_id.id,
                                "phone": r.phone,
                                "email": r.email,
                                "contact_type_ids": [(4,x) for x in r.contact_type_ids.ids]})
            if 'image_ids' in vals and len(r.image_ids) < 3: # Reducido a 3 para facilitar borrador inicial
                _logger.warning('Propiedad ID %s tiene pocas imágenes (%s)', r.id, len(r.image_ids))
                # raise UserError('Debe agregar al menos 5 imágenes de la propiedad.')

        return res
    
    @api.onchange('partner_id')
    def onchange_partner(self):
        for r in self:
            r.email = r.partner_id.sudo().email
            r.phone = r.partner_id.sudo().phone
            r.contact_type_ids = r.partner_id.contact_type_ids
            r.crm_category_id = r.partner_id.crm_category_id

    @api.model
    def get_action_url(self):
        action_id = self.env.ref('property_custom.verticali_property_action')
        action_url = "/web#id=&action={action_id}&model={model}&view_type=form".format(action_id=action_id.id, model=self._name)
        return {"url": action_url}

    def check_user_can_edit(self):
        """
        Verifica si el usuario actual puede editar esta propiedad.
        Retorna True si:
        - El usuario pertenece al grupo sales_team.group_sale_manager
        - El usuario (su partner_id) es el adviser_id de la propiedad
        """
        # Verificar si el usuario es Sales Manager
        if self.env.user.has_group('sales_team.group_sale_manager'):
            return True
        
        # Obtener el partner_id del usuario actual
        current_user_partner = self.env.user.partner_id
        
        if not current_user_partner:
            return False
        
        # Verificar si el usuario es el asesor de esta propiedad
        if self.adviser_id and self.adviser_id.id == current_user_partner.id:
            return True
        
        return False

    @api.model
    def get_data_land_use(self):
        record_ids = self.env['property.land.use'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}
    
    @api.model
    def get_data_commission_share(self):
        record_ids = self.env['property.commission.share'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}

    @api.model
    def get_data_development_services(self):
        fields_ids = self.env['property.fields'].search([('field_id','!=',False),('group_id','=','development_characteristics_services')])
        return {'fields': [{"name": x.name, "description": x.field_description} for x in fields_ids]}
    
    @api.model
    def get_data_development_atributos(self):
        fields_ids = self.env['property.fields'].search([('field_id','!=',False),('group_id','=','development_characteristics_attributes')])
        return {'fields': [{"name": x.name, "description": x.field_description} for x in fields_ids]}
    
    @api.model
    def get_data_development_amenidades(self):
        fields_ids = self.env['property.fields'].search([('field_id','!=',False),('group_id','=','development_characteristics_amenidades')])
        return {'fields': [{"name": x.name, "description": x.field_description} for x in fields_ids]}
    
    @api.model
    def get_data_property_services(self):
        fields_ids = self.env['property.fields'].search([('field_id','!=',False),('group_id','=','property_characteristics_services')])
        return {'fields': [{"name": x.name, "description": x.field_description} for x in fields_ids]}
    
    @api.model
    def get_data_property_tipo_entrega(self):
        fields_ids = self.env['property.fields'].search([('field_id','!=',False),('group_id','=','property_characteristics_delivery_time')])
        return {'fields': [{"name": x.name, "description": x.field_description} for x in fields_ids]}
    
    @api.model
    def get_data_property_atributos(self):
        fields_ids = self.env['property.fields'].search([('field_id','!=',False),('group_id','=','property_characteristics_attributes')])
        return {'fields': [{"name": x.name, "description": x.field_description} for x in fields_ids]}
    
    @api.model
    def get_data_pets(self):
        record_ids = self.env['pet'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}
    
    @api.model
    def get_data_payment_methods(self):
        record_ids = self.env['property.payment.method'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}
    
    @api.model
    def get_data_invoices(self):
        record_ids = self.env['property.invoice'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}
    
    @api.model
    def get_data_warranty(self):
        record_ids = self.env['aval.warranty'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}
    
    @api.model
    def get_data_deposits(self):
        record_ids = self.env['property.deposit'].search([])
        return {'fields': [{"id": x.id, "name": x.name} for x in record_ids]}
    
    @api.model
    def get_data_images(self, params):
        property_id = self.browse(params['id'])
        
        images = []
        for img in property_id.image_ids:
            url = f'/web/content/{img._name}/{img.id}/image/image?download=true'
            images.append(url)

        return {'images': images}

    @api.model
    def get_data(self, params):
        _logger.error('=> get_data')
        _logger.error(params)
        _logger.error(self.env.context)
        domain = []
        if params:
            for f in [('state_id','states'),
                      ('state_id','statess'),
                      ('status_id','status'),
                      ('availability_id','availability'),
                      ('property_id','property_types'),
                      ('type_ope','operation_type'),
                      ('pet_id','pets_checks'),
                      ('payment_method_id','payment_methods_checks'),
                      ('invoice_id','invoices_checks'),
                      ('warranty_ids','warranty_checks'),
                      ('deposit_id','deposits_checks')]:
                vals = params.get(f[1], [])
                _logger.error('vals: ')
                _logger.error(vals)
                if vals:
                    if f[0] == 'type_ope':
                        domain.append((f[0],'=',vals))
                    elif f[0] == 'state_id':
                        svals, zvals, cvals, dvals = [], [], [], []
                        for v in vals:
                            if 's' in v: #states
                                svals.append(int(v.replace('s','')))
                            elif 'z' in v: #zones
                                zvals.append(int(v.replace('z','')))
                            elif 'c' in v: #colony
                                cvals.append(int(v.replace('c','')))
                            elif 'd' in v: #development
                                dvals.append(int(v.replace('d','')))
                        if svals:
                            domain.append(('state_id','in',svals))
                        if zvals:
                            domain.append(('zona_id','in',zvals))
                        if cvals:
                            domain.append(('colony_id','in',cvals))
                        if dvals:
                            domain.append(('development_id','in',dvals))
                    else:
                        domain.append((f[0],'in',[int(x) for x in vals]))

            if params.get('min_price', False):
                domain.append(('price', '>=', float(params['min_price'])))
            if params.get('max_price', False):
                domain.append(('price', '<=', float(params['max_price'])))
            if params.get('currency_id', False) and (params.get('min_price', False) or params.get('max_price', False)):
                domain.append(('currency_id', '=', int(params['currency_id'])))                

            if params.get('name', False):
                domain.append('|')
                domain.append(('title', 'ilike', params['name']))
                domain.append('|')
                domain.append(('id', 'ilike', params['name']))
                domain.append('|')
                domain.append(('id_eb', 'ilike', params['name']))
                domain.append(('id_marketplace', 'ilike', params['name']))

                # domain.append('|',('title', 'ilike', params['name']),'|',('id', 'ilike', params['name']),'|',('id_eb', 'ilike', params['name']),('id_marketplace', 'ilike', params['name']))
                # domain.append('|',('title', 'ilike', params['name']),'|',('id', 'ilike', params['name']),'|',('id_eb', 'ilike', params['name']),('id_marketplace', 'ilike', params['name']))
                # domain.append('|',('title', 'ilike', params['name']),'|',('id', 'ilike', params['name']),'|',('id_eb', 'ilike', params['name']),('id_marketplace', 'ilike', params['name'])))

            if params.get('construction_from', False):
                domain.append(('constructions', '>=', float(params['construction_from'])))
            if params.get('construction_to', False):
                domain.append(('constructions', '<=', float(params['construction_to'])))
            if params.get('land_from', False):
                domain.append(('lans', '>=', float(params['land_from'])))
            if params.get('land_to', False):
                domain.append(('lans', '<=', float(params['land_to'])))

            for f in [('bedrooms', 'beds'),('bathrooms','baths'),('parking_lot','parks')]:
                if params.get(f[1], False):
                    val = int(params[f[1]])
                    if val == 5:
                        domain.append((f[0], '>=', val))
                    else:
                        domain.append((f[0], '=', val))

            land_use_checks = params.get('land_use_checks', [])
            if land_use_checks:
                domain.append(('land_use_id','in',[int(x) for x in land_use_checks]))
            
            investment_property_checks = params.get('investment_property_checks', [])
            if investment_property_checks:
                domain.append(('investment_property','in',[x for x in investment_property_checks]))

            commission_share_checks = params.get('commission_share_checks', [])
            if commission_share_checks:
                domain.append(('commission_share_id','in',[int(x) for x in commission_share_checks]))

            #caracteristicas desarrollo
            development_services_checks = params.get('development_services_checks', [])
            if development_services_checks:
                for f in development_services_checks:
                    domain.append((f'x_{f}','=',True))
            development_atributos_checks = params.get('development_atributos_checks', [])
            if development_atributos_checks:
                for f in development_atributos_checks:
                    domain.append((f'x_{f}','=',True))
            development_amenidades_checks = params.get('development_amenidades_checks', [])
            if development_amenidades_checks:
                for f in development_amenidades_checks:
                    domain.append((f'x_{f}','=',True))

            #caracteristicas propiedad
            property_services_checks = params.get('property_services_checks', [])
            if property_services_checks:
                for f in property_services_checks:
                    domain.append((f'x_{f}','=',True))
            property_tipo_entrega_checks = params.get('property_tipo_entrega_checks', [])
            if property_tipo_entrega_checks:
                for f in property_tipo_entrega_checks:
                    domain.append((f'x_{f}','=',True))
            property_amenidades_checks = params.get('property_amenidades_checks', [])
            if property_amenidades_checks:
                for f in property_amenidades_checks:
                    domain.append((f'x_{f}','=',True))
                
            if params.get('property', False):
                if int(params['property']) == 1: # mis propiedades
                    if not self.env.user.has_group('sales_team.group_sale_manager'):
                        domain.append(('adviser_id','=',self.env.user.partner_id.id))
                elif int(params['property']) == 2: # propiedades verticali
                    domain.append(('adviser_id.parent_id','=',self.env.user.company_id.partner_id.id))
                else:
                    domain.append(('adviser_id','!=',self.env.user.id))
                
        _logger.error('domain')
        _logger.error(domain)
        limit = 18
        if params.get('keep_session', False):
            current_page = request.session['current_page']
        else:
            current_page = int(params.get('current_page',0))
            if not current_page:
                current_page = 1

        offset = (current_page - 1) * limit
        if offset < 0:
            offset = 0

        order = ''
        if params.get('order_by', False):
            order = {'creation_recent': 'create_date desc',
                       'creation_ancient': 'create_date asc',
                       'update_recent': 'write_date desc',
                       'update_ancient': 'write_date asc',
                       'greater_price': 'price desc',
                       'lower_price': 'price asc',
                       'down_price': 'price asc',
                       }.get(params['order_by'])
        records = self.sudo().search(domain,offset=offset,limit=limit,order=order)
        _logger.error('records')
        _logger.error(records)
        pages = self.sudo().search_count(domain) // limit + 1
        result = []
        action_id = self.env.ref('property_custom.verticali_property_action')
        
        image = ''
        for x in records:
            img = x.image_ids and x.image_ids[0]
            image = f'/web/content/{img._name}/{img.id}/image/image?download=true'
                    
            result.append({"id": x.id, 
                            "id_eb": 'VE - {}'.format(str(x.id).zfill(4)),
                            "price": "{:,.2f}".format(x.price or 0),
                            "symbol": x.currency_id.symbol or self.env.user.company_id.currency_id.symbol,
                            "type_ope": x.type_ope or '',
                            "description": x.description and x.description[:100] or '',
                            "bedrooms": x.bedrooms or 0,
                            "bathrooms": x.bathrooms or 0,
                            "parking_lot": x.parking_lot or 0,
                            "constructions": x.constructions or 0,
                            "lans": x.lans or 0,
                            "lans_uom_id": x.lans_uom_id.name or '',
                            "title": x.title or '',
                            "action_id": action_id.id,
                            "status": x.status_id.name or '',
                            "availability": x.availability_id.name or '',
                            "adviser": x.show_adviser and x.adviser_id.name or x.partner_id.name or x.adviser_id.name or '',
                            "image": image,
                            "current_page": current_page})
            
        pagination = ''
        if pages > 1:
            pags = ''
            pagmin = current_page - 5
            pagmax = current_page + 5
            if pagmax > pages:
                pagmax = pages
                pagmin = pages - 4
                
            if pagmin <= 0:
                pagmin = 1

            c = 0
            _logger.error('== x')
            for x in range(pagmin, pagmax+1):
                c+=1
                _logger.error('c: {}'.format(c))
                if c >5:
                    continue
                _logger.error('x: {}'.format(x))
                
                active = 'active' if x == current_page else ''
                pags += '<li class="page-item {active}"><button type="button" class="btn page-link apply" data-page="{page}" data-property="{property}">{page}</button></li>'.format(page=x, active=active, property=params.get('property',  0))

            prev_disable = 'disabled' if current_page == 1 else ''
            next_disable = 'disabled' if current_page == pages else ''

            pagination = '''<ul class="pagination justify-content-center">
                                <li class="page-item {prev_disable}">
                                    <button type="button" class="btn page-link apply" data-page="{previous}" data-property="{property}">
                                        <span aria-hidden="true">&laquo;</span>
                                        <span class="sr-only">Previous</span>
                                    </button>
                                </li>
                                {pags}    
                                <li class="page-item {next_disable}">
                                    <button type="button" class="btn page-link apply" data-page="{next}" data-property="{property}">
                                        <span aria-hidden="true">&raquo;</span>
                                        <span class="sr-only">Previous</span>
                                    </button>
                                </li>
                        </ul>'''.format(pags=pags, previous=current_page-1, next=current_page+1,prev_disable=prev_disable,next_disable=next_disable, property=params.get('property',  0))
        #'current_page': current_page, 'pages': int(len(records) / step)
        menu_action = 0
        if params.get('property', False):
            menu_action = params['property']
        res = {'records': result, 'pagination': pagination, 'menu_action': menu_action}
        return res


    def view_all(self):
        action = self.env.ref('property_custom.action_property_image_preview').read()[0]
        action['context'] = {"default_property_id": self.id}
        return action
    
    def _cron_action_send(self):
        property_ids = self.env['verticali.property'].search([('status_id','=',False)])
        property_ids.action_send()
    
    def action_send(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        apiurl = self.env['ir.config_parameter'].sudo().get_param('web.api.url')
        token = self.env['ir.config_parameter'].sudo().get_param('web.api.token')
        for r in self.filtered(lambda x: x.title):
            # no enviar propiedades si no estan marcados
            if (r.inmuebles24 or r.icasas or r.inmoxperts or r.nuroa or r.goplaceit or r.mitula or r.mercadolibre or r.nestoria or r.lamudi or r.propiedades_com or r.trovit or r.vivanuncios or r.clasificados or r.verticali):
                continue
            
            if not r.colony_easybroker_id.location:
                raise UserError("Debe seleccionar una ubicación para la propiedad: {}".format(r.title))
            
            postname = r.title.split(' ')
            postname = '-'.join(postname).lower()
            
            # images
            images = []
            for image in r.image_ids:
                url = f"{base_url}/web/image/{image._name}/{image.id}/image"
                images.append(url)
                
            features = []
            fields = self.env['property.fields'].search([('field_id','!=',False)])
            for f in fields:
                if r[f.field_id.name]:
                    features.append(f.field_id.field_description)
            data = {
                "property_type": r.property_id.name or '',
                "title": r.title or '',
                "description": r.description or '',
                "status": r.status_id.name or '',
                "private_description": r.private_description or '',
                "operations_type": dict(self._fields['type_ope'].selection).get(r.type_ope) or '',
                "active": True,
                "amount": r.price or '0',
                "currency": r.currency_id.name or '',
                "agent": r.adviser_id.email or '',
                "show_prices": True,
                "bedrooms": r.bedrooms or "0",
                "bathrooms": r.bathrooms or "0",
                "half_bathrooms": r.half_baths or "0",
                "parking_spaces": r.parking_lot or "0",
                #"age": None,
                "floor": 0,
                "floors": 0,
                "expenses": 0,
                "internal_id": r.id_eb or '',
                "exterior_number": 0,
                "street": r.street or '',
                "interior_number": 0,
                "cross_street": 0,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "show_exact_location": False,
                "hide_exact_location": True,
                "features": features,
                "share_comission": r.commission_share_id and r.commission_share_id.name.lower() == 'si' and True or False,
                "comission_amount": r.commision_fixed or 0.0,
                "collaboration_notes": '',
                "images": images,
                "construction_size": r.constructions or "0.00",
                "coverage_space": "0.00",
                "postal_code": r.zipcode_id.name or "",
                "location_id": r.colony_easybroker_id.location,
                "erp_id": r.id,
                "marketplace": r.verticali and "1" or False,
                "easybroker": (r.inmuebles24 or r.icasas or r.inmoxperts or r.nuroa or r.goplaceit or r.mitula or r.mercadolibre or r.nestoria or r.lamudi or r.propiedades_com or r.trovit or r.vivanuncios or r.clasificados) and "1" or False,
            }
        
            headers = {
                'Content-Type': 'application/json',
                'X-Verticali-Token': token
            }

            json_data = json.dumps(data).encode("utf-8")
            _logger.info(json_data)
            req = urllib.request.Request(apiurl, data=json_data, headers=headers, method='POST')

            try:
                with urllib.request.urlopen(req) as response:
                    response_data = response.read().decode("utf-8")
                    _logger.info("Respuesta del servidor: %s", response_data)
            except urllib.error.HTTPError as e:
                response_data = e.read().decode('utf-8')
                raise UserError("Error en la petición de propiedades: %s" %(response_data))
            except urllib.error.URLError as e:
                raise UserError("Error de conexión: %s"% e.reason)


    def upload_images(self):
        action = self.env.ref('property_custom.action_property_update_fields').read()[0]
        action['context'] = {"default_property_id": self.id}
        return action

class ProjectTaskImage(models.Model):
    _name = 'verticali.property.image'
    _description = 'Imagenes'
    _order = 'sequence'

    sequence = fields.Integer(string="Secuencia")
    name = fields.Char(string="Description")
    image = fields.Binary(string="Image", attachment=True)
    property_id = fields.Many2one('verticali.property', string='Propiedad')
