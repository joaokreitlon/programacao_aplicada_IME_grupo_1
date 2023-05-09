# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupoX
                                 A QGIS plugin
 Solução do Grupo X
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-20
        copyright            : (C) 2023 by Grupo X
        email                : borba.philipe@ime.eb.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Grupo X'
__date__ = '2023-03-20'
__copyright__ = '(C) 2023 by Grupo X'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)


<<<<<<< Updated upstream
=======
# Definindo a classe Projeto1Solucao que herda da classe QgsProcessingAlgorithm


>>>>>>> Stashed changes
class Projeto1Solucao(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
<<<<<<< Updated upstream
    INPUT = 'INPUT'
=======
    INPUTPOINTS = 'INPUTPOINTS'
    INPUTMDS = 'INPUTMDS'
  # Função para inicializar o algoritmo
>>>>>>> Stashed changes

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )
<<<<<<< Updated upstream
=======
   # Função para criar a camada de pontos

    def create_point_layer(self, points_data: np.ndarray, crs_str: str):
        # Agora, criar os pontos e colocalos no mapa
        memoryLayer = QgsVectorLayer("Point?crs=" + crs_str,
                                     "PontosControle",
                                     "memory")

   # Obtém o provedor de dados da camada
        dp = memoryLayer.dataProvider()
   # Adiciona o atributo 'error' à camada
        # the number 6 represents a double
        dp.addAttributes([QgsField('error', QVariant.nameToType('double'))])
   # Atualiza os campos da camada
        memoryLayer.updateFields()

        # Adicionar as feições de cada um dos pontos
        features = []
        for x, y, err in points_data:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
            feat.setAttributes([abs(float(err))])
            features.append(feat)
        dp.addFeatures(features)
        memoryLayer.updateExtents()

        renderer = QgsGraduatedSymbolRenderer.createRenderer(vlayer=memoryLayer,
                                                             attrName='error',
                                                             classes=5,
                                                             mode=1,
                                                             symbol=QgsSymbol.defaultSymbol(
                                                                 memoryLayer.geometryType()),
                                                             ramp=QgsGradientColorRamp(QColor(255, 255, 255), QColor(255, 0, 0)))

        # Definindo o modo de tamanho para proporcional
        renderer.setSymbolSizes(minSize=1.5, maxSize=5.5)
        memoryLayer.setRenderer(renderer)
        memoryLayer.triggerRepaint()
        return memoryLayer

    def points_layer_para_array(self, points_layer: QgsVectorLayer) -> np.ndarray:
        """
        Pega uma camada vetorial do MDS e transforma ela em um numpy array
        """
        # Obtenha as feições da camada
        features = points_layer.getFeatures()

        # Obtenha as coordenadas XY e os atributos das feições
        xy_attributes = []
        for feature in features:
            attrs = [feature.attribute(attr)
                     for attr in points_layer.fields().names()]
            xy_attributes.append(attrs)

        # Converter a lista de tuplas em um array numpy
        np_array = np.array(xy_attributes)

        # Imprimir a matriz numpy
        return np_array

    def create_coords_finder(self, camada_raster: QgsRasterLayer):
        """
         Essa função cria um objeto que nos permitirar calcular o erro para 
         cada ponto fornecido 
        """
        # Obtenha o provedor de dados da camada
        provider = camada_raster.dataProvider()
        extent = camada_raster.extent()

        # Obtenha a extensão e o tamanho da camada raster
        m = camada_raster.width()
        n = camada_raster.height()
        x0, xf = extent.xMinimum(), extent.xMaximum()
        y0, yf = extent.yMinimum(), extent.yMaximum()
        xres, yres = (xf-x0)/m, (yf-x0)/n

        # Leitura dos dados raster em um buffer
        block = provider.block(1, extent, n, m)
        # Converte o buffer em uma matriz NumPy
        npRaster = np.frombuffer(block.data(), dtype=np.float32).reshape(m, n)

        def coords_finder(coordenates: np.ndarray) -> np.ndarray:
            """ Essa função retorna pontos que estejam junto do mds, com a ultima 
            coluna sendo um atributo de erro """
            output = []
            for line in coordenates:
                x, y, z = line

                if x0 < x < xf and y0 < y < yf:
                    i = int((x-x0)/xres)
                    j = int((y-y0)/yres)
                    output.append([x, y, z - npRaster[j, i]])
                else:
                    continue
            return np.array(output)

        return coords_finder
>>>>>>> Stashed changes

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT, context)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, source.fields(), source.wkbType(), source.sourceCrs())

<<<<<<< Updated upstream
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
=======
        points_layer = self.parameterAsVectorLayer(parameters,
                                                   self.INPUTPOINTS,
                                                   context)

        raster_layer = self.parameterAsRasterLayer(parameters,
                                                   self.INPUTMDS,
                                                   context)
>>>>>>> Stashed changes

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

<<<<<<< Updated upstream
        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
=======
        my_layer = self.create_point_layer(coords,
                                           points_layer.crs().authid())
        # coords = coords_finder(data)
        # (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
        # context,
        # my_layer.fields(),
        # my_layer.wkbType(),
        # my_layer.sourceCrs())

        QgsProject.instance().addMapLayer(my_layer)
        # return {self.OUTPUT: dest_id}
>>>>>>> Stashed changes

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução do Projeto 1'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto1Solucao()
