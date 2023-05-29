# -- coding: utf-8 --

"""
/*************************
programacao_aplicada_IME_grupo_1
                                 A QGIS plugin
 Solução do Grupo 1
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-06
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

_author_ = 'Grupo 1'
_date_ = '2023-05-06'
_copyright_ = '(C) 2023 by Grupo 1'

# This will get replaced with a git SHA1 when you do a git archive

_revision_ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingException,
                       QgsWkbTypes,
                       QgsPointXY,
                       QgsSpatialIndex,
                       QgsFeatureSink,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsExpression,
                       QgsVectorLayer,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterVectorLayer,)
import processing


class Project_2(QgsProcessingAlgorithm):
    """
    DESCRIPTION

    This processing algorithm is used to verify hydrography data extracted manually by human operators.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # INPUTS 
    INPUT_DRAINAGES = 'INPUT_DRAINAGES'
    SINK_SPILL_LAYER = 'SINK_SPILL_LAYER'
    WATER_BODY = 'WATER_BODY'
    DITCH_LAYER = 'DITCH_LAYER'
    # OUTPUTS
    POINT_FLAGS = 'POINT_FLAGS'
    LINE_FLAGS = 'LINE_FLAGS'
    POLYGON_FLAGS = 'POLYGON_FLAGS'

    def initAlgorithm(self, config):

        #################################################### INPUTS ####################################################

        # Camadas de entrada do processing: Drenagens; Massas d’água (com fluxo ou sem fluxo, distinção que será feita posteriormente); Sumidouros e Vertedouros; Canal;

        # VectorLines:

        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_DRAINAGES, 'Drenagens', types=[QgsProcessing.TypeVectorLine], defaultValue=None))

        self.addParameter(QgsProcessingParameterVectorLayer(self.DITCH_LAYER, 'Canais', types=[QgsProcessing.TypeVectorLine], defaultValue=None))

        # VectorPolygons:

        self.addParameter(QgsProcessingParameterVectorLayer(self.WATER_BODY, 'Massa de Agua', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))

        # VectorPoints:

        self.addParameter(QgsProcessingParameterVectorLayer(self.SINK_SPILL_LAYER, 'Sumidouros e Vertedouros', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))

        
        #################################################### OUTPUTS ###################################################

        # Saídas: Flags de erro do operador

        # Point flags:
        self.addParameter(QgsProcessingParameterFeatureSink(self.POINT_FLAGS, 'Erros pontuais', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))

        # Line flags:

        self.addParameter(QgsProcessingParameterFeatureSink(self.LINE_FLAGS, 'Erros em linhas', type=QgsProcessing.TypeVectorLine, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))

        # Polygon flags:

        self.addParameter(QgsProcessingParameterFeatureSink(self.POLYGON_FLAGS, 'Erros em polígonos', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        


        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # Armazena as camadas de entrada em variaveis


        ## Drenagens:

        Drain_input = self.parameterAsVectorLayer(parameters, self.INPUT_DRAINAGES, context)
        
        ## Canais:
        
        Ditch_input = self.parameterAsVectorLayer(parameters, self.DITCH_LAYER, context)
        
        ## Massa d'água:

        Water_Body_input = self.parameterAsVectorLayer(parameters, self.WATER_BODY, context)

        ### Separando os casos com e sem fluxo:

        #### Sem fluxo
        
        Wb_no_flow = Water_Body_input.clone()
        
        ##### Definindo o filtro
        
        filter = QgsExpression('possuitrechodrenagem = 0')
        Wb_no_flow.setSubsetString(filter.expression())

        #### Com fluxo:

        Wb_flow = Water_Body_input.clone()

        ##### Definindo o filtro

        filter = QgsExpression('possuitrechodrenagem = 1')
        Wb_flow.setSubsetString(filter.expression())
        
        ### Oceano
        
        Wb_ocean = Water_Body_input.clone()

        ##### Definindo o filtro

        filter = QgsExpression('tipomassadagua = 3')
        Wb_ocean.setSubsetString(filter.expression())

        ## Sumidouros e Vertedouros:

        Sink_spill_input = self.parameterAsVectorLayer(parameters, self.SINK_SPILL_LAYER, context)
        
        ### Sumidouros:
        
        Water_sink = Sink_spill_input.clone()

        ##### Definindo o filtro

        filter = QgsExpression('tiposumvert = 1')
        Water_sink.setSubsetString(filter.expression())

        ### Vertedouro
        Water_spill = Sink_spill_input.clone()
        ##### Definindo o filtro

        filter = QgsExpression('tiposumvert = 2')
        Water_spill.setSubsetString(filter.expression())



        (self.pointFlagSink, self.point_flag_id) = self.prepareAndReturnFlagSink(
            parameters,
            Drain_input,
            QgsWkbTypes.Point,
            context,
            self.POINT_FLAGS
        )
        (self.lineFlagSink, self.line_flag_id) = self.prepareAndReturnFlagSink(
            parameters,
            Drain_input,
            QgsWkbTypes.LineString,
            context,
            self.LINE_FLAGS
        )
        (self.polygonFlagSink, self.polygon_flag_id) = self.prepareAndReturnFlagSink(
            parameters,
            Drain_input,
            QgsWkbTypes.Polygon,
            context,
            self.POLYGON_FLAGS
        )

#####################################################################################################################

###########################################          ALGORITMOS          ############################################

#####################################################################################################################
        
        
        # Algoritmo 1 - Drenagens com fluxo incorreto

        ## O fluxo das drenagens é dado pelo sentido de digitalização da geometria.
        ## Deve existiir coincidência de pontos de início e fim de drenagem
        ## Pontos de início e fim são os ÚNICOS que configuram erro

        ## Procedimento:

        ### 1 - Análise do fluxo de drenagem
        ### 2 - Fragmentação em trechos de drenagem
        ### 3 - Criação de layer temporária 

        # PASSO 1: Análise

        Drain_lyr = processing.run("native:multiparttosingleparts", {
            'INPUT': Drain_input,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }, context=context, feedback=feedback)
        Drain_lyr = Drain_lyr['OUTPUT']

        # PASSO 2: Fragmentação

        subDrain_lyr = processing.run("native:multiparttosingleparts", {
            'INPUT': Drain_lyr,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }, context=context, feedback=feedback)
        subDrain_lyr = subDrain_lyr['OUTPUT']
        

        ## Armazenamento da contagem de ocorrência dos nós por meio de dicionário:

        knot_dict = {}

        ## Subtrechos:

        for subfeat in subDrain_lyr.getFeatures():
            subtrecho = subfeat['id']
            startGeom = subfeat.geometry().asPolyline()[0]
            endGeom = subfeat.geometry().asPolyline()[-1]
            startPoint = (startGeom.x(), startGeom.y())
            endPoint = (endGeom.x(), endGeom.y())

            ## Contagem:

            if startPoint not in knot_dict:
                knot_dict[startPoint] = { "trechos chegando": 0, "trechos saindo": 0, "subtrechos": []}
            
            if endPoint not in knot_dict:
                knot_dict[endPoint] = { "trechos chegando": 0, "trechos saindo": 0, "subtrechos": []}
            
            knot_dict[startPoint]["trechos saindo"] += 1
            knot_dict[endPoint]["trechos chegando"] += 1
            knot_dict[startPoint]["subtrechos"].append(subtrecho)
            knot_dict[endPoint]["subtrechos"].append(subtrecho)

        # Passo 3 - Criação da Layer:
        
        sharedKnots_lyr = QgsVectorLayer("Point?crs=epsg:4674", "Knots_shared", "memory")
        prov = sharedKnots_lyr.dataProvider()
        

        prov.addAttributes([QgsField("erro", QVariant.String)])
        sharedKnots_lyr.updateFields()

        ## Layer dos pontos de drenagem:
        
        subDitch_lyr = processing.run("native:multiparttosingleparts", {
            'INPUT': Ditch_input,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }, context=context, feedback=feedback)
        subDitch_lyr = subDitch_lyr['OUTPUT']

        ## Extração dos vértices iniciais:

        v_ditchs = processing.run("native:extractvertices", {
            'INPUT': subDitch_lyr,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }, context=context, feedback=feedback)
        v_ditchs = v_ditchs['OUTPUT']

        exp_dict = {}
        for ponto, i in knot_dict.items():
            t_in = i['trechos chegando']
            t_out = i['trechos saindo']
            total = t_in + t_out
            erro = ''
            
            ### Testar se o ponto é Sumidouro ou vertedouro
            
            belonging = False
            for feature in Sink_spill_input.getFeatures():
                geom = feature.geometry()
                if geom.type() == QgsWkbTypes.PointGeometry:
                    if geom.isMultipart():
                        # Extract the first point from the MultiPoint geometry
                        point = geom.asMultiPoint()[0]
                    else:
                        # The geometry is already a single point
                        point = geom.asPoint()
                else:
                    raise ValueError("Only Point or MultiPoint geometries are permitted")

                ponto_sink = point
                if (ponto_sink.x(), ponto_sink.y()) == ponto:
                    belonging = True
                    break
            for feature in v_ditchs.getFeatures():
                geom = feature.geometry()
                if geom.type() == QgsWkbTypes.MultiPoint:
                    point = geom.asMultiPoint()[0]
                else:
                    point = geom.asPoint()
                ponto_ditchs = QgsPointXY(point)
                if (ponto_ditchs.x(), ponto_ditchs.y()) == ponto:
                    belonging = True
                    break
            
            if (t_in == 0 and total > 1 and not belonging):
                erro = 'Erro: Divergência'
                exp_dict[ponto] = i['subtrechos']
            elif (t_out == 0 and total > 1 and not belonging):
                erro = 'Erro: Convergência'
                exp_dict[ponto] = i['subtrechos']
        
            if erro != '':

                ### Adicionando os nós

                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(ponto[0], ponto[1])))
                feat.setAttributes([erro])
                prov.addFeatures([feat])

        ## Salvar a camada
        
        sharedKnots_lyr.commitChanges()

        ## Adicionar a flag
        
        flag_txt = 'Drenagens com erro de identificação de fluxo'
        flagLambda = lambda x: self.flagFeature(
        x.geometry(),
        flag_txt=flag_txt,
        sink=self.pointFlagSink
        )
        list(map(flagLambda, sharedKnots_lyr.getFeatures()))
        
