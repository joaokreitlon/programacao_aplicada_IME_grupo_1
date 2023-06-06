# -*- coding: utf-8 -*-

"""
/*************************
programacao_aplicada_IME_grupo_1
                                 A QGIS plugin
 Solução do Grupo 1
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-06-03
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
from typing import Tuple
import numpy as np
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorLayer,
    QgsProject,
    QgsField,
    QgsFeatureSink,
    QgsCoordinateReferenceSystem,
    QgsRenderContext,
    QgsVectorLayer,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsFeature,
    QgsRaster,
)

from PyQt5.QtCore import QVariant
from qgis.analysis import QgsNativeAlgorithms
from qgis.PyQt.QtCore import QCoreApplication
import processing
from qgis.utils import List, iface

_author_ = "Grupo 1"
_date_ = "2023-06-03"
_copyright_ = "(C) 2023 by Grupo 1"

# This will get replaced with a git SHA1 when you do a git archive

_revision_ = "$Format:%H$"


class Projeto4Solucao(QgsProcessingAlgorithm):
    TARGET_INPUT = "TARGET_INPUT"
    FRAME_INPUT = "FRAME_INPUT"
    SEARCH_DISTANCE = "SEARCH_DISTANCE"
    ERROR_OUTPUT = "ERROR_OUTPUT"

    def initAlgorithm(self, config=None):
        # Inputs
        # Target - Camada vetorial do tipo linha para verificação de erros de ligação.
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TARGET_INPUT, "Camada-alvo", defaultValue=None
            )
        )

        # Frame - Camada vetorial do tipo polígono que delimita a área de verificação de erros.
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.FRAME_INPUT, "Moldura", defaultValue=None
            )
        )

        # Search distance - Distância de busca de feições para verificação de erros.
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SEARCH_DISTANCE,
                "Distância de busca",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.001,
            )
        )

        # Output - Generalized layer with buildings displaced and rotated.
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.ERROR_OUTPUT, "ERROR_OUTPUT")
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Iniciar a camada alvo
        camada_linhas = self.parameterAsVectorLayer(
            parameters, self.TARGET_INPUT, context
        )
        # Coletar todas as pontas dessas camadas
        pontas = coletar_pontas(camada_linhas)

        # Filtrar para reduzir o número de pontos a serem analisados
        moldura = self.parameterAsVectorLayer(parameters, self.FRAME_INPUT, context)
        janela_busca = self.parameterAsDouble(parameters, self.SEARCH_DISTANCE, context)
        regioes_interiores = definir_secoes_interiores(moldura, janela_busca)
        pontos_por_regiao = []
        for regiao in regioes_interiores:
            pontos_por_regiao.append([p for p in pontas if regiao.contains(p[0])])

        # Compar os pontos entre cada regiao e adicionalos na camada de saída
        pontos_com_erro = []
        for i, p_regiao1 in enumerate(pontos_por_regiao[:-1]):
            for p_regiao2 in pontos_por_regiao[i:]:
                for p1, nome1 in p_regiao1:
                    x1, y1 = p1.x, p1.y
                    for p2, nome2 in p_regiao2:
                        x2, y2 = p2.x, p2.y
                        # Se os pontos conterem um erro, basta adicionalos
                        is_disconected = disconnected_geometry(x1, y1, x2, y2, 0)
                        same_name = nome1 == nome2
                        if is_disconected and same_name:
                            pontos_com_erro.append((p1, p2, "geometria_desconectada"))
                        elif not is_disconected and not same_name:
                            pontos_com_erro.append((p1, p2, "atributos_diferentes"))

        # Camada de saída do tipo ponto com campo de "tipo do erro"
        fields = QgsFields()
        fields.append(QgsField("tipo_do_erro", QVariant.String))
        (output_sink, output_dest_id) = self.parameterAsSink(
            parameters, self.ERROR_OUTPUT, context, fields, 1, moldura.sourceCrs()
        )

        # Adicionar a camada de saída
        for p1, p2, erro in pontos_com_erro:
            new_feature = QgsFeature(fields)
            geometria = QgsGeometry.fromPointXY(QgsPointXY(p1.x, p1.y))
            new_feature.setGeometry(geometria)
            new_feature.setAttribute(0, erro)
            output_sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            # Adincionar o segundo ponto também
            new_feature = QgsFeature(fields)
            geometria = QgsGeometry.fromPointXY(QgsPointXY(p2.x, p2.y))
            new_feature.setGeometry(geometria)
            new_feature.setAttribute(0, erro)
            output_sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

        return {self.ERROR_OUTPUT: output_dest_id}

    def name(self):
        return "Solução do Projeto 4"

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return "Projeto 4"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return Projeto4Solucao()


###############################################################################
###############################################################################
###############################################################################


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def sum_points(self, p2):
        return Point(self.x + p2.x, self.y + p2.y)

    def points_dif(self, p2):
        return Point(self.x - p2.x, self.y - p2.y)

    def times_scalar(self, scalar: float):
        return Point(self.x * scalar, self.y * scalar)

    def dot_prod(self, p2):
        return self.x * p2.x + self.y * p2.y

    def project(self, versor):
        dot = self.x * versor.x + self.y * versor.y
        return Point(dot * versor.x, dot * versor.y)

    def module(self):
        return (self.x**2 + self.y**2) ** 0.5

    def normalize(self):
        mod = self.module()
        return Point(self.x / mod, self.y / mod)

    def __str__(self) -> str:
        return f"({self.x:.2f},{self.y:.2f})"

    def __repr__(self) -> str:
        return f"({self.x},{self.y})"


class Box:
    def __init__(self, bbox, u, v) -> None:
        self.u = u
        self.v = v
        self.box = self.bbox_to_box(bbox)

    def contains(self, p: Point) -> bool:
        (c1, c2), (c3, c4) = self.box
        c = p.dot_prod(self.u)
        c_ = p.dot_prod(self.v)
        return (c1 < c < c2) and (c3 < c_ < c4)

    def bbox_to_box(self, bbox: Tuple[Point, Point, Point, Point]):
        p1, p2, p3, _ = bbox
        # para o primeiro segmento de segmento de reta
        c1 = p1.dot_prod(self.u)
        c2 = p3.dot_prod(self.u)
        first = (min(c1, c2), max(c1, c2))
        # Para o segundo
        c3 = p1.dot_prod(self.v)
        c4 = p2.dot_prod(self.v)
        second = (min(c3, c4), max(c3, c4))
        return (first, second)


class SecaoInterior:
    def __init__(self, boxes: List[Box]):
        self.boxes = boxes

    def contains(self, p: Point):
        return any(box.contains(p) for box in self.boxes)


def definir_secoes_interiores(
    multypolygonlyr: QgsVectorLayer, distancia: float
) -> List[SecaoInterior]:
    interior_poligonos = []
    for feature in multypolygonlyr.getFeatures():
        geom = feature.geometry()
        seg_retas = []
        ponto_central = Point(0.0, 0.0)
        boxes = []
        for polygon in geom.asMultiPolygon():
            vertices = polygon[0]
            n = len(vertices)
            for beg, end in zip(vertices[:-1], vertices[1:]):
                seg_retas.append((Point(beg.x(), beg.y()), Point(end.x(), end.y())))
            for vertice in (Point(v.x(), v.y()) for v in vertices):
                ponto_central = ponto_central.sum_points(vertice)
            if n > 0:
                ponto_central = ponto_central.times_scalar(1 / n)
            for beg, end in seg_retas:
                u, v = uv_from_seg_reta(beg, end)
                deslocamento_interior = (
                    ponto_central.points_dif(beg)
                    .project(v)
                    .normalize()
                    .times_scalar(distancia)
                )
                bbox = (
                    beg,
                    beg.sum_points(deslocamento_interior),
                    end,
                    end.sum_points(deslocamento_interior),
                )
                boxes.append(Box(bbox, u, v))
        interior_poligonos.append(SecaoInterior(boxes))
    return interior_poligonos


def uv_from_seg_reta(beg: Point, end: Point) -> Tuple[Point, Point]:
    x0, y0 = beg.x, beg.y
    xf, yf = end.x, end.y
    modulo = ((xf - x0) ** 2 + (yf - y0) ** 2) ** 0.5
    u = Point((xf - x0) / modulo, (yf - y0) / modulo)
    v = Point((yf - y0) / modulo, -(xf - x0) / modulo)
    return (u, v)


def coletar_pontas(corregos: QgsVectorLayer):
    pontos = []
    for feature in corregos.getFeatures():
        geometry = feature.geometry()
        nome = feature["nome"]
        if nome is not None:
            for line in geometry.asMultiPolyline():
                # Pegar os pontos do começo e final
                first_point = line[0]
                last_point = line[-1]
                pontos.append((Point(first_point.x(), first_point.y()), nome))
                pontos.append((Point(last_point.x(), last_point.y()), nome))
    return pontos


def disconnected_geometry(x1, y1, x2, y2, tol):
    p1 = np.array((x1, y1))
    p2 = np.array((x2, y2))
    distance = np.linalg.norm(p1 - p2)

    if 0.0001 > distance > tol:
        return True
    else:
        return False


def different_attributes(nome_feat1, nome_feat2):
    if nome_feat1 != nome_feat2:
        return True
    else:
        return False
