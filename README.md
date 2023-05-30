# Plugin ```programacao_aplicada_grupo_1```

## Resumo da iniciativa

O trabalho proposto consiste na elaboração de um plugin para o QGIS, no qual serão adicionadas novas features com o decorrer do semestre. As soluções de cada projeto serão implementadas como ferramenta adicional integrante do plugin.

## Projetos:

* **Projeto 1:** [Controle de Qualidade Altimétrico](#proj1)

  * [Solução do problema proposto](#sol)
  * [Solução complementar](#sol_complementar)
  * [Criação do plugin](#plugin)


* **Projeto 2:** [Validação de Hidrografia](#proj2)
  
  * [Solução do problema proposto](#sol_2)
  * [Solução complementar](#sol_complementar_2)

* **Projeto 3:** [Generalização Cartográfica](#proj3)

  * [Solução do problema proposto](#sol_3)
  * [Solução complementar](#sol_complementar_3)

<a name="proj1"></a>

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

<a name="sol"></a>

### Estrutura do Processing da solução

Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto1/solucao.py)

#### Criação das camadas

A partir de um ```IMPUTMDS``` vetorial carregado no QGIS (no caso do exercício, os MDS) e um  ```IMPUTPOINTS``` (os pontos de controle), adicionamos essas feições como camadas: 

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
#### Transformando uma camada vetorial do MDS em um array:

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

#### Cálculo do erro

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
<a name="sol_complementar"></a>

### Solução complementar:
Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto1/solucao_complementar.py)

#### Objetivos:
Calcular o EMQZ entre os MDS adjacentes através da maior área sobreposta entre os TIFFs, de forma a criar uma malha 200m x 200m nos eixos x e y.
Partindo das mesmas bibliotecas que na solução do problema proposto, basta agora criar o processing. Partindo de dois rasters como imputs:

```python

class Projeto1SolucaoComplementar(QgsProcessingAlgorithm):
    
    OUTPUT = 'OUTPUT'
    INPUTRASTER01 = 'INPUTRASTER01'
    INPUTRASTER02 = 'INPUTRASTER02'

def initAlgorithm(self, config):

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
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

```
Analogamente ao problema anterior, vamos adicionar os pontos ao mapa:

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

#### Calculando o erro por ponto fornecido

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

        def coords_finder(coordenates:np.ndarray) -> np.ndarray:
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

#### Encontrando a interseção entre os rasters:

```python

def encontrar_intersercao(self, raster_layer01:QgsRasterLayer, raster_layer02:QgsRasterLayer):
       
        extent = raster_layer01.extent()       
 
        x0, xf = extent.xMinimum(), extent.xMaximum()
        y0, yf = extent.yMinimum(), extent.yMaximum()
        
        provider_2 = raster_layer02.dataProvider()
        
        extent_2 = raster_layer02.extent()
        m_2 = raster_layer02.height()
        n_2 = raster_layer02.width()
        x0_2, xf_2 = extent_2.xMinimum(), extent_2.xMaximum()
        y0_2, yf_2 = extent_2.yMinimum(), extent_2.yMaximum()
        xres_2, yres_2 = (xf_2-x0_2)/n_2, (yf_2-y0_2)/m_2
        block_2 = provider_2.block(1, extent_2, n_2, m_2)
        npRaster_2 = np.frombuffer(block_2.data(), dtype=np.float32).reshape(m_2, n_2)

        x0_int = max(x0,x0_2)
        y0_int = max(y0,y0_2)
        xf_int = min(xf,xf_2)
        yf_int = min(yf,yf_2)

        if not (x0_int < xf_int and y0_int < yf_int):
            return np.array([np.nan])
        
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
        
        coords_finder = self.create_coords_finder(raster_layer01)
        return coords_finder(np.array(points_raster2))
```

Por fim, analogamente ao problema proposto, basta definir o  ```processAlgorithm```, chamando os dois rasters dos MDS:

```python
    
    def processAlgorithm(self, parameters, context, feedback):
        raster_layer01 = self.parameterAsRasterLayer(parameters, 
                                              self.INPUTRASTER01, 
                                              context)

        raster_layer02 = self.parameterAsRasterLayer(parameters, 
                                              self.INPUTRASTER02, 
                                              context)

        pontos_intercesao = self.encontrar_intersercao(raster_layer01, raster_layer02)
        
        instance = QgsProject().instance()
        crs_str = instance.crs().authid()
        output_layer = self.create_point_layer(pontos_intercesao,crs_str)
        instance.addMapLayer(output_layer)
        
    def name(self):
        return 'Solução Complementar do Projeto 1'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto1SolucaoComplementar()

```

<a name="plugin"></a>

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


<a name="proj2"></a>

## Projeto 2: Validação de Hidrografia

### Orientação:
A orientação do trabalho se encontra no [link](https://classroom.google.com/u/1/c/NTkxMTg3ODA0MjI2/a/NTUyODIxNjQ5MzM5/details)

### Objetivos:
Desenvolver um processing que identifica
os seguintes erros de validação nos
dados fornecidos:
1. Drenagens com fluxo incorreto:

• O fluxo das drenagens é dado
pelo sentido de digitalização
da geometria.
• Para cada nó da rede, devem
existir trechos entrando e
saindo (coincidência de
pontos de início e fim de
drenagem).
• Somente pontos de início ou
de fim no meio da rede é erro
(nós no meio da rede em que
só chegam trechos ou só
saem).

2. Drenagens que iniciam em sumidouro;
3. Drenagens que terminam em
vertedouro;
4. Drenagens que iniciam no oceano/
baía/enseada;

5. Massa d’água com
fluxo sem drenagem
interna;

6. Massa d’água sem
fluxo com drenagens
internas;

7. Objetos da classe canal
linhas em drenagem
coincidentes;

8. Vertedouros e sumidouros
devem estar relacionados
com uma drenagem (não
podem existir isoladamente);

<a name="sol_2"></a>

### Estrutura do Processing da solução
Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto2/solucao.py) 

<a name="sol_complementar_2"></a>

### Solução complementar:
Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto2/solucao_complementar.py)

#### Objetivos:
Na etapa de edição, é importante ressaltar
quais drenagens estão dentro de massa
d’água, pois existe uma forma particular de
representar os rótulos destes elementos;

• Sendo assim, é pedido que se desenvolva
um processo que crie um atributo
dentro_de_poligono do tipo booleano e
que se calcule automaticamente o valor
desse atributo para cada trecho de
drenagem.

• São parâmetros de entrada as drenagens
e massas d’água como parâmetros de
entrada;

• A saída do algoritmo deve ter o mesmo
tipo da entrada de drenagens, mesmos
atributos de entrada, acrescidos do
atributo do tipo booleano
dentro_de_poligono;


<a name="proj3"></a>

## Projeto 3: Generalização Cartográfica

### Orientação:
A orientação do trabalho se encontra no [link](https://classroom.google.com/u/1/c/NTkxMTg3ODA0MjI2/a/NTUzNzcxMjY2Mzk3/details)

### Objetivos:
Desenvolver um processing que seja capaz de
deslocar edificações de forma que a
representação de rodovia não atrapalhe a
visibilidade da representação de edificações.

Os inputs são: camada de edificações,
camada de rodovias , distância de
deslocamento.

Os deslocamentos das edificações devem
respeitar a relação entre as edificações e as
rodovias: as edificações que estão à direita da
rodovia devem permanecer à direita, e as
edificações que estão à esquerda das rodovias
devem permanecer à esquerda.

O output deve ser uma camada de geometria
ponto no mesmo CRS da camada de entrada,
com as edificações deslocadas.

<a name="sol_3"></a>

### Estrutura do Processing da solução
Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto3/solucao.py) 


<a name="sol_complementar_3"></a>
### Solução complementar:
Código utilizado: [link](https://github.com/joaokreitlon/programacao_aplicada_IME_grupo_1/blob/main/algorithms/Projeto3/solucao_complementar.py)

### Objetivos:
• Além de deslocar, rotacionar as edificações de modo perpendicular a rodovia mais
próxima;

• Preencher campo rotação em edificação;
