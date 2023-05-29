# -*- coding: utf-8 -*-

"""
/*************************
programacao_aplicada_IME_grupo_1
                                 A QGIS plugin
 Solução Complementar do Grupo 1
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-20
        copyright            : (C) 2023 by Grupo 1
        emails               : joao.pereira@ime.eb.br
                               marcio.santos@ime.eb.br
                               pedro.kovalczuk@ime.eb.br
                               vinicius.magalhaes@ime.eb.br
                            
 *************************/

/*************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *************************/
"""
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsProject,
                       QgsField,
                       QgsFeatureSink,
                       QgsCoordinateReferenceSystem,
                       QgsVectorLayer,
                       QgsFields,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFeature,
                       QgsRaster)

from PyQt5.QtCore import QVariant
from qgis.analysis import QgsNativeAlgorithms
from qgis.PyQt.QtCore import QCoreApplication
import processing
from qgis.utils import iface

_author_ = 'Grupo 1'
_date_ = '2023-05-20'
_copyright_ = '(C) 2023 by Grupo 1'

# This will get replaced with a git SHA1 when you do a git archive

_revision_ = '$Format:%H$'


class Projeto3SolucaoComplementar(QgsProcessingAlgorithm):

    INPUT_BUILDINGS = 'INPUT_BUILDINGS'
    INPUT_ROADS = 'INPUT_ROADS'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        # Inputs

        # Buildings - they will be the focus of cartographic generalization - rotation.
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_BUILDINGS,
                                                              'BUILDINGS', [QgsProcessing.TypeVectorPoint], defaultValue=None))

        # Roads - used to get the direction vector for rotation.
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_ROADS,
                                                              'ROADS', [QgsProcessing.TypeVectorLine], defaultValue=None))

        # Output - Generalized layer with buildings rotated.
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT,
                                                            'GENERALIZED_BUILDINGS'))

    def processAlgorithm(self, parameters, context, feedback):

        # Multiline source
        src_ml = self.parameterAsSource(
            parameters, self.INPUT_MULTILINE, context)

        # Polygon source
        src_poly = self.parameterAsSource(
            parameters, self.INPUT_POLYGON, context)

    def name(self):
        return 'Solução Complementar do Projeto 3'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 3'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto3SolucaoComplementar()
