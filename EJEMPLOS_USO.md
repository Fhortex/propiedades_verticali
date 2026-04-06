# 🎯 Ejemplos Prácticos de Componentes Multi-Select

## 📋 Tabla de Contenidos

1. [Selector de Propiedades](#1-selector-de-propiedades)
2. [Selector de Estados/Municipios](#2-selector-de-estadosmunicipios)
3. [Selector con Filtros Avanzados](#3-selector-con-filtros-avanzados)
4. [Selector de Imágenes](#4-selector-de-imágenes)
5. [Tips de Integración](#tips-de-integración)

---

## 1️⃣ Selector de Propiedades

### JavaScript (`property_selector.js`)

```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PropertySelector extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.inputRef = useRef("searchInput");
        
        this.state = useState({
            query: "",
            options: [],
            selectedItems: [],
            showDropdown: false,
            isLoading: false,
            // NUEVO: Filtros adicionales
            selectedType: "",
            selectedZone: "",
        });

        this.searchTimeout = null;
        this.loadOptions();
    }

    async loadOptions() {
        this.state.isLoading = true;
        
        // Construir dominio dinámico
        const domain = [["active", "=", true]];
        
        // Filtro por búsqueda
        if (this.state.query) {
            domain.push(["name", "ilike", this.state.query]);
        }
        
        // Filtro por tipo de operación
        if (this.state.selectedType) {
            domain.push(["type_ope", "=", this.state.selectedType]);
        }
        
        // Filtro por zona
        if (this.state.selectedZone) {
            domain.push(["zona_id", "=", parseInt(this.state.selectedZone)]);
        }
        
        try {
            const res = await this.orm.searchRead(
                "verticali.property",
                domain,
                ["id", "name", "property_id", "type_ope", "zona_id", "price"],
                { limit: 20, order: "price DESC" }
            );
            
            const selectedIds = this.state.selectedItems.map(item => item.id);
            this.state.options = res.filter(opt => !selectedIds.includes(opt.id));
        } catch (error) {
            this.notification.add("Error al cargar propiedades", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    onInput(ev) {
        this.state.query = ev.target.value;
        this.state.showDropdown = true;
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => this.loadOptions(), 300);
    }

    onTypeChange(ev) {
        this.state.selectedType = ev.target.value;
        this.loadOptions();
    }

    onZoneChange(ev) {
        this.state.selectedZone = ev.target.value;
        this.loadOptions();
    }

    onFocus() {
        this.state.showDropdown = true;
        if (this.state.options.length === 0) this.loadOptions();
    }

    onBlur() {
        setTimeout(() => this.state.showDropdown = false, 200);
    }

    selectOption(option) {
        this.state.selectedItems.push(option);
        this.state.query = "";
        this.loadOptions();
        this.notification.add(`Propiedad agregada: ${option.name}`, { type: "success" });
        if (this.inputRef.el) this.inputRef.el.focus();
    }

    removeItem(item) {
        const index = this.state.selectedItems.findIndex(i => i.id === item.id);
        if (index > -1) {
            this.state.selectedItems.splice(index, 1);
            this.loadOptions();
        }
    }

    clearAll() {
        this.state.selectedItems = [];
        this.state.query = "";
        this.loadOptions();
    }
    
    // NUEVO: Calcular total de precios
    get totalPrice() {
        return this.state.selectedItems.reduce((sum, item) => sum + (item.price || 0), 0);
    }
}

PropertySelector.template = "property_custom.PropertySelector";
registry.category("actions").add("property_custom.property_selector", PropertySelector);
```

### Template XML (`property_selector.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="property_custom.PropertySelector" owl="1">
        <div class="o_property_selector p-4">
            <h2 class="mb-3">Selector de Propiedades</h2>

            <!-- Filtros adicionales -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <label>Tipo de Operación</label>
                    <select class="form-select" t-on-change="onTypeChange">
                        <option value="">Todos</option>
                        <option value="Venta">Venta</option>
                        <option value="Renta">Renta</option>
                        <option value="Preventa">Preventa</option>
                    </select>
                </div>
            </div>

            <!-- Input con chips -->
            <div class="position-relative mb-3">
                <div class="border rounded p-2 bg-white" style="min-height: 50px;">
                    <t t-foreach="state.selectedItems" t-as="item" t-key="item.id">
                        <span class="badge bg-primary me-1 mb-1">
                            <span t-esc="item.name"/>
                            <button type="button" 
                                    class="btn-close btn-close-white ms-2" 
                                    t-on-click="() => this.removeItem(item)"/>
                        </span>
                    </t>
                    
                    <input type="text"
                           t-ref="searchInput"
                           placeholder="Buscar propiedades..."
                           class="border-0"
                           style="outline: none; min-width: 300px;"
                           t-on-input="onInput"
                           t-on-focus="onFocus"
                           t-on-blur="onBlur"
                           t-att-value="state.query"/>
                </div>

                <!-- Dropdown -->
                <div t-if="state.showDropdown" 
                     class="position-absolute w-100 border rounded shadow-sm bg-white mt-1" 
                     style="max-height: 300px; overflow-y: auto; z-index: 1000;">
                    
                    <t t-if="state.isLoading">
                        <div class="text-center p-3">
                            <div class="spinner-border spinner-border-sm"/>
                            <span class="ms-2">Buscando...</span>
                        </div>
                    </t>
                    
                    <t t-elif="state.options.length > 0">
                        <t t-foreach="state.options" t-as="opt" t-key="opt.id">
                            <div class="dropdown-item p-2" 
                                 style="cursor: pointer;"
                                 t-on-click="() => this.selectOption(opt)">
                                <div class="fw-bold" t-esc="opt.name"/>
                                <small class="text-muted">
                                    <span t-esc="opt.type_ope"/> - 
                                    $<span t-esc="opt.price"/>
                                </small>
                            </div>
                        </t>
                    </t>
                    
                    <t t-else="">
                        <div class="text-center text-muted p-3">
                            No se encontraron resultados
                        </div>
                    </t>
                </div>
            </div>

            <!-- Resumen -->
            <t t-if="state.selectedItems.length > 0">
                <div class="alert alert-success">
                    <h5>Total: $<t t-esc="this.totalPrice.toFixed(2)"/></h5>
                    <p><t t-esc="state.selectedItems.length"/> propiedades seleccionadas</p>
                    <button class="btn btn-sm btn-danger" t-on-click="clearAll">
                        Limpiar
                    </button>
                </div>
            </t>
        </div>
    </t>
</templates>
```

---

## 2️⃣ Selector de Estados/Municipios (Cascada)

```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LocationSelector extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.inputRef = useRef("searchInput");
        
        this.state = useState({
            query: "",
            options: [],
            selectedItems: [],
            showDropdown: false,
            isLoading: false,
            // Estados disponibles
            states: [],
            selectedStateId: null,
        });

        this.searchTimeout = null;
        this.loadStates();
    }

    async loadStates() {
        try {
            const states = await this.orm.searchRead(
                "res.country.state",
                [["country_id.code", "=", "MX"]],  // Solo México
                ["id", "name"],
                { order: "name ASC" }
            );
            this.state.states = states;
        } catch (error) {
            this.notification.add("Error al cargar estados", { type: "danger" });
        }
    }

    async loadOptions() {
        if (!this.state.selectedStateId) {
            this.notification.add("Selecciona un estado primero", { type: "warning" });
            return;
        }

        this.state.isLoading = true;
        
        const domain = [
            ["state_id", "=", this.state.selectedStateId]
        ];
        
        if (this.state.query) {
            domain.push(["name", "ilike", this.state.query]);
        }
        
        try {
            const res = await this.orm.searchRead(
                "res.zona",
                domain,
                ["id", "name", "state_id"],
                { limit: 50, order: "name ASC" }
            );
            
            const selectedIds = this.state.selectedItems.map(item => item.id);
            this.state.options = res.filter(opt => !selectedIds.includes(opt.id));
        } catch (error) {
            this.notification.add("Error al cargar municipios", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    onStateChange(ev) {
        this.state.selectedStateId = parseInt(ev.target.value) || null;
        this.state.options = [];
        this.loadOptions();
    }

    onInput(ev) {
        this.state.query = ev.target.value;
        this.state.showDropdown = true;
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => this.loadOptions(), 300);
    }

    onFocus() {
        this.state.showDropdown = true;
        if (this.state.options.length === 0) this.loadOptions();
    }

    onBlur() {
        setTimeout(() => this.state.showDropdown = false, 200);
    }

    selectOption(option) {
        this.state.selectedItems.push(option);
        this.state.query = "";
        this.loadOptions();
        this.notification.add(`Municipio agregado: ${option.name}`, { type: "success" });
        if (this.inputRef.el) this.inputRef.el.focus();
    }

    removeItem(item) {
        const index = this.state.selectedItems.findIndex(i => i.id === item.id);
        if (index > -1) {
            this.state.selectedItems.splice(index, 1);
            this.loadOptions();
        }
    }

    clearAll() {
        this.state.selectedItems = [];
        this.state.query = "";
        this.loadOptions();
    }
}

LocationSelector.template = "property_custom.LocationSelector";
registry.category("actions").add("property_custom.location_selector", LocationSelector);
```

---

## 3️⃣ Selector con Imágenes

```javascript
async loadOptions() {
    this.state.isLoading = true;
    
    const domain = this.state.query
        ? [["name", "ilike", this.state.query]]
        : [];
    
    try {
        const res = await this.orm.searchRead(
            "res.partner",
            domain,
            ["id", "name", "image_128"],  // ⭐ Incluir imagen
            { limit: 20 }
        );
        
        const selectedIds = this.state.selectedItems.map(item => item.id);
        this.state.options = res.filter(opt => !selectedIds.includes(opt.id));
    } catch (error) {
        this.notification.add("Error al cargar", { type: "danger" });
    } finally {
        this.state.isLoading = false;
    }
}
```

### Template con imágenes

```xml
<div class="dropdown-item p-2 d-flex align-items-center" 
     style="cursor: pointer;"
     t-on-click="() => this.selectOption(opt)">
    <!-- Imagen -->
    <img t-if="opt.image_128" 
         t-att-src="`data:image/png;base64,${opt.image_128}`"
         class="rounded-circle me-2"
         style="width: 40px; height: 40px; object-fit: cover;"/>
    
    <!-- Sin imagen -->
    <div t-else="" 
         class="rounded-circle me-2 bg-secondary d-flex align-items-center justify-content-center"
         style="width: 40px; height: 40px;">
        <i class="fa fa-user text-white"/>
    </div>
    
    <!-- Info -->
    <div>
        <div class="fw-bold" t-esc="opt.name"/>
        <small class="text-muted" t-esc="opt.email"/>
    </div>
</div>
```

---

## 🔗 Tips de Integración

### 1. Pasar datos desde Python

```python
# En tu método Python
def action_open_selector(self):
    return {
        'type': 'ir.actions.client',
        'tag': 'property_custom.property_selector',
        'context': {
            'default_state_id': self.state_id.id,  # Pre-filtro
            'allowed_types': ['Venta', 'Renta'],   # Tipos permitidos
        }
    }
```

```javascript
// En setup() del componente
setup() {
    // ...
    const context = this.props.action.context || {};
    this.defaultStateId = context.default_state_id;
    this.allowedTypes = context.allowed_types || [];
}

async loadOptions() {
    const domain = [];
    
    // Usar valores del context
    if (this.defaultStateId) {
        domain.push(["state_id", "=", this.defaultStateId]);
    }
    
    if (this.allowedTypes.length > 0) {
        domain.push(["type_ope", "in", this.allowedTypes]);
    }
    
    // ... resto del código
}
```

### 2. Enviar datos de vuelta a Python

```javascript
async saveSelection() {
    const selectedIds = this.state.selectedItems.map(item => item.id);
    
    try {
        await this.orm.call(
            "mi.modelo",
            "process_selection",
            [selectedIds],
            { additional_data: "value" }
        );
        
        this.notification.add("Guardado exitosamente", { type: "success" });
    } catch (error) {
        this.notification.add("Error al guardar", { type: "danger" });
    }
}
```

### 3. Validaciones antes de seleccionar

```javascript
selectOption(option) {
    // Máximo 5 selecciones
    if (this.state.selectedItems.length >= 5) {
        this.notification.add("Máximo 5 selecciones permitidas", { 
            type: "warning" 
        });
        return;
    }
    
    // Validar precio
    if (option.price > 10000000) {
        this.notification.add("Propiedad muy cara", { type: "warning" });
        return;
    }
    
    // Todo OK, agregar
    this.state.selectedItems.push(option);
    this.loadOptions();
}
```

---

## 📊 Agregar al Manifest

```python
'assets': {
    'web.assets_backend': [
        'property_custom/static/src/css/multi_select.css',
        'property_custom/static/src/xml/template2.xml',
        
        # Nuevos componentes
        'property_custom/static/src/js/script2.js',
        'property_custom/static/src/js/property_selector.js',
        'property_custom/static/src/js/location_selector.js',
    ],
}
```

---

## 🎯 Crear Acción en XML

```xml
<record id="action_property_selector" model="ir.actions.client">
    <field name="name">Selector de Propiedades</field>
    <field name="tag">property_custom.property_selector</field>
    <field name="context">{}</field>
</record>

<menuitem id="menu_property_selector" 
          name="Seleccionar Propiedades" 
          action="action_property_selector"/>
```

