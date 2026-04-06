/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";

export class CustomAction extends Component {
    setup() {
        onMounted(() => {
            // Espera que Select2 esté cargado globalmente (sin jQuery)
            if (typeof window.Select2 === "undefined" && typeof $ === "undefined") {
                console.error("⚠️ Select2 no está disponible.");
                return;
            }

            // Usa la API moderna (sin $)
            const selects = document.querySelectorAll(".select2");
            selects.forEach(select => {
                if (typeof $ !== "undefined" && $.fn.select2) {
                    // Si jQuery existe (por compatibilidad)
                    $(select).select2({ width: "100%", placeholder: "Selecciona" });
                } else if (window.Select2) {
                    // Si no hay jQuery, inicializa con la API moderna
                    new window.Select2(select, { width: "100%" });
                }
            });
        });
    }
}

CustomAction.template = "property_custom.PropertyTemplate";
