/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class WebProperty extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.inputRef = useRef("searchInput");
        
        this.state = useState({
            query: "",
            options: [],
            selectedItems: [], // Array de items seleccionados
            showDropdown: false,
            isLoading: false,
        });

        this.searchTimeout = null;
        this.loadOptions();
    }

    async loadOptions() {
        this.state.isLoading = true;
        const domain = this.state.query
            ? [["name", "ilike", this.state.query]]
            : [];
        
        try {
            // const res = await this.orm.searchRead(
            //     "res.partner", 
            //     domain, 
            //     ["id", "name", "email", "phone"], 
            //     { limit: 20 }
            // );
            const res = await this.orm.call(
                "res.country.state",
                "get_data", 
                [],
                {                
                    search: this.state.query,
                    limit: 10
                }
            );
            
            // ✅ res retorna: {records: [{id: 's1', name: '...'}, ...]}
            // Acceder al array dentro de 'records'
            const allRecords = res.records || [];
            
            // Filtrar opciones ya seleccionadas
            const selectedIds = this.state.selectedItems.map(item => item.id);
            this.state.options = allRecords.filter(opt => !selectedIds.includes(opt.id));
        } catch (error) {
            console.log(error);
            this.notification.add("Error al cargar opciones", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    onInput(ev) {
        this.state.query = ev.target.value;
        this.state.showDropdown = true;
        
        // Debounce para no hacer muchas peticiones
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadOptions();
        }, 300);
    }

    onFocus() {
        this.state.showDropdown = true;
        if (this.state.options.length === 0) {
            this.loadOptions();
        }
    }

    onBlur() {
        // Pequeño delay para permitir clicks en el dropdown
        setTimeout(() => {
            this.state.showDropdown = false;
        }, 200);
    }

    selectOption(option) {
        // Agregar a seleccionados
        this.state.selectedItems.push(option);
        
        // Limpiar búsqueda y recargar opciones
        this.state.query = "";
        this.loadOptions();
        
        // Notificar
        // this.notification.add(`Agregado: ${option.name}`, { 
        //     type: "success",
        //     className: "o_notification_fade"
        // });
        
        // Focus en el input
        if (this.inputRef.el) {
            this.inputRef.el.focus();
        }
    }

    removeItem(item) {
        const index = this.state.selectedItems.findIndex(i => i.id === item.id);
        if (index > -1) {
            this.state.selectedItems.splice(index, 1);
            this.loadOptions(); // Recargar para mostrar la opción nuevamente
            this.notification.add(`Eliminado: ${item.name}`, { 
                type: "info",
                className: "o_notification_fade"
            });
        }
    }

    clearAll() {
        this.state.selectedItems = [];
        this.state.query = "";
        this.loadOptions();
        // this.notification.add("Todas las selecciones eliminadas", { type: "info" });
    }
}

WebProperty.template = "property_custom.WebProperty";

// ✅ REGISTRO COMO ACCIÓN
registry.category("actions").add("property_custom.web_property", WebProperty);
