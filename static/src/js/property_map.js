/** @odoo-module **/
/**
 * Property Map Widget - Embedded Mapbox Map
 * Compatible with Odoo 17+ / 19 OWL architecture.
 *
 * Embeds a Mapbox map directly inside the property form.
 * Users can click/drag to set the property location.
 * Auto-repositions when zipcode compute updates lat/lng.
 * Reverse geocoding auto-fills state, municipality, colony, and zipcode.
 */

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onMounted, onWillUnmount, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const MAPBOX_TOKEN = "pk.eyJ1IjoiYWxleHNhbmNoZXoyOCIsImEiOiJjbWQ0eDd5eXkwNzJkMnZwcHRkNHY5aXdhIn0.rkOiyAbWigTbooUZadY28w";

// Default center: Mexico City
const DEFAULT_LAT = 19.4326;
const DEFAULT_LNG = -99.1332;

export class PropertyMapWidget extends Component {
    static template = "property_custom.PropertyMapWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.mapContainerRef = useRef("mapContainer");

        this.state = useState({
            lat: DEFAULT_LAT,
            lng: DEFAULT_LNG,
            address: "",
            isLoading: false,
            mapLoaded: false,
            searchQuery: "",
        });

        this.map = null;
        this.marker = null;
        this._boundaryLayerAdded = false;
        this._currentBbox = null;  // [west, south, east, north]
        // Track the last known lat/lng to detect changes from compute
        this._lastRecordLat = null;
        this._lastRecordLng = null;

        onMounted(() => {
            this._initMap();
        });

        // Watch for record data changes (e.g. zipcode compute updates lat/lng)
        onPatched(() => {
            this._checkRecordCoordsChanged();
        });

