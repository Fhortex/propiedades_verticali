odoo.define('property_custom.input_mask_widget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var InputMask = require('web.dom_input_mask');

    var InputMaskWidget = AbstractField.extend({
        // template: 'InputMaskField', // Esto es opcional si no usas template
        events: {
            'input': '_onInput',
        },

        init: function () {
            this._super.apply(this, arguments);
        },

        start: function () {
            this._super.apply(this, arguments);
            this._applyInputMask();
        },

        _applyInputMask: function () {
            if (this.field.attrs.input_mask) {
                var mask = this.field.attrs.input_mask;
                InputMask.mask(this.$el, mask);
            }
        },

        _onInput: function (event) {
            // Puedes manejar el evento 'input' si necesitas algo cuando cambie el valor
            this._setValueFromDOM();
        }
    });

    core.form_widget_registry.add('input_mask_widget', InputMaskWidget);
});
