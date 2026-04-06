# 📚 Explicación del Componente Multi-Select

## 🎯 Estructura General

El componente está dividido en varias partes clave:

---

## 1️⃣ IMPORTACIONES (Líneas 1-5)

```javascript
/** @odoo-module **/
```
- **Qué hace**: Marca el archivo como un módulo de Odoo 19
- **Por qué**: Necesario para que Odoo reconozca el archivo como módulo ES6

```javascript
import { registry } from "@web/core/registry";
```
- **Qué hace**: Importa el sistema de registro de Odoo
- **Para qué**: Registrar tu componente como "acción" que puede ser llamada desde menús

```javascript
import { Component, useState, useRef } from "@odoo/owl";
```
- **Component**: Clase base para crear componentes OWL
- **useState**: Hook para crear estado reactivo (cuando cambia, la vista se actualiza automáticamente)
- **useRef**: Hook para obtener referencia directa a elementos HTML (como el input)

```javascript
import { useService } from "@web/core/utils/hooks";
```
- **Qué hace**: Importa el hook para usar servicios de Odoo
- **Servicios disponibles**: `orm` (base de datos), `notification` (mensajes), `rpc`, `action`, etc.

---

## 2️⃣ SETUP - Inicialización (Líneas 8-23)

```javascript
setup() {
    this.orm = useService("orm");
    this.notification = useService("notification");
    this.inputRef = useRef("searchInput");
```

### **useService("orm")**
- Servicio para interactuar con la base de datos
- Métodos principales:
  - `searchRead(modelo, dominio, campos, opciones)`: Lee registros
  - `create(modelo, valores)`: Crea registros
  - `write(modelo, ids, valores)`: Actualiza registros
  - `unlink(modelo, ids)`: Elimina registros

### **useService("notification")**
- Servicio para mostrar notificaciones al usuario
- Uso: `this.notification.add(mensaje, { type: "success" | "danger" | "info" | "warning" })`

### **useRef("searchInput")**
- Crea referencia al input del template (debe tener `t-ref="searchInput"`)
- Acceso al elemento HTML: `this.inputRef.el`
- Útil para hacer focus, obtener valor, etc.

```javascript
this.state = useState({
    query: "",              // Texto de búsqueda
    options: [],            // Opciones disponibles en el dropdown
    selectedItems: [],      // Items seleccionados (los chips)
    showDropdown: false,    // Mostrar/ocultar dropdown
    isLoading: false,       // Estado de carga
});
```

### **useState(objeto)**
- Hace que el objeto sea **reactivo**
- Cuando cambias `this.state.query = "nuevo"`, la vista se actualiza automáticamente
- IMPORTANTE: Siempre modifica el state directamente, no crees copias

```javascript
this.searchTimeout = null;
this.loadOptions();
```
- `searchTimeout`: Variable para el debounce (evitar muchas búsquedas)
- `loadOptions()`: Carga inicial de datos al abrir el componente

---

## 3️⃣ CARGAR DATOS - loadOptions() (Líneas 25-46)

```javascript
async loadOptions() {
    this.state.isLoading = true;  // Mostrar spinner
```

### **Domain (Filtros Odoo)**
```javascript
const domain = this.state.query
    ? [["name", "ilike", this.state.query]]  // Si hay búsqueda
    : [];  // Sin filtros
```

**Operadores de dominio comunes:**
- `"="` : Igual
- `"!="` : Diferente
- `">"`, `"<"`, `">="`, `"<="` : Comparaciones
- `"ilike"` : Contiene (insensible a mayúsculas)
- `"like"` : Contiene (sensible a mayúsculas)
- `"in"` : Está en la lista
- `"not in"` : No está en la lista

**Ejemplos de dominios:**
```javascript
// Un solo filtro
[["name", "=", "Juan"]]

// Múltiples filtros (AND implícito)
[["name", "ilike", "juan"], ["active", "=", true]]

// OR lógico
["|", ["name", "=", "Juan"], ["name", "=", "Pedro"]]

// Combinado AND/OR
["&", ["active", "=", true], "|", ["type", "=", "Venta"], ["type", "=", "Renta"]]
```

### **searchRead - Leer de la base de datos**
```javascript
const res = await this.orm.searchRead(
    "res.partner",                          // Modelo
    domain,                                 // Filtros
    ["id", "name", "email", "phone"],      // Campos a leer
    { limit: 20 }                          // Opciones
);
```

**Opciones disponibles:**
- `limit`: Máximo de registros
- `offset`: Saltar N registros
- `order`: Ordenamiento ("name ASC", "create_date DESC")
- `context`: Contexto adicional

### **Filtrar ya seleccionados**
```javascript
const selectedIds = this.state.selectedItems.map(item => item.id);
this.state.options = res.filter(opt => !selectedIds.includes(opt.id));
```
- Obtiene los IDs ya seleccionados
- Filtra el resultado para NO mostrar duplicados en el dropdown

### **Manejo de errores**
```javascript
try {
    // código que puede fallar
} catch (error) {
    this.notification.add("Error al cargar", { type: "danger" });
} finally {
    this.state.isLoading = false;  // Siempre ejecuta esto
}
```

---

## 4️⃣ EVENTOS DEL INPUT (Líneas 48-71)

### **onInput - Cuando el usuario escribe**
```javascript
onInput(ev) {
    this.state.query = ev.target.value;  // Guardar texto
    this.state.showDropdown = true;       // Mostrar dropdown
    
    // DEBOUNCE - Evita hacer búsqueda en cada tecla
    clearTimeout(this.searchTimeout);     // Cancela búsqueda anterior
    this.searchTimeout = setTimeout(() => {
        this.loadOptions();               // Busca después de 300ms
    }, 300);
}
```

