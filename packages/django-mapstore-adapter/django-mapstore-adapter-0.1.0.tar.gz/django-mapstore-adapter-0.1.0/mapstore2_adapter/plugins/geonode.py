# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from __future__ import unicode_literals

try:
    import json
except ImportError:
    from django.utils import simplejson as json

import logging
import traceback

from ..utils import (GoogleZoom,
                     get_valid_number,
                     to_json)
from ..settings import (MAP_BASELAYERS,
                        CATALOGUE_SERVICES,
                        CATALOGUE_SELECTED_SERVICE)
from ..converters import BaseMapStore2ConfigConverter

from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


class GeoNodeMapStore2ConfigConverter(BaseMapStore2ConfigConverter):

    def convert(self, viewer, request):
        """
            input: GeoNode JSON Gxp Config
            output: MapStore2 compliant str(config)
        """
        data = {}
        data['version'] = 2
        data['widgetsConfig'] = {}  # TODO

        try:
            viewer_obj = json.loads(viewer)

            # Map Definition
            ms2_map = {}
            ms2_map['projection'] = viewer_obj['map']['projection']
            ms2_map['units'] = viewer_obj['map']['units']
            ms2_map['zoom'] = viewer_obj['map']['zoom']
            ms2_map['maxExtent'] = viewer_obj['map']['maxExtent']
            ms2_map['maxResolution'] = viewer_obj['map']['maxResolution']

            # Backgrouns
            ms2_map['layers'] = MAP_BASELAYERS + [
                # TODO: covnert Viewer Backgroun Layers
                # Add here more backgrounds e.g.:
                # {
                # 	"type": "wms",
                # 	"url": "https://demo.geo-solutions.it/geoserver/wms",
                # 	"visibility": True,
                # 	"opacity": 0.5,
                # 	"title": "Weather data",
                # 	"name": "nurc:Arc_Sample",
                # 	"group": "Meteo",
                # 	"format": "image/png",
                # 	"bbox": {
                # 		"bounds": {
                # 			"minx": -25.6640625,
                # 			"miny": 26.194876675795218,
                # 			"maxx": 48.1640625,
                # 			"maxy": 56.80087831233043
                # 		},
                # 		"crs": "EPSG:4326"
                # 	}
                # }, ...
            ]

            # Overlays
            overlays, selected = self.get_overlays(viewer)

            if selected:
                center, zoom = self.get_center_and_zoom(viewer_obj['map'], selected)
                ms2_map['center'] = center
                ms2_map['zoom'] = zoom
            else:
                ms2_map['center'] = {
                    "x": get_valid_number(viewer_obj['map']['center'][0]),
                    "y": get_valid_number(viewer_obj['map']['center'][1]),
                    "crs": viewer_obj['map']['projection']
                }

            for overlay in overlays:
                ms2_map['layers'].append(overlay)

            data['map'] = ms2_map

            # Catalogue Services Definition
            ms2_catalogue = {}
            ms2_catalogue['selectedService'] = CATALOGUE_SELECTED_SERVICE
            ms2_catalogue['services'] = CATALOGUE_SERVICES

            data['catalogServices'] = ms2_catalogue
        except BaseException:
            # traceback.print_exc()
            tb = traceback.format_exc()
            logger.error(tb)

        return json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True)

    def get_overlays(self, viewer):
        overlays = []
        selected = None
        try:
            viewer_obj = json.loads(viewer)
            layers = viewer_obj['map']['layers']
            sources = viewer_obj['sources']

            for layer in layers:
                if 'group' not in layer or layer['group'] != "background":
                    source = sources[layer['source']]
                    overlay = {}
                    if 'url' in source:
                        overlay['type'] = "wms" if 'ptype' not in source or \
                            source['ptype'] != 'gxp_arcrestsource' else 'arcgis'
                        overlay['url'] = source['url']
                        overlay['visibility'] = layer['visibility'] if 'visibility' in layer else True
                        overlay['opacity'] = layer['opacity'] if 'opacity' in layer else 1.0
                        overlay['title'] = layer['title'] if 'title' in layer else ''
                        overlay['name'] = layer['name'] if 'name' in layer else ''
                        overlay['group'] = layer['group'] if 'group' in layer else ''
                        overlay['format'] = layer['format'] if 'format' in layer else "image/png"

                        overlay['bbox'] = {}
                        if 'capability' in layer:
                            capa = layer['capability']
                            if 'styles' in capa:
                                overlay['styles'] = capa['styles']
                            if 'abstract' in capa:
                                overlay['abstract'] = capa['abstract']
                            if 'attribution' in capa:
                                overlay['attribution'] = capa['attribution']
                            if 'keywords' in capa:
                                overlay['keywords'] = capa['keywords']
                            if 'dimensions' in capa:
                                overlay['dimensions'] = capa['dimensions']
                            if 'llbbox' in capa:
                                overlay['llbbox'] = capa['llbbox']
                            if 'bbox' in capa:
                                bbox = capa['bbox']
                                if viewer_obj['map']['projection'] in bbox:
                                    proj = viewer_obj['map']['projection']
                                    bbox = capa['bbox'][proj]
                                    overlay['bbox']['bounds'] = {
                                        "minx": get_valid_number(bbox['bbox'][0]),
                                        "miny": get_valid_number(bbox['bbox'][1]),
                                        "maxx": get_valid_number(bbox['bbox'][2]),
                                        "maxy": get_valid_number(bbox['bbox'][3])
                                    }
                                    overlay['bbox']['crs'] = bbox['srs']

                        if 'bbox' in layer and not overlay['bbox']:
                            overlay['bbox']['bounds'] = {
                                "minx": get_valid_number(layer['bbox'][0],
                                                         default=layer['bbox'][2],
                                                         complementar=True),
                                "miny": get_valid_number(layer['bbox'][1],
                                                         default=layer['bbox'][3],
                                                         complementar=True),
                                "maxx": get_valid_number(layer['bbox'][2],
                                                         default=layer['bbox'][0],
                                                         complementar=True),
                                "maxy": get_valid_number(layer['bbox'][3],
                                                         default=layer['bbox'][1],
                                                         complementar=True)
                            }
                            overlay['bbox']['crs'] = layer['srs'] if 'srs' in layer else viewer_obj['map']['projection']

                    overlays.append(overlay)
                    if not selected or ('selected' in layer and layer['selected']):
                        selected = overlay
        except BaseException:
            # traceback.print_exc()
            tb = traceback.format_exc()
            logger.error(tb)

        return (overlays, selected)

    def get_center_and_zoom(self, view_map, overlay):
        center = {
            "x": get_valid_number(overlay['bbox']['bounds']['minx'] +
                                  (overlay['bbox']['bounds']['maxx'] -
                                   overlay['bbox']['bounds']['minx']) / 2),
            "y": get_valid_number(overlay['bbox']['bounds']['miny'] +
                                  (overlay['bbox']['bounds']['maxy'] -
                                   overlay['bbox']['bounds']['miny']) / 2),
            "crs": overlay['bbox']['crs']
        }
        zoom = view_map['zoom']
        # max_extent = view_map['maxExtent']
        # map_crs = view_map['projection']
        try:
            ov_bbox = [get_valid_number(overlay['bbox']['bounds']['minx']),
                       get_valid_number(overlay['bbox']['bounds']['miny']),
                       get_valid_number(overlay['bbox']['bounds']['maxx']),
                       get_valid_number(overlay['bbox']['bounds']['maxy']), ]
            ov_crs = overlay['bbox']['crs']
            srid = int(ov_crs.split(':')[1])
            srid = 3857 if srid == 900913 else srid
            poly = Polygon((
                (ov_bbox[0], ov_bbox[1]),
                (ov_bbox[0], ov_bbox[3]),
                (ov_bbox[2], ov_bbox[3]),
                (ov_bbox[2], ov_bbox[1]),
                (ov_bbox[0], ov_bbox[1])), srid=srid)
            gcoord = SpatialReference(4326)
            ycoord = SpatialReference(srid)
            trans = CoordTransform(ycoord, gcoord)
            poly.transform(trans)
            try:
                zoom = GoogleZoom().get_zoom(poly) + 1
            except BaseException:
                center = (0, 0)
                zoom = 0
                # traceback.print_exc()
                tb = traceback.format_exc()
                logger.error(tb)
        except BaseException:
            # traceback.print_exc()
            tb = traceback.format_exc()
            logger.error(tb)

        return (center, zoom)

    def viewer_json(self, viewer, request):
        """
            input: MapStore2 compliant str(config)
            output: GeoNode JSON Gxp Config
        """
        # TODO
        return to_json(viewer)