##########################################################################################################################################
        
        
        # Algoritmo 2 - Drenagens que iniciam em sumidouro

        count_errors = 0

        for p in Sink_spill_input.getFeatures():
            type = p.attributes()[4]

            if type == 1:
                p_geom = p.geometry()

                for line in Drain_input.getFeatures():
                    l_geom = line.geometry()
                    nome = line.attributes()[1]

                    for part in l_geom.parts():
                        vertices = list(part)
                        initialPoint = QgsGeometry.fromPointXY(QgsPointXY(vertices[0].x(), vertices[0].y()))

                    # Printar qual drenagem se iniciou em sumidouro e contabilizá-la na contagem da mensagem de erro

                        if initialPoint.equals(p_geom):
                            feedback.pushInfo(f"A drenagem {nome} inicia em um sumidouro!")
                            count_errors += 1

        feedback.pushInfo(f"Cuidado! Existem {count_errors} drenagens que estão iniciando em um sumidouro!")


##########################################################################################################################################
        
        
        # Algoritmo 3 - Drenagens que finalizam em vertedouro

        count_errors = 0

        for p in Sink_spill_input.getFeatures():
            type = p.attributes()[4]

            if type == 2:
                p_geom = p.geometry()

                for line in Drain_input.getFeatures():
                    l_geom = line.geometry()
                    nome = line.attributes()[1]

                    for part in l_geom.parts():
                        vertices = list(part)
                        finalPoint = QgsGeometry.fromPointXY(QgsPointXY(vertices[-1].x(), vertices[-1].y()))

                    # Printar qual drenagem se finalizou em vertedouro e contabilizá-la na contagem da mensagem de erro

                        if finalPoint.equals(p_geom):
                            feedback.pushInfo(f"A drenagem {nome} se encerra em um vertedouro!")
                            count_errors += 1

        feedback.pushInfo(f"Cuidado! Existem {count_errors} drenagens que estão se encerrando em um vertedouro!")

