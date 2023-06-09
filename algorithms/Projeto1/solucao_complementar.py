# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupo1
                                 A QGIS plugin
 Solução do Grupo 1
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-20
        copyright            : (C) 2023 by Grupo 1
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

__author__ = 'Grupo 1'
__date__ = '2023-03-20'
__copyright__ = '(C) 2023 by Grupo 1'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsFeature, QgsField, QgsGeometry, QgsGradientColorRamp, QgsGraduatedSymbolRenderer, QgsPointXY, QgsProcessing,
                       QgsFeatureSink,QgsProcessingParameterRasterLayer,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink, QgsProject, QgsRasterLayer, QgsSymbol, QgsVectorLayer)

import numpy as np


class Projeto1SolucaoComplementar(QgsProcessingAlgorithm):
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
    INPUTRASTER01 = 'INPUTRASTER01'
    INPUTRASTER02 = 'INPUTRASTER02'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRASTER01,
                self.tr('Camada Raster para o primeiro MDS'),
                [QgsProcessing().TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRASTER02,
                self.tr('Camada Raster para o segundo MDS'),
                [QgsProcessing().TypeRaster]
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

    def create_point_layer(self, points_data:np.ndarray, crs_str:str):
        # Agora, criar os pontos e colocalos no mapa
        memoryLayer = QgsVectorLayer("Point?crs=" + crs_str,
                                     "PontosControle",
                                     "memory")

        dp = memoryLayer.dataProvider()
        dp.addAttributes([QgsField('error', QVariant.nameToType('double'))]) # the number 6 represents a double
        memoryLayer.updateFields()

        # Adicionar as feições de cada um dos pontos
        features = []
        for x,y,err in points_data:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
            feat.setAttributes([abs(float(err))])
            features.append(feat)
        dp.addFeatures(features)
        memoryLayer.updateExtents()


        renderer = QgsGraduatedSymbolRenderer.createRenderer(vlayer=memoryLayer,
                                                           attrName='error',
                                                           classes=5,
                                                           mode=1, 
                                                           symbol=QgsSymbol.defaultSymbol(memoryLayer.geometryType()),
                                                           ramp= QgsGradientColorRamp(QColor(255, 255, 255), QColor(255, 0, 0)))

        # set the size mode to proportional
        renderer.setSymbolSizes(minSize=1.5, maxSize=5.5)
        memoryLayer.setRenderer(renderer)
        memoryLayer.triggerRepaint()
        return memoryLayer


    def create_coords_finder(self, camada_raster:QgsRasterLayer):
        """
         Essa função cria um objeto que nos permitirá calcular o erro para 
         cada ponto fornecido 
        """
        # Get the data provider of the layer
        provider = camada_raster.dataProvider()
        extent = camada_raster.extent()

        # Get the extent and size of the raster layer
        m = camada_raster.width()
        n = camada_raster.height()
        x0, xf = extent.xMinimum(), extent.xMaximum()
        y0, yf = extent.yMinimum(), extent.yMaximum()
        xres, yres = (xf-x0)/m, (yf-x0)/n

        # Read the raster data into a buffer
        block = provider.block(1, extent, n, m)
        # Convert the buffer to a NumPy array
        npRaster = np.frombuffer(block.data(), dtype=np.float32).reshape(m, n)

        def coords_finder(coordenates:np.ndarray) -> np.ndarray:
            """ Essa função retorna pontos que estejam junto do mds, com a ultima 
            coluna sendo um atributo de erro """
            output = []
            for line in coordenates:
                x,y,z = line

                if x0 < x < xf and y0 < y < yf:
                    i = int((x-x0)/xres)
                    j = int((y-y0)/yres)
                    output.append([x,y,z - npRaster[j,i]])
                else:
                    continue
            return np.array(output)

        return coords_finder


    def encontrar_intersercao(self, raster_layer01:QgsRasterLayer, raster_layer02:QgsRasterLayer):
        # Encontrar os bounds para ambos os rasteres
        # Get the data provider of the layer
        # provider = raster_layer01.dataProvider()
        extent = raster_layer01.extent()
        # m = raster_layer01.height()
        # n = raster_layer01.width()
        x0, xf = extent.xMinimum(), extent.xMaximum()
        y0, yf = extent.yMinimum(), extent.yMaximum()
        # xres, yres = (xf-x0)/m, (yf-x0)/n
        # block = provider.block(1, extent, n, m)
        # npRaster = np.frombuffer(block.data(), dtype=np.float32).reshape(m, n)

        # Get the extent and size of the raster layer
        provider_2 = raster_layer02.dataProvider()
        extent_2 = raster_layer02.extent()
        m_2 = raster_layer02.height()
        n_2 = raster_layer02.width()
        x0_2, xf_2 = extent_2.xMinimum(), extent_2.xMaximum()
        y0_2, yf_2 = extent_2.yMinimum(), extent_2.yMaximum()
        xres_2, yres_2 = (xf_2-x0_2)/n_2, (yf_2-y0_2)/m_2
        block_2 = provider_2.block(1, extent_2, n_2, m_2)
        npRaster_2 = np.frombuffer(block_2.data(), dtype=np.float32).reshape(m_2, n_2)

        # Achar a intersecao
        x0_int = max(x0,x0_2)
        y0_int = max(y0,y0_2)
        xf_int = min(xf,xf_2)
        yf_int = min(yf,yf_2)

        if not (x0_int < xf_int and y0_int < yf_int):
            return np.array([np.nan])
        
        # Selecionar os pontos do segundo raster que estao na intersecao
        points_raster2 = []
        for j in range(int((x0_int-x0_2)//abs(xres_2)),
                       int((xf_int-x0_2)//abs(xres_2)),
                       int(200/abs(xres_2))):
            x_coord = x0_2 + j*xres_2
            for i in range(int((yf_2-yf_int)//abs(yres_2)),
                           int((yf_2-y0_2)//abs(yres_2)),
                           int(200/abs(yres_2))):
                y_coord = yf_2 - i*abs(yres_2)
                points_raster2.append([x_coord, y_coord, npRaster_2[i,j]])
        
        # Gerar arquivo de erro para o primeiro raster
        coords_finder = self.create_coords_finder(raster_layer01)
        return coords_finder(np.array(points_raster2))


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.

        raster_layer01 = self.parameterAsRasterLayer(parameters, 
                                              self.INPUTRASTER01, 
                                              context)

        raster_layer02 = self.parameterAsRasterLayer(parameters, 
                                              self.INPUTRASTER02, 
                                              context)

        pontos_intercesao = self.encontrar_intersercao(raster_layer01, raster_layer02)

        # Agora, criar os pontos e colocalos no mapa
        instance = QgsProject().instance()
        crs_str = instance.crs().authid()
        output_layer = self.create_point_layer(pontos_intercesao,crs_str)
        instance.addMapLayer(output_layer)

        # return {self.OUTPUT: dest_id}
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução Complementar do Projeto 1'

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
        return Projeto1SolucaoComplementar()

