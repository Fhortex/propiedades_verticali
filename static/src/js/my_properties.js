/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class WebProperty extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        this.inputRef = useRef("searchInput");

        this.state = useState({
            // Opciones de filtros
            availabilityOptions: [],    // [{id: 1, name: 'Disponible'}, ...]
            statusOptions: [],
            propertyTypeOptions: [],
            currencyOptions: [],         // [{id: 1, name: 'MXN', symbol: '$'}, ...]
            
            // Seleccionados
            selectedAvailability: [],   // [1, 2, 3]
            selectedStatus: [],
            selectedPropertyTypes: [],
            selectedOperation: '',  // 'Venta', 'Renta', 'Preventa'
            
            // Precios
            minPrice: '',
            maxPrice: '',
            currency: '',  // ID de la moneda seleccionada
            
            // Resultados
            properties: [],
            isLoading: false,
        });

        this.loadProperties();
        this.loadAvailabilityOptions();
        this.loadStatusOptions();
        this.loadPropertyTypeOptions();
        this.loadCurrencyOptions();
    }

    // ✅ Cargar opciones de estatus
    async loadStatusOptions() {
        try {
            const res = await this.orm.call(
                'property.status',
                'get_data',
                [],
                {}
            );
            
            this.state.statusOptions = res.records || res || [];
        } catch (error) {
            console.error("Error al cargar estatus:", error);
        }
    }

    // ✅ Cargar opciones de disponibilidad
    async loadAvailabilityOptions() {
        try {
            const res = await this.orm.call(
                'property.availability',
                'get_data',
                [],
                {}
            );
            
            this.state.availabilityOptions = res.records || res || [];
        } catch (error) {
            console.error("Error al cargar disponibilidad:", error);
        }
    }

    // ✅ Cargar tipos de propiedad
    async loadPropertyTypeOptions() {
        try {
            // const res = await this.orm.searchRead(
            //     'property.type',
            //     [],
            //     ['id', 'name'],
            //     { limit: 100, order: 'name ASC' }
            // );
            const res = await this.orm.call(
                'res.property',
                'get_data',
                [],
                {}
            );
            
            this.state.propertyTypeOptions = res.records || res || [];
        } catch (error) {
            console.error("Error al cargar tipos:", error);
        }
    }

    // ✅ Cargar opciones de moneda desde res.currency
    async loadCurrencyOptions() {
        try {
            const res = await this.orm.searchRead(
                'res.currency',
                [['active', '=', true]],  // Solo monedas activas
                ['id', 'name', 'symbol'],
                { limit: 50, order: 'name ASC' }
            );
            
            this.state.currencyOptions = res || [];
            
            // Establecer MXN como moneda por defecto si existe
            const mxn = res.find(c => c.name === 'MXN');
            if (mxn && !this.state.currency) {
                this.state.currency = mxn.id;
            }
        } catch (error) {
            console.error("Error al cargar monedas:", error);
        }
    }

    // ✅ Toggle checkbox
    toggleAvailability(itemId) {
        const index = this.state.selectedAvailability.indexOf(itemId);
        
        if (index > -1) {
            // Ya está seleccionado, quitarlo
            this.state.selectedAvailability.splice(index, 1);
        } else {
            // No está seleccionado, agregarlo
            this.state.selectedAvailability.push(itemId);
        }
        // Recargar propiedades con nuevos filtros
        // this.loadProperties();
    }

    toggleStatus(itemId) {
        const index = this.state.selectedStatus.indexOf(itemId);
        if (index > -1) {
            this.state.selectedStatus.splice(index, 1);
        } else {
            this.state.selectedStatus.push(itemId);
        }
        // this.loadProperties();
    }

    togglePropertyType(itemId) {
        const index = this.state.selectedPropertyTypes.indexOf(itemId);
        if (index > -1) {
            this.state.selectedPropertyTypes.splice(index, 1);
        } else {
            this.state.selectedPropertyTypes.push(itemId);
        }
        // this.loadProperties();
    }

    // ✅ Verificar si está seleccionado
    isAvailabilitySelected(itemId) {
        return this.state.selectedAvailability.includes(itemId);
    }

    isStatusSelected(itemId) {
        return this.state.selectedStatus.includes(itemId);
    }

    isPropertyTypeSelected(itemId) {
        return this.state.selectedPropertyTypes.includes(itemId);
    }

    // ✅ Seleccionar tipo de operación
    selectOperation(operation) {
        this.state.selectedOperation = operation;
        console.log(`✅ Operación seleccionada: ${operation}`);
    }

    // ✅ Manejar cambio de moneda
    onCurrencyChange(event) {
        const value = event.target.value;
        this.state.currency = value ? parseInt(value) : null;
    }

    // ✅ Abrir formulario de nueva propiedad
    async openNewPropertyForm() {
        try {
            await this.action.doAction('property_custom.verticali_property_action', {
                additionalContext: {
                    default_state: 'new',
                }
            });
        } catch (error) {
            console.error("Error al abrir formulario de propiedad:", error);
            this.notification.add("Error al abrir el formulario", { type: "danger" });
        }
    }

    // ✅ Abrir detalle de propiedad
    async openPropertyDetail(propertyId) {
        try {
            // Verificar permisos del usuario
            const canEdit = await this.checkPropertyEditPermission(propertyId);
            
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'verticali.property',
                res_id: propertyId,
                views: [[false, 'form']],
                target: 'current',
                context: {
                    form_view_initial_mode: canEdit ? 'edit' : 'readonly',
                }
            });
        } catch (error) {
            console.error("Error al abrir detalle de propiedad:", error);
            this.notification.add("Error al abrir la propiedad", { type: "danger" });
        }
    }

    // ✅ Verificar si el usuario puede editar la propiedad
    async checkPropertyEditPermission(propertyId) {
        try {
            // Llamar al método Python que verifica los permisos
            const canEdit = await this.orm.call(
                'verticali.property',
                'check_user_can_edit',
                [propertyId]
            );
            
            return canEdit;
            
        } catch (error) {
            console.error("Error verificando permisos:", error);
            return false;  // En caso de error, denegar edición
        }
    }

    applyFilters() {
        this.state.openFilter = null;
        this.state.currentPage = 1;
        this.loadProperties();
        this.notification.add("Filtros aplicados", { type: "success" });
    }
    
    async loadProperties() {
        this.state.isLoading = true;
        
        try {
            const res = await this.orm.call(
                'verticali.property',
                'get_data',
                [],
                {
                    params: {
                        availability_id: this.state.selectedAvailability,
                        status_id: this.state.selectedStatus,
                        property_type_id: this.state.selectedPropertyTypes,
                        operation_type: this.state.selectedOperation,
                        min_price: this.state.minPrice || null,
                        max_price: this.state.maxPrice || null,
                        currency_id: this.state.currency || null,
                    }
                }
            );
            this.state.properties = res.records || res || [];
            
        } catch (error) {
            console.error("Error cargando propiedades:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    // ✅ Limpiar todos los filtros
    clearAllFilters() {
        this.state.selectedStatus = [];
        this.state.selectedAvailability = [];
        this.state.selectedPropertyTypes = [];
        this.state.selectedOperation = '';
        this.state.minPrice = '';
        this.state.maxPrice = '';
        
        // Resetear a la moneda MXN por defecto
        const mxn = this.state.currencyOptions.find(c => c.name === 'MXN');
        this.state.currency = mxn ? mxn.id : '';
        
        this.loadProperties();
        
        this.notification.add("Filtros limpiados", { type: "info" });
    }
}

WebProperty.template = "property_custom.MyProperties";

// ✅ REGISTRO COMO ACCIÓN
registry.category("actions").add("property_custom.web_property", WebProperty);