##########################################################################################################################################
        
        
        # Algoritmo 4 - Drenagens que iniciam no oceano/baía/enseada

        ## Procedimento:

        ### 1 - Trechos de drenagem serão divididos em linhas
        ### 2 - Criação de layer temporária 

        Drain_lyr = processing.run("native:multiparttosingleparts", {
            'INPUT': Drain_input,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }, context=context, feedback=feedback)
        Drain_lyr = Drain_lyr['OUTPUT']

        #### Extração dos vértices iniciais:
        
        initial_points_lyr = processing.run("native:extractspecificvertices", {
            'INPUT': Drain_lyr,
            'VERTICES': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }, context=context, feedback=feedback)
        initial_points_lyr = initial_points_lyr['OUTPUT']

        #### Armazenamento
        invalid_intersec = processing.run(
            "native:extractbylocation",
            {
                'INPUT': initial_points_lyr,
                'INTERSECT': Wb_ocean,
                'PREDICATE': 0, #Intersects
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            },
            context=context,
            feedback=feedback,
        )
        invalid_intersec = invalid_intersec['OUTPUT']

        #### Armazenamento

        flag_txt = 'Cuidado! Essa drenagem está se iniciando no oceano'

        flag = lambda x: self.flagFeature(
            x.geometry(),
            flag_txt=flag_txt,
            sink=self.pointFlagSink
        )
        list(map(flagLambda, invalid_intersec.getFeatures()))
        teste_alg_4 = list(map(flag, invalid_intersec.getFeatures()))
        