**¿Por qué debounce?**
- Usuario escribe "Juan Pedro" = 10 caracteres
- Sin debounce = 10 búsquedas en la base de datos
- Con debounce = 1 sola búsqueda (después de dejar de escribir)

### **onFocus - Cuando hace click en el input**
```javascript
onFocus() {
    this.state.showDropdown = true;
    if (this.state.options.length === 0) {
        this.loadOptions();  // Carga inicial si no hay datos
    }
}
```

### **onBlur - Cuando pierde el foco**
```javascript
onBlur() {
    setTimeout(() => {
        this.state.showDropdown = false;
    }, 200);  // Delay de 200ms para permitir clicks en el dropdown
}
```

**¿Por qué el setTimeout?**
- Sin delay: Al hacer click en una opción, el blur cierra el dropdown ANTES del click
- Con delay: Permite que el click se registre antes de cerrar

---

## 5️⃣ SELECCIONAR Y ELIMINAR (Líneas 73-110)

### **selectOption - Agregar item**
```javascript
selectOption(option) {
    this.state.selectedItems.push(option);  // Agregar al array
    this.state.query = "";                  // Limpiar búsqueda
    this.loadOptions();                     // Recargar opciones
    
    this.notification.add(`Agregado: ${option.name}`, { 
        type: "success",
        className: "o_notification_fade"
    });
    
    // Volver a enfocar el input
    if (this.inputRef.el) {
        this.inputRef.el.focus();
    }
}
```

### **removeItem - Eliminar chip**
```javascript
removeItem(item) {
    const index = this.state.selectedItems.findIndex(i => i.id === item.id);
    if (index > -1) {
        this.state.selectedItems.splice(index, 1);  // Eliminar del array
        this.loadOptions();  // Recargar para que aparezca en dropdown
    }
}
```

**Métodos de arrays útiles:**
- `push(item)`: Agregar al final
- `splice(index, 1)`: Eliminar en posición
- `filter(fn)`: Filtrar elementos
- `map(fn)`: Transformar elementos
- `find(fn)`: Encontrar primer elemento
- `findIndex(fn)`: Encontrar posición

---

## 6️⃣ REGISTRO DEL COMPONENTE (Líneas 113-116)

```javascript
WebProperty.template = "property_custom.WebProperty";
```
- Conecta el componente con su template XML
- El template debe tener: `<t t-name="property_custom.WebProperty">`

```javascript
registry.category("actions").add("property_custom.web_property", WebProperty);
```
- Registra el componente en el sistema de acciones de Odoo
- Puede ser llamado desde: `<field name="tag">property_custom.web_property</field>`

---

## 🔄 EJEMPLO: Crear componente para Propiedades

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
        });

        this.searchTimeout = null;
        this.loadOptions();
    }

    async loadOptions() {
        this.state.isLoading = true;
        
        // 🔹 PERSONALIZACIÓN: Dominio para propiedades
        const domain = [
            ["active", "=", true],  // Solo activas
        ];
        
        if (this.state.query) {
            domain.push(["name", "ilike", this.state.query]);
        }
        
        try {
            const res = await this.orm.searchRead(
                "verticali.property",  // 🔹 CAMBIAR MODELO
                domain,
                ["id", "name", "property_id", "type_ope", "zona_id"],  // 🔹 CAMPOS
                { limit: 20, order: "name ASC" }
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
}

PropertySelector.template = "property_custom.PropertySelector";
registry.category("actions").add("property_custom.property_selector", PropertySelector);
```

---

## 📝 CHECKLIST para crear nuevo componente

1. **Copiar el archivo JS** y renombrar la clase
2. **Cambiar el modelo** en `searchRead("MODELO_AQUI")`
3. **Cambiar los campos** que quieres leer
4. **Ajustar el dominio** según tus necesidades
5. **Crear template XML** con el mismo nombre
6. **Registrar** con un nombre único
7. **Agregar al __manifest__.py** en assets
8. **Crear acción XML** con el tag correspondiente

---

## 🎨 Personalización del Template

El template usa las mismas variables del state. Solo necesitas:
- Cambiar `t-name="TU_NOMBRE_AQUI"`
- Ajustar los campos que muestras: `t-esc="opt.CAMPO"`
- Modificar estilos CSS si es necesario

---

## 🚀 Servicios Adicionales Útiles

```javascript
// Router - Navegar
this.router = useService("router");
this.router.pushState({ action: 123 });

// Action - Abrir acciones
this.action = useService("action");
this.action.doAction("nombre.accion");

// RPC - Llamar métodos Python
this.rpc = useService("rpc");
await this.rpc("/mi/ruta", { params });

// Dialog - Mostrar diálogos
this.dialog = useService("dialog");
this.dialog.add(MiComponente, { props });
```

---

## ⚡ Tips de Performance

1. **Siempre usa `limit`** en searchRead
2. **Lee solo campos necesarios** (no uses `[]` para todos)
3. **Usa debounce** en búsquedas
4. **Filtra en el servidor** (dominio) no en JavaScript
5. **Usa `finally`** para limpiar estados (loading, etc.)

---

## 🐛 Debugging

```javascript
// Ver estado actual
console.log("State:", this.state);

// Ver servicios
console.log("ORM:", this.orm);

// Ver errores en try/catch
catch (error) {
    console.error("Error completo:", error);
    this.notification.add(error.message, { type: "danger" });
}
```

