/** @odoo-module **/
/**
 * Property Image Drag-and-Drop Upload Widget
 * Compatible with Odoo 17+ / 19 OWL architecture.
 *
 * Provides a dropzone component that allows users to drag-and-drop
 * image files directly onto the property form to upload them.
 * Also integrates with the FormController to handle drops anywhere on the form.
 */

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class PropertyImageDropzone extends Component {
    static template = "property_custom.PropertyImageDropzone";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dropzoneRef = useRef("dropzone");
        this.fileInputRef = useRef("fileInput");

        this.state = useState({
            isDragOver: false,
            isUploading: false,
            uploadProgress: 0,
            previewImages: [],
        });

        onMounted(() => {
            // Add form-level drag listeners
            const formEl = this.dropzoneRef.el?.closest(".o_form_view");
            if (formEl) {
                this._formEl = formEl;
                formEl.addEventListener("dragover", this._onFormDragOver.bind(this));
                formEl.addEventListener("drop", this._onFormDrop.bind(this));
                formEl.addEventListener("dragleave", this._onFormDragLeave.bind(this));
            }
        });

        onWillUnmount(() => {
            if (this._formEl) {
                this._formEl.removeEventListener("dragover", this._onFormDragOver);
                this._formEl.removeEventListener("drop", this._onFormDrop);
                this._formEl.removeEventListener("dragleave", this._onFormDragLeave);
            }
        });
    }

    // ── Form-level drag handlers (intercept drops anywhere on the form) ──

    _onFormDragOver(ev) {
        // Only intercept if carrying files
        if (ev.dataTransfer?.types?.includes("Files")) {
            ev.preventDefault();
            ev.stopPropagation();
            this.state.isDragOver = true;
        }
    }

    _onFormDragLeave(ev) {
        // Only deactivate if truly leaving the form
        if (!ev.relatedTarget || !this._formEl?.contains(ev.relatedTarget)) {
            this.state.isDragOver = false;
        }
    }

    _onFormDrop(ev) {
        if (ev.dataTransfer?.types?.includes("Files")) {
            ev.preventDefault();
            ev.stopPropagation();
            this.state.isDragOver = false;
            const files = ev.dataTransfer.files;
            if (files.length > 0) {
                this._processFiles(files);
            }
        }
    }

    // ── Dropzone-specific handlers ──

    onDragOver(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.state.isDragOver = true;
    }

    onDragLeave(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.state.isDragOver = false;
    }

    onDrop(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.state.isDragOver = false;
        const files = ev.dataTransfer?.files;
        if (files && files.length > 0) {
            this._processFiles(files);
        }
    }

    onClickDropzone() {
        this.fileInputRef.el?.click();
    }

    onFileChange(ev) {
        const files = ev.target.files;
        if (files && files.length > 0) {
            this._processFiles(files);
        }
        // Reset file input so the same file can be selected again
        ev.target.value = "";
    }

    // ── File Processing ──

    async _processFiles(files) {
        const imageFiles = Array.from(files).filter((f) =>
            f.type.startsWith("image/")
        );

        if (imageFiles.length === 0) {
            this.notification.add("Solo se permiten archivos de imagen (JPG, PNG, etc.)", {
                type: "warning",
            });
            return;
        }

        // Get the property record ID
        const record = this.props.record;
        const propertyId = record?.resId;

        if (!propertyId) {
            this.notification.add(
                "Guarda la propiedad primero antes de subir imágenes.",
                { type: "warning" }
            );
            return;
        }

        this.state.isUploading = true;
        this.state.uploadProgress = 0;

        let uploadedCount = 0;
        let failedCount = 0;
        const total = imageFiles.length;

        // Upload ONE image at a time, sequentially, with pause between each
        for (let i = 0; i < total; i++) {
            const file = imageFiles[i];
            this.state.uploadProgress = Math.round((i / total) * 100);

            try {
                // 1. Read file as base64 (client-side)
                const base64 = await this._readFileAsBase64(file);

                // 2. Upload this single image to the server
                await this.orm.create("verticali.property.image", [{
                    name: file.name.replace(/\.[^/.]+$/, ""),
                    image: base64,
                    property_id: propertyId,
                    sequence: (i + 1) * 10,
                }]);

                uploadedCount++;

                // 3. Wait 500ms before next upload to let the server breathe
                if (i < total - 1) {
                    await new Promise((r) => setTimeout(r, 500));
                }
            } catch (error) {
                console.error(`Error uploading ${file.name}:`, error);
                failedCount++;

                // Wait a bit longer on error before retrying next image
                await new Promise((r) => setTimeout(r, 1000));
            }
        }

        this.state.uploadProgress = 100;
        this.state.isUploading = false;

        // Show result notification
        if (uploadedCount > 0) {
            let msg = `✅ ${uploadedCount} de ${total} imagen(es) subida(s) correctamente.`;
            if (failedCount > 0) {
                msg += ` (${failedCount} fallaron)`;
            }
            this.notification.add(msg, {
                type: failedCount > 0 ? "warning" : "success",
            });
            // Reload the record to refresh image_ids
            await record.load();
        } else {
            this.notification.add(
                "No se pudo subir ninguna imagen. Verifica tu conexión e intenta de nuevo.",
                { type: "danger" }
            );
        }

        this.state.uploadProgress = 0;
    }

    /**
     * Read a File object and return its base64 content (without the data URL prefix).
     */
    _readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const base64 = e.target.result.split(",")[1];
                resolve(base64);
            };
            reader.onerror = () => reject(new Error(`No se pudo leer: ${file.name}`));
            reader.readAsDataURL(file);
        });
    }
}

// Register as a field widget
registry.category("fields").add("property_image_dropzone", {
    component: PropertyImageDropzone,
    supportedTypes: ["one2many"],
});