##########################################################################################################################################
        
        
        # Algoritmo 5 - Massa d’água com fluxo sem drenagem interna

        count_errors = 0

        for wb in Water_Body_input.getFeatures():
            flow = wb.attributes()[9]
            name = wb.attributes()[1]

            if flow == True:
                wb_geom = wb.geometry()
                count = 0 

                for l in Drain_input.getFeatures():
                    l_geom = l.geometry()

                    # Se não houver interseção, contabiliza-se erro:

                    if l_geom.crosses(wb_geom): count +=1

                if count == 0:
                    feedback.pushInfo(f"A massa {name} não possui drenagem interna!")
                    count_errors += 1
                    

        feedback.pushInfo(f" Cuidado! Existem {count_errors} massas d'água sem drenagem interna!")




##########################################################################################################################################
        
        
        # Algoritmo 6 - Massa d’água sem fluxo com drenagens internas

        
        invalid_intersec_wb = processing.run(
            "native:extractbylocation",
            {
                'INPUT': Wb_no_flow,
                'INTERSECT': Drain_lyr,
                'PREDICATE': 1, 
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            },
            context=context,
            feedback=feedback,
        )

        invalid_intersec_wb = invalid_intersec_wb['OUTPUT']

        flag_txt = ' Massas d\'água sem fluxo com drenagens internas'
        flag = lambda x: self.flagFeature(
            x.geometry(),
            flag_txt=flag_txt,
            sink=self.polygonFlagSink
        )
        list(map(flag, invalid_intersec_wb.getFeatures()))



##########################################################################################################################################
        
        
        # Algoritmo 7 - Objetos da classe canal linha sem drenagem coincidentes

        invalid_ditch = processing.run(
            "native:extractbylocation",
            {
                'INPUT': Ditch_input,
                'INTERSECT': Drain_lyr,
                'PREDICATE': 2, #Touches
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            },
            context=context,
            feedback=feedback,
        )

        invalid_ditch = invalid_ditch['OUTPUT']

        flagText = 'Objeto da classe Canal linha sem drenagem coincidente.'
        flagLambda = lambda x: self.flagFeature(
            x.geometry(),
            flag_txt=flagText,
            sink=self.lineFlagSink
        )
        list(map(flagLambda, invalid_ditch.getFeatures()))

        

##########################################################################################################################################
        
        
        # Algoritmo 8 - Vertedouros e sumidouros devem estar relacionados com uma drenagem

        count_errors = 0

        for p in Sink_spill_input.getFeatures():
            p_geom = p.geometry()
            name = p.attributes()[1]
            no_error = False

            for line in Drain_input.getFeatures():
                lineGeometry = line.geometry()
                for part in lineGeometry.parts():
                    vertices = list(part)
                    for i in range(len(vertices)-1):
                        point = QgsGeometry.fromPointXY(QgsPointXY(vertices[i].x(), vertices[i].y()))
                        if p_geom.intersects(point): no_error = True

            if no_error:
                feedback.pushInfo(f"O sumidouro ou vertedouro {name} não está relacionado a nenhuma drenagem.")
                count_errors += 1

        feedback.pushInfo(f"Existem {count_errors} vertedouros ou sumidouros sem relacionamento com alguma drenagem!")

        return {
            self.POINT_FLAGS: self.point_flag_id,
            self.LINE_FLAGS: self.line_flag_id,
            self.POLYGON_FLAGS: self.polygon_flag_id,
        }

##########################################################################################################################################


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução do Projeto 2'

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
        return 'Projeto 2'

    def getPointDict(self, pointLyr, idField):
            pointDict = {}
            for feature in pointLyr.getFeatures():
                pointDict[feature[idField]] = feature.geometry().asPoint()
            return pointDict

    def prepareFlagSink(self, parameters, source, wkbType, context):
        (self.flagSink, self.flag_id) = self.prepareAndReturnFlagSink(
            parameters,
            source,
            wkbType,
            context,
            self.FLAGS
            )

    def prepareAndReturnFlagSink(self, parameters, source, wkbType, context, UI_FIELD):
        flagFields = self.getFlagFields()
        (flagSink, flag_id) = self.parameterAsSink(
            parameters,
            UI_FIELD,
            context,
            flagFields,
            wkbType,
            source.sourceCrs() if source is not None else QgsProject.instance().crs()
        )
        if flagSink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, UI_FIELD))
        return (flagSink, flag_id)
    
    def getFlagFields(self):
        fields = QgsFields()
        fields.append(QgsField('Motivo',QVariant.String))
        return fields
    
    def flagFeature(self, flagGeom, flag_txt, sink=None):
        """
        Creates and adds to flagSink a new flag with the reason.
        :param flagGeom: (QgsGeometry) geometry of the flag;
        :param flag_txt: (string) Text of the flag
        """
        flagSink = self.flagSink if sink is None else sink
        newFeat = QgsFeature(self.getFlagFields())
        newFeat['Motivo'] = flag_txt
        newFeat.setGeometry(flagGeom)
        flagSink.addFeature(newFeat, QgsFeatureSink.FastInsert)

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Project_2()
