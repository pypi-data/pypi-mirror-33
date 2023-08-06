(function () {
  function init(params) {
    var settings = {
      template: params.dialog,
      fieldName: params.name,
      sidebar: {
        json: params.json,
        template: params.sidebar,
        suggestions: params.suggestions,
        fieldName: params.id
      },
      map: {
        json: params.json,
        mapping_url: params.country_mapping,
        fieldName: params.id
      },
      basket: {
        json: params.json,
        template: params.basket,
        fieldName: params.id,
        multiline: params.multiline,
        geojson: {
          type: 'FeatureCollection',
          features: []
        }
      }
    };

    return function run() {
      if (params.geojson.features) {
        settings.basket.geojson = params.geojson;
      }

      // Initialize popup
      var geo = jQuery('#' + params.id).geodialog(settings);
      jQuery('#' + params.id + '-edit').click(function () {
        geo.dialog('open');
      });

      // Display map
      jQuery('#' + params.id + '-geopreview').geopreview({
        fieldName: params.id,
        json: params.geojson
      });
    };

  }

  // make available on window
  window.eea_geotags = window.eea_geotags || {
    init: init
  };

})();
