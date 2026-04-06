odoo.define('property_custom.mapbox_init', function (require) {
    'use strict';

    $(document).ready(function () {
        if ($('#map').length){
            if (typeof mapboxgl === 'undefined') return;
            const lat = parseFloat($("#lat").val()) || 0;
            const lng = parseFloat($("#lng").val()) || 0;

            mapboxgl.accessToken = $("#access_token").val();

            const map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/streets-v11',
                center: [lng, lat],
                zoom: 10
            });

            const marker = new mapboxgl.Marker({ draggable: true })
                .setLngLat([lng, lat])
                .addTo(map);

            marker.on('dragend', function () {
                const lngLat = marker.getLngLat();
                console.log(lngLat);
                console.log(lngLat.lat);
                console.log(lngLat.lng);
                $('#lat').val(lngLat.lat);
                $('#lng').val(lngLat.lng);
            });
        }
    });
});
