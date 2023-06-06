from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsWkbTypes,
    QgsFields,
    QgsField,
)

class IntersectionAlgorithm(QgsProcessingAlgorithm):
    INPUT_BUILDINGS = 'INPUT_BUILDINGS'
    INPUT_FRAME = 'INPUT_FRAME'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_BUILDINGS,
            'Buildings',
            types=[QgsProcessing.TypeVectorPolygon]
        ))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_FRAME,
            'Frame',
            types=[QgsProcessing.TypeVectorPolygon]
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            'Output',
            QgsProcessing.TypeVectorPolygon
        ))

    def processAlgorithm(self, parameters, context, feedback):
        # Get input parameters
        buildings_layer = self.parameterAsSource(parameters, self.INPUT_BUILDINGS, context)
        frame_layer = self.parameterAsSource(parameters, self.INPUT_FRAME, context)
        output_sink = self.parameterAsSink(parameters, self.OUTPUT, context,
                                           QgsFields(), QgsWkbTypes.Polygon, frame_layer.sourceCrs())

        # Create output fields
        output_fields = QgsFields()
        output_fields.extend(frame_layer.fields())
        output_fields.append(QgsField('building_id'))

        # # Create output writer
        # output_writer = output_sink.getVectorWriter(output_fields,
        #                                             QgsWkbTypes.Polygon,
        #                                             frame_layer.sourceCrs())

        # Iterate over buildings
        for building_feature in buildings_layer.getFeatures():
            building_geometry = building_feature.geometry()

            # Iterate over frame features and find intersection
            for frame_feature in frame_layer.getFeatures():
                frame_geometry = frame_feature.geometry()
                intersection = building_geometry.intersection(frame_geometry)

                # Write intersection feature to the output layer
                if not intersection.isEmpty() and intersection.isGeosValid():
                    output_feature = QgsFeature(output_fields)
                    output_feature.setGeometry(intersection)
                    output_feature.setAttribute('building_id', building_feature.id())
                    # output_writer.addFeature(output_feature)

        return {self.OUTPUT: output_sink}

    def name(self):
        return 'Intersection Algorithm'

    def displayName(self):
        return self.name()

    def group(self):
        return 'Custom Algorithms'

    def groupId(self):
        return 'custom_algorithms'

    def createInstance(self):
        return IntersectionAlgorithm()
