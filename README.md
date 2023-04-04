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

### Cálculo da acurácia posicional:
```python
s = "Python syntax highlighting"
print s
# falta colocar o código aqui
```

### Criação das camadas dos pontos de controle

A partir do ```.csv``` fornecido das coordenadas dos pontos de controle, pode-se gerar a camada temporária:

```python
s = "Python syntax highlighting"
print s
# falta colocar o código aqui
```

### Carregamento das camadas temporárias

### Criação do plugin

O primeiro passo para a criação do plugin é instalar a extensão ```Plugin Builder 3``` no QGIS. A partir daí, é são preenchidos os campos:

<img align="right" src="https://user-images.githubusercontent.com/99846391/229716623-ceaf920a-0bba-4159-b1b4-8e179b933a9d.png" width="500">


```
Class name: ProgramacaoAplicadaGrupo1 

Plugin name: ProgramacaoAplicadaGrupo1

Description: Solução do Grupo 1

Module name: programacao_aplicada_grupo1

Version number: 0.11

Minimum QGIS version: 3.22

Author / Company: Grupo 1

Email: borba.philipe@ime.eb.br
```

Após preenchida a descrição do plugin, basta colocar o template como ```Preocessing Provider``` e posteriormente submeter o link do repositório no campo adequado.   
