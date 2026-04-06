import json
from odoo import http
from odoo.http import request, Response
from werkzeug.utils import redirect

import logging 

_logger = logging.getLogger(__name__)

class Property(http.Controller):

    def _validate_token(self, token):
        if not token:
            return None, "Token faltante", 401

        token_record = request.env['ir.config_parameter'].sudo().search([
            ('key', '=', 'web.api.token'),
            ('value', '=', token)
        ], limit=1)

        if not token_record:
            return "Token inválido", 401
        return False, False

    @http.route('/api/v1/property', type='json', auth='none', csrf=False, methods=['POST'])
    def secure_data(self, **kwargs):

        try:
            payload = json.loads(request.httprequest.data)
        except Exception:
            return Response(
                response=json.dumps({'error': 'JSON inválido'}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )

        token = request.httprequest.headers.get('Authorization')
        _logger.error(payload)

        error_msg, error_code = self._validate_token(token)
        if error_msg:
            return Response(
                response=http.json.dumps({'error': error_msg}),
                status=error_code,
                headers={'Content-Type': 'application/json'}
            )

        if payload.get('id_erp', False):
            property = request.env['verticali.property'].sudo().search([('id', '=', payload['id_erp'])])
            if property:
                data = {}
                if payload.get('id_eb', False):
                    data.update({"id_eb": payload['id_eb']})
                if payload.get('url', False):
                    data.update({"url": payload['url']})
                if payload.get('id_eb', False):
                    data.update({"id_marketplace": payload['id_marketplace']})
                if data.keys():
                    property.sudo().write(data)
                return Response(
                    response=http.json.dumps({'data': data}),
                    status=200,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                return None, "Propiedad no encontrada", 404
        else:
            return None, "Parametros incorrectos", 404

    @http.route('/property/create', auth='public', methods=['POST'], type='json', csrf=False)
    def actualizar_contacto(self, **kwargs):
        data = request.jsonrequest
        _logger.error(data)
        # contacto_id = data.get('contacto_id')
        # nombre = data.get('nombre')
        # email = data.get('email')

        # if not contacto_id:
        #     return {'error': 'ID de contacto no proporcionado'}

        # # Buscar el contacto por ID
        # contacto = request.env['res.partner'].sudo().search([('id', '=', contacto_id)], limit=1)
        # if not contacto:
        #     return {'error': 'Contacto no encontrado'}

        # # Actualizar los datos del contacto
        # contacto.sudo().write({
        #     'name': nombre,
        #     'email': email,
        # })

        return {'status': 'success', 'message': 'Propiedad creada correctamente'}

    @http.route('/property/view/detail/<int:res_id>/<int:current_page>', auth='public', methods=['GET'], type='http', csrf=False)
    def view_detail(self, res_id, current_page, **kwargs):
        _logger.error('=> view_detail')
        _logger.error(kwargs)
        action_id = request.env.ref('property_custom.verticali_property_detail_action').id
        property_id = request.env['verticali.property'].browse(int(res_id))
        if property_id and property_id.adviser_id == request.env.user.partner_id or request.env.user.has_group('sales_team.group_sale_manager'):
            action_id = request.env.ref('property_custom.verticali_property_owner_detail_action').id
        menu_id = request.env.ref('property_custom.menu_verticali_property_act').id
        # url = f"/web#action={action_id}&cids=1&id={res_id}&menu_id={menu_id}&model=verticali.property&view_type=form"

        url = f"/odoo/action-{action_id}/{res_id}"
        _logger.error(current_page)
        request.session['current_page'] = current_page
        return redirect(url)
    
    @http.route('/property/view/create', auth='public', methods=['GET'], type='http', csrf=False)
    def view_create(self, **kwargs):
        action_id = request.env.ref('property_custom.verticali_property_action').id
        menu_id = request.env.ref('property_custom.menu_verticali_property_act').id
        url = f"/web#action={action_id}&cids=1&id=&menu_id={menu_id}&model=verticali.property&view_type=form"
        # href="/web#id=${property.id}&action=${property.action_id}&model=verticali.property&view_type=form" target="_top" 
        return redirect(url)

    @http.route('/property/mapbox', type='http', auth='user', website=True)
    def show_map(self, model, id, **kw):
        record = request.env[model].sudo().browse(int(id))
        return request.render('property_custom.mapbox_template', {
            'record': record,
            'access_token': 'pk.eyJ1IjoiYWxleHNhbmNoZXoyOCIsImEiOiJjbWQ0eDd5eXkwNzJkMnZwcHRkNHY5aXdhIn0.rkOiyAbWigTbooUZadY28w',
        })

    @http.route('/property/mapbox/save', type='http', auth='user', methods=['POST'], csrf=False)
    def save_coords(self, **post):
        _logger.error(post)
        model = post.get('model')
        record_id = int(post.get('record_id'))
        lat = float(post.get('lat') or 0)
        lng = float(post.get('lng') or 0)
        record = request.env[model].sudo().browse(record_id)
        if record.exists():
            record.write({'latitude': lat, 'longitude': lng})
        action_id = request.env.ref('property_custom.verticali_property_action').id
        menu_id = request.env.ref('property_custom.menu_verticali_property_act').id
        url = f'/web#id={record_id}&action={action_id}&model=verticali.property&view_type=form&cids=1&menu_id={menu_id}'
        return redirect(url)
