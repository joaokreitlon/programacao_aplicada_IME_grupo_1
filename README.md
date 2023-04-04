# Plugin ```programacao_aplicada_grupo_1```

## Resumo da iniciativa

O trabalho proposto consiste na elaboração de um plugin para o QGIS, no qual serão adicionadas novas features com o decorrer do semestre. As soluções de cada projeto serão implementadas como ferramenta adicional integrante do plugin.

## Projetos:

* **Projeto 1:** [Controle de Qualidade Altimétrico](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/edit/main/README.md#projeto-1-controle-de-qualidade-altim%C3%A9trico)

## Projeto 1: Controle de Qualidade Altimétrico

### Orientação:
A orientação do trabalho se encontra no [link](https://drive.google.com/file/d/1NM3SGzX03Ivp08Ya7gNVz9yaU5UBTaZG/view?usp=drive_web&authuser=3)

### Objetivos:
Realizar a acurácia posicional absoluta altimétrica (EMQz e PEC) de 6 MDS gerados por uma empresa contratada pelo governo do Rio Grande do Sul. 

### Bibliotecas necessárias para importação:

```python
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsFeature, QgsField, QgsGeometry, QgsGradientColorRamp, QgsGraduatedSymbolRenderer, QgsPointXY, QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm, QgsProcessingOutputVectorLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorLayer, QgsProject, QgsRasterLayer, QgsSymbol, QgsVectorLayer)

import numpy as np
```

### Estrutura do Processing da solução

Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto1/solucao.py)

#### Criação das camadas

A partir de um ```python 
IMPUTMDS
``` vetorial carregado no QGIS (no caso do exercício, os MDS) e um  ```IMPUTPOINTS``` (os pontos de controle), adicionamos essas feições como camadas: 

```python

    OUTPUT = 'OUTPUT'
    INPUTPOINTS = 'INPUTPOINTS'
    INPUTMDS = 'INPUTMDS'

    def initAlgorithm(self, config):

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTMDS,
                self.tr('Camada Raster para o MDS'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUTPOINTS,
                self.tr('Camada Vetorial dos Pontos de Controle'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

```

Agora, vamos adicionar uma camada sink para armazenar as features processadas:

```python

self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )


```

Posteriormente, vamos criar os pontos e inseri-los no mapa com tamanho proporcional

```python


def create_point_layer(self, points_data:np.ndarray, crs_str:str):

        memoryLayer = QgsVectorLayer("Point?crs=" + crs_str,
                                     "PontosControle",
                                     "memory")

        dp = memoryLayer.dataProvider()
        dp.addAttributes([QgsField('error', QVariant.nameToType('double'))]) # the number 6 represents a double
        memoryLayer.updateFields()

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

        renderer.setSymbolSizes(minSize=1.5, maxSize=5.5)
        memoryLayer.setRenderer(renderer)
        memoryLayer.triggerRepaint()
        return memoryLayer

```
Transformando uma camada vetorial do MDS em um array:

```python

def points_layer_para_array(self, points_layer:QgsVectorLayer) -> np.ndarray:
    
        features = points_layer.getFeatures()

        xy_attributes = []
        for feature in features:
            attrs = [feature.attribute(attr) for attr in points_layer.fields().names()]
            xy_attributes.append(attrs)
            
        np_array = np.array(xy_attributes)

        return np_array
```

### Cálculo do erro

Ainda dentro do processing, é possível calcular o erro através de:


```python

def create_coords_finder(self, camada_raster:QgsRasterLayer):
      
        provider = camada_raster.dataProvider()
        extent = camada_raster.extent()


        m = camada_raster.width()
        n = camada_raster.height()
        x0, xf = extent.xMinimum(), extent.xMaximum()
        y0, yf = extent.yMinimum(), extent.yMaximum()
        xres, yres = (xf-x0)/m, (yf-x0)/n


        block = provider.block(1, extent, n, m)
        
        npRaster = np.frombuffer(block.data(), dtype=np.float32).reshape(m, n)


```

Agora, vamos criar uma função que retorna os pontos próximos ao MDS, com uma coluna de erro:


```python

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
```

Por fim, basta definir o  ```processAlgorithm```, chamando o ```.csv``` com os pontos de controle e os TIFFs dos MDS:

```python

    def processAlgorithm(self, parameters, context, feedback):

        points_layer = self.parameterAsVectorLayer(parameters, self.INPUTPOINTS, context)
        raster_layer = self.parameterAsRasterLayer(parameters, self.INPUTMDS, context)

        coords_finder = self.create_coords_finder(raster_layer)
        csv_file = '<diretorio>/pontos_controle.csv'

        # data = np.loadtxt(csv_file, delimiter=',', skiprows=1)
        points_array = self.points_layer_para_array(points_layer)
        coords = coords_finder(points_array)

        my_layer = self.create_point_layer(coords, 
                                           points_layer.crs().authid())

        QgsProject.instance().addMapLayer(my_layer)

    def name(self):
        
        return 'Solução do Projeto 1'

    def displayName(self):
    
        return self.tr(self.name())

    def group(self):
    
        return self.tr(self.groupId())

    def groupId(self):
    
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto1Solucao()
```

### Solução complementar:
Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto1/solucao_complementar.py)

### Criação do plugin

O primeiro passo para a criação do plugin é instalar a extensão ```Plugin Builder 3``` no QGIS. A partir daí, é são preenchidos os campos:

<img align="right" src="https://user-images.githubusercontent.com/99846391/229716623-ceaf920a-0bba-4159-b1b4-8e179b933a9d.png" width="500">


```
Class name: ProgramacaoAplicadaGrupo1 

Plugin name: ProgramacaoAplicadaGrupo1

Description: Solução do Grupo 1

Module name: programacao_aplicada_grupo1

Version number: 0.1

Minimum QGIS version: 3.22

Author / Company: Grupo 1

Email: borba.philipe@ime.eb.br
```

Após preenchida a descrição do plugin, basta colocar o template como ```Preocessing Provider``` e posteriormente submeter o link do repositório no campo adequado.   
