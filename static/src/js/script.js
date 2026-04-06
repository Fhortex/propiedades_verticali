odoo.define('property_custom.PropertyAction', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;

    var PropertyAction = AbstractAction.extend({
        template: 'PropertyTemplate',
        events: {
            'click .apply': '_onApplyClick',
            'click .card-header': '_showModal',
            'click .close': '_closeModal',
            'click #filter_ubicacion': '_click_ubicacion',
            'click #status': '_click_status',
            'click #availability': '_click_availability',
            'click #property_types': '_click_property_type',
            'click #more_filters': '_click_more_filter',
            'click #filters': '_click_filters',
            'click .operation_action': '_click_operation_type',
        },
        
        /**
         * Método para iniciar la acción.
         */
        init: function (parent, context) {
            this._super(parent, context);
            this._fetchVerticaliPropertyData(context.context);
        },

        /**
         * Renderizamos la acción personalizada.
         */
        start: function () {
            var self = this;
            self._fetchResStatesData()
            //self._fetchUbicacionData()
            // self._fetchMunicipalitiesData(); no se usa
            // self._fetchMunicipalitiessData(); no se usa
            // self._fetchStatusData();
            // self._fetchAvailabilityData();
            // self._fetchPropertiesTypesData();
            //self._fetchResCurrencyData();
            // self._fetchLandUse();
            // self._fetchCommissionShare();
            // self._fetchDevelopmentServices();
            // self._fetchDevelopmentAtributos();
            // self._fetchDevelopmentAmenidades();
            // self._fetchPropertyServices();
            // self._fetchPropertyTipoEntrega();
            // self._fetchPropertyAtributos();
            // self._fetchPetsData();
            // self._fetchPaymentMethodsData();
            // self._fetchInvoicesData();
            // self._fetchDepositsData();
            // self._fetchWarrantyData();
        },

        /**
         * Método que llama al backend para obtener datos de municipios
         */
        _fetchResStatesData: function () {
            return this._rpc({
                model: 'res.country.state',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var $states = $('#states');
                $.each(result['records'], function(index, state) {
                    $states.append($('<option>', {
                        value: state.id,
                        text: state.name,
                    }));
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicacion
         */
        _fetchUbicacionData: function () {
            return this._rpc({
                model: 'res.country.state',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var $states = $('#statess');
                $.each(result['records'], function(index, state) {
                    $states.append($('<option>', {
                        value: state.id,
                        text: state.name,
                    }));
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchMunicipalitiesData: function () {
            return this._rpc({
                model: 'res.zona',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var $municipalities = $('#municipalities');
                $.each(result['records'], function(index, option) {
                    $municipalities.append($('<option>', {
                        value: option.id,
                        text: option.name,
                    }));
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchMunicipalitiessData: function () {
            return this._rpc({
                model: 'res.zona',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var $municipalities = $('#municipalitiess');
                $.each(result['records'], function(index, option) {
                    $municipalities.append($('<option>', {
                        value: option.id,
                        text: option.name,
                    }));
                });
            }.bind(this));
        },

        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchResCurrencyData: function () {
            return this._rpc({
                model: 'res.currency',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var $currencies = $('.currencies');
                console.log(result);
                $.each(result['records'], function(index, option) {
                    $currencies.append($('<option>', {
                        value: option.id,
                        text: option.name,
                    }));
                });
            }.bind(this));
        },

        /**
         * Método que llama al backend para obtener listado de propiedades
         */
        _fetchVerticaliPropertyData: function (params) {
            var res = this._rpc({
                model: 'verticali.property',
                method: 'get_data',
                args: [params],
            }).then(function (result) {
                $('#properties').empty();
                if (result['records'].length===0){
                    $('#pagination').hide();
                    $('#sort').hide();
                    if (params.property === 1){
                        console.log($('#new_property').attr('href'));
                        $('#new_property').show();
                    }
                    else{
                        $('#new_property').hide();
                    }
                    $('#properties').attr("class","row mb-5 text-center");
                    $('#properties').append('<div class="col-12 mt-5"><p>Por el momento no hay propiedades con tus criterios de búsqueda.</p></div>');
                    $('#properties').append('<div class="col-12 mt-0 mb-5"><a href="#" onclick="location.reload(); return false;" class="m-2" data-toggle="tooltip" title="Limpiar filtros">Limpiar filtros</a></div>');
                }
                else{
                    if (result['menu_action']){
                        $('#menu_action').val(result['menu_action']);
                    }
                    $('#pagination').show();
                    $('#pagination').html(result['pagination']);
                    if (result['pagination']){
                        $('#sort').show();
                    }
                    else{
                        $('#sort').hide();
                    }

                    $.each(result['records'], function(index, property) {
                        var properties = $('#properties');
                        // var images = "";
                        // var c = 0;
                        // $.each(property.images, function(i, image) {
                        //     c += 1;
                        //     var active = "";
                        //     if (c==1){
                        //         active = "active";
                        //     }
                        //     images +=  `<div class="carousel-item `+ active +`">
                        //                     <img class="d-block w-100" src="${image}" alt="First slide" style="width: 100%;height:300px;object-fit: cover;">
                        //                 </div>`;
                        // });
                        // <div class="card col-12 col-md-12 col-lg-3 mb-2 mb-md-2 ml-md-0 ml-lg-5 mt-lg-2 p-0" >
                        //                         <div id="carousel-${property.id}" class="carousel slide card-img-top p-0 m-0" data-ride="carousel">
                        //                             <div class="carousel-inner">
                        //                                 `+ images +`
                        //                             </div>
                        //                             <a class="carousel-control-prev" href="#carousel-${property.id}" role="button" data-slide="prev">
                        //                                 <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                        //                                 <span class="sr-only">Previous</span>
                        //                             </a>
                        //                             <a class="carousel-control-next" href="#carousel-${property.id}" role="button" data-slide="next">
                        //                                 <span class="carousel-control-next-icon" aria-hidden="true"></span>
                        //                                 <span class="sr-only">Next</span>
                        //                             </a>
                        //                         </div>
                        properties.append(`<div class="card col-12 col-md-12 col-lg-3 mb-2 mb-md-2 ml-md-0 ml-lg-5 mt-lg-2 p-0" >
                                                <img data-id="${property.id}" class="d-block w-100 card-header p-0 m-0" src="${property.image}" alt="First slide" style="width: 100%;height:300px;object-fit: cover;">
                                                <div class="card-body">
                                                    <h5 class="card-title m-1">${property.id_eb}</h5>
 						    <a target="_blank" href="/property/view/detail/${property.id}/${property.current_page}" style="display: inline-block;max-width: 100%;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;" class="m-1">${property.title}</a>                                                    
                                                    <p class="card-text m-1"><strong>${property.symbol} ${property.price}</strong> En ${property.type_ope}</p>
                                                    <p class="card-text m-1" style="display: inline-block;max-width: 100%;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;">${property.description}</p>
                                                    <div class="m-1">
                                                        <i class="fa fa-bed"/>
                                                        <span>${property.bedrooms}</span>
                                                        <i class="fa fa-bath ml-2"/>
                                                        <span>${property.bathrooms}</span>
                                                        <i class="fa fa-car ml-2"/>
                                                        <span>${property.parking_lot}</span>
                                                        <i class="fa fa-cube ml-2"/>
                                                        <span>${property.constructions} m²</span>
                                                        <i class="fa fa-expand ml-2"/>
                                                        <span>${property.lans} ${property.lans_uom_id}</span>
                                                    </div>
                                                    <i class="fa fa-key"/>
                                                    <span>${property.adviser}</span><br/>

                                                    <strong>Estatus: </strong><span>${property.status}</span><br/>
                                                    <strong>Disponibilidad: </strong><span>${property.availability}</span>
                                                </div>
                                             </div>`);
                                            });
                    if (params.property === 1){
                        $('#new_property').show();
                    }
                    else{
                        $('#new_property').hide();
                    }
                }
            }.bind(this));
            return res;
        },

        _showModal: function(ev){
            const params = {
                id: $(ev.currentTarget).data('id'),
            };
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_images',
                args: [params],
            }).then(function (result) {
                let card = $(this).closest(".card");
                let title = card.find(".card-title").text();
                let description = card.find(".card-text").first().text();
                $("#modalTitle").text(title);
                $("#modalBody").text(description);
                $("#myModal").fadeIn();
                var images = "";
                var c = 0;

                $.each(result['images'], function(i, image) {
                    c += 1;
                    var active = "";
                    if (c==1){
                        active = "active";
                    }
                    images +=  `<div class="carousel-item `+ active +`">
                                    <img class="d-block w-100" src="${image}" alt="First slide" style="max-width: 100%;max-height: 80vh;display: block;margin: auto;">
                                </div>`;
                });


                var modal_images = $('.modal_images');
                modal_images.append(`<div class="card col-12 p-0" >
                                        <div id="carousel-${$(ev.currentTarget).data('id')}" class="carousel slide card-img-top p-0 m-0" data-ride="carousel">
                                            <div class="carousel-inner" style="width: 100%; height: 100%; object-fit: cover;">
                                                `+ images +`
                                            </div>
                                            <a class="carousel-control-prev" href="#carousel-${$(ev.currentTarget).data('id')}" role="button" data-slide="prev">
                                                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                                                <span class="sr-only">Previous</span>
                                            </a>
                                            <a class="carousel-control-next" href="#carousel-${$(ev.currentTarget).data('id')}" role="button" data-slide="next">
                                                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                                                <span class="sr-only">Next</span>
                                            </a>
                                        </div>`);
            }.bind(this));
        },

        _closeModal: function(){
            $("#myModal").fadeOut();
        },

        _click_ubicacion: function(){
            this._fetchUbicacionData();
        },

        _click_status: function(){
            this._fetchStatusData();
        },

        _click_availability: function(){
            this._fetchAvailabilityData();
        },

        _click_property_type: function(){
            this._fetchPropertiesTypesData();
        },

        _click_operation_type: function(){
            console.log('_click_operation_type');
            this._fetchResCurrencyData();
        },

        _click_more_filter: function(){
            this._fetchResCurrencyData();
            this._fetchLandUse();
            this._fetchCommissionShare();
            this._fetchDevelopmentServices();
            this._fetchDevelopmentAtributos();
            this._fetchDevelopmentAmenidades();
            this._fetchPropertyServices();
            this._fetchPropertyTipoEntrega();
            this._fetchPropertyAtributos();
            this._fetchPetsData();
            this._fetchPaymentMethodsData();
            this._fetchInvoicesData();
            this._fetchDepositsData();
            this._fetchWarrantyData();
        },
        _click_filters: function(){
            this._fetchResCurrencyData();
            this._fetchStatusData();
            this._fetchAvailabilityData();
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchStatusData: function () {
            return this._rpc({
                model: 'property.status',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var status = $('.status');
                $.each(result['records'], function(index, item) {
                    console.log(item);
                    status.append(`<div class="form-check">
                                            <input type="checkbox" class="form-check-input status_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="exampleCheck1">${item.name}</label>
                                        </div>`); 
                });
            }.bind(this));
        },

        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchAvailabilityData: function () {
            return this._rpc({
                model: 'property.availability',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var availability = $('.availability');
                $.each(result['records'], function(index, item) {
                    availability.append(`<div class="form-check">
                                            <input type="checkbox" class="form-check-input availables_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="exampleCheck1">${item.name}</label>
                                        </div>`); 
                });
            }.bind(this));
        },

        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchPropertiesTypesData: function () {
            return this._rpc({
                model: 'res.property',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                var property_types = $('.property_types');
                $.each(result['records'], function(index, item) {
                    property_types.append(`<div class="form-check">
                                            <input type="checkbox" class="form-check-input property_types_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="exampleCheck1">${item.name}</label>
                                        </div>`); 
                });
            }.bind(this));
        },
        // Método para manejar el clic en el primer botón
        _onApplyClick: function (ev) {
            console.log('Click:');
            console.log($(ev.currentTarget).data('property'));
            $('#filters_md').removeClass('d-none').addClass('d-none');
            $('#properties').removeClass('d-none');

            var status_checks = [];

            $('.status_checks:checked').each(function() {
                status_checks.push($(this).attr('id'));
            });

            var availables_checks = [];
            $('.availables_checks:checked').each(function() {
                availables_checks.push($(this).attr('id'));
            });

            var property_types_checks = [];
            $('.property_types_checks:checked').each(function() {
                property_types_checks.push($(this).attr('id'));
            });

            var investment_property_checks = [];
            $('.investment_property_checks:checked').each(function() {
                investment_property_checks.push($(this).attr('id'));
            });

            var land_use_checks = [];
                $('.land_use_checks:checked').each(function() {
                land_use_checks.push($(this).attr('id'));
            });

            var commission_share_checks = [];
                $('.commission_share_checks:checked').each(function() {
                commission_share_checks.push($(this).attr('id'));
            });

            const hash = window.location.hash;
            const attributes = new URLSearchParams(hash.replace('#', ''));
            var property = 1;
            if (attributes.get('action') == '591') {property = 1;}
            else if (attributes.get('action') == '592') {property = 2;}
            else if (attributes.get('action') == '593') {property=3;}

            //caracteristicas desarrollo
            var development_services_checks = [];
            $('.development_services_checks:checked').each(function() {
                development_services_checks.push($(this).attr('id'));
            });
            var development_atributos_checks = [];
            $('.development_atributos_checks:checked').each(function() {
                development_atributos_checks.push($(this).attr('id'));
            });
            var development_amenidades_checks = [];
            $('.development_amenidades_checks:checked').each(function() {
                development_amenidades_checks.push($(this).attr('id'));
            });

            //caracteristicas desarrollo
            var property_services_checks = [];
            $('.property_services_checks:checked').each(function() {
                property_services_checks.push($(this).attr('id'));
            });
            var property_tipo_entrega_checks = [];
            $('.property_tipo_entrega_checks:checked').each(function() {
                property_tipo_entrega_checks.push($(this).attr('id'));
            });
            var property_amenidades_checks = [];
            $('.property_amenidades_checks:checked').each(function() {
                property_amenidades_checks.push($(this).attr('id'));
            });

            //politicas
            var pets_checks = [];
            $('.pets_checks:checked').each(function() {
                pets_checks.push($(this).attr('id'));
            });
            var payment_methods_checks = [];
            $('.payment_methods_checks:checked').each(function() {
                payment_methods_checks.push($(this).attr('id'));
            });
            var invoices_checks = [];
            $('.invoices_checks:checked').each(function() {
                invoices_checks.push($(this).attr('id'));
            });   
            
            //condiciones
            var warranty_checks = [];
            $('.warranty_checks:checked').each(function() {
                warranty_checks.push($(this).attr('id'));
            });   
            var deposits_checks = [];
            $('.deposits_checks:checked').each(function() {
                deposits_checks.push($(this).attr('id'));
            });   

            const params = {
                states: $('#states').val(),
                statess: $('#statess').val(),
                municipalities: $('#municipalities').val(),
                locations: $('#locations').val(),
                status: status_checks,
                availability: availables_checks,
                property_types: property_types_checks,
                operation_type: $('a.operation_actions.active').attr('id'),
                price_min: $('#min_price').val(),
                price_max: $('#max_price').val(),
                currency_id: $('#currencies').val(),
                name: $('#search').val(),
                beds: $('a.bed_actions.active').attr('id'),
                baths: $('a.bath_actions.active').attr('id'),
                parks: $('a.park_actions.active').attr('id'),
                construction_from: $('#construction_from').val(),
                construction_to: $('#construction_to').val(),
                land_from: $('#land_from').val(),
                land_to: $('#land_to').val(),
                land_use_checks: land_use_checks,
                investment_property_checks: investment_property_checks,
                commission_share_checks: commission_share_checks,
                development_services_checks: development_services_checks,
                development_atributos_checks: development_atributos_checks,
                development_amenidades_checks: development_amenidades_checks,
                property_services_checks: property_services_checks,
                property_tipo_entrega_checks: property_tipo_entrega_checks,
                property_amenidades_checks: property_amenidades_checks,
                pets_checks: pets_checks,
                payment_methods_checks: payment_methods_checks,
                invoices_checks: invoices_checks,
                warranty_checks: warranty_checks,
                deposits_checks: deposits_checks,
                current_page: $(ev.currentTarget).data('page'),
                property: property,
                order_by: $('input[name="order_by"]:checked').val()
            };
            $('#properties').empty();
            this._fetchVerticaliPropertyData(params);
            $('#more_filters_modal').modal('hide');
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _getActionURL: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_action_url',
                args: [],
            }).then(function (result) {
                $('#new_property').attr("href",result.url)
            }.bind(this));  
        },
        /**
         * Método que llama al backend para obtener datos de servicios (desarrollo)
         */
        _fetchLandUse: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_land_use',
                args: [],
            }).then(function (result) {
                var records = $('#land_use');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input land_use_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de servicios (desarrollo)
         */
        _fetchCommissionShare: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_commission_share',
                args: [],
            }).then(function (result) {
                var records = $('#commission_share');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input commission_share_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de servicios (desarrollo)
         */
        _fetchDevelopmentServices: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_development_services',
                args: [],
            }).then(function (result) {
                var records = $('#development_services');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input development_services_checks" id="${item.name}"/>
                                            <label class="form-check-label" for="${item.name}">${item.description}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },    
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchDevelopmentAtributos: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_development_atributos',
                args: [],
            }).then(function (result) {
                var records = $('#development_atributos');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input development_atributos_checks" id="${item.name}"/>
                                            <label class="form-check-label" for="${item.name}">${item.description}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchDevelopmentAmenidades: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_development_amenidades',
                args: [],
            }).then(function (result) {
                var records = $('#development_amenidades');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input development_amenidades_checks" id="${item.name}"/>
                                            <label class="form-check-label" for="${item.name}">${item.description}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de servicios (desarrollo)
         */
        _fetchPropertyServices: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_property_services',
                args: [],
            }).then(function (result) {
                var records = $('#property_services');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input property_services_checks" id="${item.name}"/>
                                            <label class="form-check-label" for="${item.name}">${item.description}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },    
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchPropertyTipoEntrega: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_property_tipo_entrega',
                args: [],
            }).then(function (result) {
                var records = $('#property_tipo_entrega');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input property_tipo_entrega_checks" id="${item.name}"/>
                                            <label class="form-check-label" for="${item.name}">${item.description}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchPropertyAtributos: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_property_atributos',
                args: [],
            }).then(function (result) {
                var records = $('#property_atributos');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-6"><div class="form-check m-2">
                                            <input type="checkbox" class="form-check-input property_amenidades_checks" id="${item.name}"/>
                                            <label class="form-check-label" for="${item.name}">${item.description}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchPetsData: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_pets',
                args: [],
            }).then(function (result) {
                var records = $('.pets');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-12"><div class="form-check m-1">
                                            <input type="checkbox" class="form-check-input pets_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchPaymentMethodsData: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_payment_methods',
                args: [],
            }).then(function (result) {
                var records = $('.payment_methods');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-12"><div class="form-check m-1">
                                            <input type="checkbox" class="form-check-input payment_methods_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchInvoicesData: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_invoices',
                args: [],
            }).then(function (result) {
                var records = $('.invoices');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-12"><div class="form-check m-1">
                                            <input type="checkbox" class="form-check-input invoices_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },

        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchWarrantyData: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_warranty',
                args: [],
            }).then(function (result) {
                var records = $('.warranty');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-12"><div class="form-check m-1">
                                            <input type="checkbox" class="form-check-input warranty_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
        /**
         * Método que llama al backend para obtener datos de ubicaciones
         */
        _fetchDepositsData: function () {
            return this._rpc({
                model: 'verticali.property',
                method: 'get_data_deposits',
                args: [],
            }).then(function (result) {
                var records = $('.deposits');
                $.each(result['fields'], function(index, item) {
                    records.append(`<div class="col-12"><div class="form-check m-1">
                                            <input type="checkbox" class="form-check-input deposits_checks" id="${item.id}"/>
                                            <label class="form-check-label" for="${item.id}">${item.name}</label>
                                       </div></div>`); 
                });
            }.bind(this));
        },
    });

    core.action_registry.add('web_property', PropertyAction);
    return PropertyAction;
});