        onWillUnmount(() => {
            if (this.map) {
                this.map.remove();
                this.map = null;
            }
        });
    }

    /**
     * Called after every render. Detects when the server-side compute
     * (triggered by zipcode change) updates latitude/longitude,
     * and auto-repositions the map pin.
     */
    _checkRecordCoordsChanged() {
        if (!this.map || !this.marker) return;

        const record = this.props.record;
        const newLat = parseFloat(record.data.latitude) || 0;
        const newLng = parseFloat(record.data.longitude) || 0;

        if (newLat === 0 && newLng === 0) return;

        const latDiff = Math.abs(newLat - (this._lastRecordLat || 0));
        const lngDiff = Math.abs(newLng - (this._lastRecordLng || 0));

        // Track dropdown administrative location
        const rawZona = record.data.zona_id;
        const rawColony = record.data.colony_id;
        const zonaId = rawZona ? (Array.isArray(rawZona) ? rawZona[0] : (rawZona.id || rawZona)) : null;
        const colId = rawColony ? (Array.isArray(rawColony) ? rawColony[0] : (rawColony.id || rawColony)) : null;

        const coordsChanged = latDiff > 0.00001 || lngDiff > 0.00001;
        // Only consider it a genuine location dropdown change if this is NOT the first initial load/mount
        const isInitialMount = this._lastZonaId === undefined;
        const locationChanged = !isInitialMount && (zonaId !== this._lastZonaId || colId !== this._lastColId);

        if (coordsChanged || isInitialMount || locationChanged) {
            this._lastRecordLat = newLat;
            this._lastRecordLng = newLng;
            this._lastZonaId = zonaId;
            this._lastColId = colId;

            // Update pin if the server gave us new specific coordinates
            if (coordsChanged) {
                this.marker.setLngLat([newLng, newLat]);
                this.map.flyTo({
                    center: [newLng, newLat],
                    zoom: 15,
                    duration: 1500,
                });
                
                this.state.lat = newLat;
                this.state.lng = newLng;
                this.state.address = "";
                
                // Only reverse geocode if user didn't explicitly place the pin themselves (coords changed from backend compute)
                this._reverseGeocode(newLat, newLng, false);
            }

            // Always redraw boundary if dropdown changed directly OR it's the initial page load
            if (locationChanged || isInitialMount) {
                this._showZipcodeBoundary(locationChanged); // Only aggressively fitBounds if dropdown changed explicitly right now
            }
        }
    }

    _getRecordLatLng() {
        const record = this.props.record;
        let lat = parseFloat(record.data.latitude) || 0;
        let lng = parseFloat(record.data.longitude) || 0;
        if (lat === 0 && lng === 0) {
            lat = DEFAULT_LAT;
            lng = DEFAULT_LNG;
        }
        return { lat, lng };
    }

    async _initMap() {
        // Load Mapbox GL JS dynamically if not already loaded
        if (typeof window.mapboxgl === "undefined") {
            await this._loadMapboxScript();
        }

        if (typeof window.mapboxgl === "undefined") {
            console.error("Mapbox GL JS could not be loaded");
            return;
        }

        const { lat, lng } = this._getRecordLatLng();
        this.state.lat = lat;
        this.state.lng = lng;
        this._lastRecordLat = lat;
        this._lastRecordLng = lng;

        window.mapboxgl.accessToken = MAPBOX_TOKEN;

        const container = this.mapContainerRef.el;
        if (!container) return;

        // Retrieve last visual camera state from localStorage to prevent "jump" effect when Odoo remounts on Save
        const resId = this.props.record.resId || "new";
        const savedZoomStr = localStorage.getItem(`property_map_zoom_${resId}`);
        const savedCenterStr = localStorage.getItem(`property_map_center_${resId}`);
        
        let initialZoom = lat !== DEFAULT_LAT ? 15 : 5;
        let initialCenter = [lng, lat];

        // Only restore camera if it was saved natively (meaning user interacted with it on this property)
        if (savedZoomStr) initialZoom = parseFloat(savedZoomStr);
        if (savedCenterStr) {
            try { 
                const parsedCenter = JSON.parse(savedCenterStr);
                if (parsedCenter.length === 2) initialCenter = parsedCenter;
            } catch(e) { }
        }

        this.map = new window.mapboxgl.Map({
            container: container,
            style: "mapbox://styles/mapbox/streets-v12",
            center: initialCenter,
            zoom: initialZoom,
        });

        // Persist camera movements so they survive Odoo's forced reloads
        this.map.on("moveend", () => {
            if (this.props.record.resId) {
                const center = this.map.getCenter().toArray();
                localStorage.setItem(`property_map_center_${this.props.record.resId}`, JSON.stringify(center));
                localStorage.setItem(`property_map_zoom_${this.props.record.resId}`, this.map.getZoom());
            }
        });

        // Add navigation controls
        this.map.addControl(new window.mapboxgl.NavigationControl(), "top-right");

        // Add geolocate control
        this.map.addControl(
            new window.mapboxgl.GeolocateControl({
                positionOptions: { enableHighAccuracy: true },
                trackUserLocation: false,
            })
        );

        // Add marker
        this.marker = new window.mapboxgl.Marker({
            draggable: true,
            color: "#7c3aed",
        })
            .setLngLat([lng, lat])
            .addTo(this.map);

        // On marker drag end — save the final location
        this.marker.on("dragend", async () => {
            let lngLat = this.marker.getLngLat();
            
            this.state.lat = lngLat.lat;
            this.state.lng = lngLat.lng;
            this._lastRecordLat = lngLat.lat;
            this._lastRecordLng = lngLat.lng;
            
            // Synchronously inject high-precision coordinates immediately so Odoo "Save" catches them instantly
            this.props.record.update({ 
                 latitude: String(lngLat.lat), 
                 longitude: String(lngLat.lng) 
            }, { save: false });

            // Asynchronously resolve the POI address name (won't block coordinates from being saved if user hits Save right now)
            await this._reverseGeocode(lngLat.lat, lngLat.lng, true);
        });

        // On map click — place pin and save
        this.map.on("click", async (e) => {
            const { lat, lng } = e.lngLat;
            this.marker.setLngLat([lng, lat]);
            this.state.lat = lat;
            this.state.lng = lng;
            this._lastRecordLat = lat;
            this._lastRecordLng = lng;
            await this._reverseGeocode(lat, lng, true);
        });

        this.state.mapLoaded = true;

        // If already has coords, show address and boundary
        if (lat !== DEFAULT_LAT && lng !== DEFAULT_LNG) {
            this._reverseGeocode(lat, lng, false);
            // Show zip code boundary on initial load but do not force re-center
            this._showZipcodeBoundary(false);
        }
    }

    /**
     * Load Mapbox GL JS + CSS dynamically
     */
    _loadMapboxScript() {
        return new Promise((resolve) => {
            // Load CSS
            if (!document.querySelector('link[href*="mapbox-gl"]')) {
                const link = document.createElement("link");
                link.rel = "stylesheet";
                link.href = "https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css";
                document.head.appendChild(link);
            }

            // Load JS
            if (!document.querySelector('script[src*="mapbox-gl"]')) {
                const script = document.createElement("script");
                script.src = "https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js";
                script.onload = () => setTimeout(resolve, 200);
                script.onerror = () => resolve();
                document.head.appendChild(script);
            } else {
                resolve();
            }
        });
    }

    /**
     * Reverse geocode coordinates to get address details via Mapbox API
     * @param {boolean} saveToRecord - If true, saves location data to DB
     */
    async _reverseGeocode(lat, lng, saveToRecord = true) {
        this.state.isLoading = true;

        try {
            const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${MAPBOX_TOKEN}&language=es&types=address,neighborhood,locality,place,region,postcode,country`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.features && data.features.length > 0) {
                const feature = data.features[0];
                this.state.address = feature.place_name || "";

                if (saveToRecord) {
                    // Extract components from the context
                    const context = feature.context || [];
                    const components = {};

                    for (const ctx of context) {
                        const type = ctx.id.split(".")[0];
                        components[type] = ctx.text;
                        if (ctx.short_code) {
                            components[type + "_code"] = ctx.short_code;
                        }
                    }

                    const mainType = feature.id.split(".")[0];
                    components[mainType] = feature.text;

                    if (feature.properties?.postcode) {
                        components.postcode = feature.properties.postcode;
                    }

                    console.log("Geocode components:", components);
                    await this._saveLocationData(lat, lng, components);
                }
            }
        } catch (error) {
            console.error("Error in reverse geocoding:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Save location data to the property record currently being edited
     * (Updates the frontend data model, requires user to hit "Save" eventually)
     */
    async _saveLocationData(lat, lng, components) {
        const record = this.props.record;
        
        try {
            const updates = {
                latitude: String(lat),
                longitude: String(lng),
            };

            // Optionally auto-fill street if it's completely empty
            if (components.address && !record.data.street) {
                updates.street = components.address;
            }

            // Update the record proxy natively (marks fields dirty so Odoo backend won't easily erase them and avoids wiping unsaved form values)
            await record.update(updates, {
                context: Object.assign({}, this.props.record.context || {}, { skip_geocode: true })
            });

            this.notification.add("📍 Coordenadas ajustadas correctamente en el formulario.", {
                type: "success",
            });

        } catch (error) {
            console.error("Error setting location:", error);
            this.notification.add(
                `Error al aplicar ubicación en el mapa: ${error.message || ""}`,
                { type: "danger" }
            );
        }
    }

    /**
     * Search for an address using Mapbox forward geocoding
     */
    async onSearchAddress() {
        const query = this.state.searchQuery?.trim();
        if (!query) return;

        this.state.isLoading = true;

        try {
            const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${MAPBOX_TOKEN}&language=es&country=mx&limit=1`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.features && data.features.length > 0) {
                const feature = data.features[0];
                const [lng, lat] = feature.center;

                // Move map and marker
                this.map.flyTo({ center: [lng, lat], zoom: 15 });
                this.marker.setLngLat([lng, lat]);
                this.state.lat = lat;
                this.state.lng = lng;
                this._lastRecordLat = lat;
                this._lastRecordLng = lng;

                // Reverse geocode to get full details and save
                await this._reverseGeocode(lat, lng, true);
            } else {
                this.notification.add("No se encontró la dirección.", {
                    type: "warning",
                });
            }
        } catch (error) {
            console.error("Search error:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    onSearchKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.onSearchAddress();
        }
    }

    /**
     * Remove any existing ZIP code boundary layer from the map.
     */
    _removeZipcodeBoundary() {
        if (!this.map) return;
        if (this.map.getLayer('zipcode-boundary-fill')) {
            this.map.removeLayer('zipcode-boundary-fill');
        }
        if (this.map.getLayer('zipcode-boundary-line')) {
            this.map.removeLayer('zipcode-boundary-line');
        }
        if (this.map.getSource('zipcode-boundary')) {
            this.map.removeSource('zipcode-boundary');
        }
        this._boundaryLayerAdded = false;
        this._currentBbox = null;
    }

    /**
     * Fetch the approximate boundary of the current ZIP code and display
     * it as a semi-transparent rectangle/polygon on the map.
     * @param {boolean} shouldFitBounds - Whether to adjust the map zoom to fit
     */
    async _showZipcodeBoundary(shouldFitBounds = false) {
        if (!this.map) {
            console.log('[ZipBoundary] No map instance');
            return;
        }

        const record = this.props.record;
        const colonyData = record.data.colony_id;
        const zonaData = record.data.zona_id;
        const zipcodeData = record.data.zipcode_id;
        
        let colName = '';
        if (colonyData) {
            if (Array.isArray(colonyData)) colName = colonyData[1];
            else if (typeof colonyData === 'object') colName = colonyData.display_name || colonyData.name;
        }

        let zipName = '';
        if (zipcodeData) {
            if (Array.isArray(zipcodeData)) zipName = zipcodeData[1];
            else if (typeof zipcodeData === 'object') zipName = zipcodeData.display_name || zipcodeData.name || (zipcodeData.id && record.displayNames ? record.displayNames[zipcodeData.id] : '');
            else zipName = String(zipcodeData);
        }

        let zonaName = '';
        if (zonaData) {
            if (Array.isArray(zonaData)) zonaName = zonaData[1];
            else if (typeof zonaData === 'object') zonaName = zonaData.display_name || zonaData.name || (zonaData.id && record.displayNames ? record.displayNames[zonaData.id] : '');
        }

        if (!colName && !zipName && !zonaName) {
            console.log('[ZipBoundary] No location data yet for bound restriction.');
            this._removeZipcodeBoundary();
            return;
        }

        try {
            let polygonData = null;
            let boundsData = null;

            try {
                // Determine search query for Nominatim: Use Colonia + Municipio if available, otherwise just Zipcode
                let nomQuery = zipName; // Default
                if (colName && zonaName) {
                    nomQuery = `${colName}, ${zonaName}, Mexico`;
                } else if (colName) {
                    nomQuery = `${colName}, Mexico`;
                } else if (!zipName && zonaName) {
                    nomQuery = `${zonaName}, Mexico`;
                }

                if (!nomQuery) {
                    console.log('[ZipBoundary] No location string to query Nominatim');
                    return;
                }

                console.log('[ZipBoundary] Intentando Nominatim con:', nomQuery);
                // Buscamos con polygon_geojson para obtener la forma real
                const nomUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(nomQuery)}&format=geojson&polygon_geojson=1&limit=1&email=admin@verticali.mx`;
                const nomRes = await fetch(nomUrl);
                const nomData = await nomRes.json();
                
                if (nomData && nomData.features && nomData.features.length > 0) {
                    const feature = nomData.features[0];
                    if (feature.geometry && (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon')) {
                        // Accept Nominatim's geometry even if it's a simple bounding box rectangle
                        polygonData = feature;
                        boundsData = feature.bbox || null;
                    }
                }
            } catch (nomErr) {
                console.warn('[ZipBoundary] OpenStreetMap Nominatim Error:', nomErr);
            }

            // Fallback a Mapbox si Nominatim no devuelve polígono complejo
            if (!polygonData) {
                let mbQuery = zipName;
                if (!mbQuery && colName) mbQuery = colName;
                if (zonaName) mbQuery = `${mbQuery}, ${zonaName}`;

                console.log('[ZipBoundary] Fallback a Mapbox Query:', mbQuery);
                const isPostcodeQuery = mbQuery === zipName && !!zipName;
                const typesParam = isPostcodeQuery ? '&types=postcode' : '';
                const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(mbQuery)}.json?access_token=${MAPBOX_TOKEN}${typesParam}&country=mx&limit=1`;
                const response = await fetch(url);
                const data = await response.json();

                if (data.features && data.features.length > 0) {
                    const feature = data.features[0];
                    const bbox = feature.bbox;

                    if (bbox && bbox.length === 4) {
                        boundsData = bbox; // [west, south, east, north]
                        const [west, south, east, north] = bbox;
                        
                        // Crear cuadrado básico manual (Fallback)
                        polygonData = {
                            type: 'Feature',
                            geometry: {
                                type: 'Polygon',
                                coordinates: [[
                                    [west, south],
                                    [east, south],
                                    [east, north],
                                    [west, north],
                                    [west, south],
                                ]],
                            },
                        };
                    }
                }
            }

            if (polygonData && boundsData) {
                const [west, south, east, north] = boundsData;
                this._currentBbox = boundsData;

                const applyBoundaryLayer = () => {
                    if (!this.map) return;

                    const source = this.map.getSource('zipcode-boundary');
                    if (source) {
                        // Dynamically update polygon data without destructive re-render! Fixes 'refresh' needed bug
                        source.setData(polygonData);
                    } else {
                        this.map.addSource('zipcode-boundary', {
                            type: 'geojson',
                            data: polygonData,
                        });

                        // Standard semi-transparent fill (placed on top for visibility)
                        this.map.addLayer({
                            id: 'zipcode-boundary-fill',
                            type: 'fill',
                            source: 'zipcode-boundary',
                            layout: {},
                            paint: {
                                'fill-color': '#7c3aed',
                                'fill-opacity': 0.25,
                            },
                        });

                        // Solid and bright border
                        this.map.addLayer({
                            id: 'zipcode-boundary-line',
                            type: 'line',
                            source: 'zipcode-boundary',
                            layout: {
                                'line-join': 'round',
                                'line-cap': 'round'
                            },
                            paint: {
                                'line-color': '#5b21b6',
                                'line-width': 3,
                            },
                        });
                    }

                    // Gentle fitBounds and Marker Update
                    if (shouldFitBounds && boundsData) {
                        this.map.fitBounds(
                            [[west, south], [east, north]],
                            { padding: 80, maxZoom: 16, duration: 1500 }
                        );

                        // Only move the pin if the user is explicitly changing the dropdown, OR if the coordinate was absolutely empty/default
                        const currentLat = parseFloat(this.props.record.data.latitude) || 0;
                        if (shouldFitBounds && (currentLat === 0 || currentLat === DEFAULT_LAT)) {
                            const centerY = (south + north) / 2;
                            const centerX = (west + east) / 2;

                            this.marker.setLngLat([centerX, centerY]);
                            this.state.lat = centerY;
                            this.state.lng = centerX;
                            this._lastRecordLat = centerY;
                            this._lastRecordLng = centerX;

                            // Inform Odoo Web Client of the coordinate assignment to fill out empty form
                            this.props.record.update({ latitude: String(centerY), longitude: String(centerX) }, { save: false });
                            
                            // Reverse geolocate to update full street name
                            this._reverseGeocode(centerY, centerX, true);
                        }
                    }
                };

                if (this.map.isStyleLoaded()) {
                    applyBoundaryLayer();
                } else {
                    this.map.once('styledata', applyBoundaryLayer);
                }
            } else {
                this._removeZipcodeBoundary();
            }
        } catch (error) {
            console.warn('[ZipBoundary] Error:', error);
        }
    }
}

// Register as a field widget for Char fields (used on latitude)
registry.category("fields").add("property_map_widget", {
    component: PropertyMapWidget,
    supportedTypes: ["char"],
});
