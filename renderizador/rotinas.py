#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rotinas de operação de nós X3D.

Desenvolvido por:
Disciplina: Computação Gráfica
Data:
"""

import gpu          # Simula os recursos de uma GPU
import math

def CollectPoints(point):
    points = []
    i = 0
    while i < len(point):
        points.append(ponto(point[i], point[i+1]))
        i+= 2
    return points

class ponto(): # Usarei essa classe para facilitar o gerenciamento de pontos (WIP)
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def Info(self):
        print(f"Ponto ({self.x}, {self.y})")

class segmento(): # Classe que representa um segmento, utilizada principalmente para identificar qual lado um ponto esta
    def __init__(self, pontoA, pontoB):
        self.begin = pontoA
        self.end = pontoB
    
    def GetDistance(self):
        return math.abs(math.sqrt((self.end.x - self.begin.x) + (self.end.y - self.begin.y)))

    def GetSign(self, ponto):
        return (ponto.x - self.end.x) * (self.begin.y - self.end.y) - (self.begin.x - self.end.x) * (ponto.y - self.end.y)
    
    def GetAngularCoef(self):
        if(self.end.x == self.begin.x): return 0
        return (self.end.y - self.begin.y)/(self.end.x - self.begin.x)
    
    def GetPixelsStraight(self, pixels, ca):
        passo = 1
        if self.begin.y == self.end.y:
            # Constante em y
            if(self.end.x - self.begin.x < 0):
                passo = -1
            for x in range(int(self.begin.x), int(self.end.x), passo):
                pixels.append(ponto(x, self.begin.y))
        else:
            # Constante em x
            if(self.end.y - self.begin.y < 0):
                passo = -1
            for y in range(int(self.begin.y), int(self.end.y), passo):
                pixels.append(ponto(self.begin.x, y))
            
        return pixels
    
    def GetPixelsWithY(self, pixels, ca):
        ca_x = 1/ca * (abs(ca)/ca)
        x = self.begin.x
        if self.end.y - self.begin.y < 0:
            if ca < 0:
                ca_x = -ca_x
            for y in range(int(self.begin.y), int(self.end.y)-1,-1):
                if not(pixels[-1].x == x and pixels[-1].y == y):
                    pixels.append(ponto(round(x), y))
                x -= ca_x
        else:
            for y in range(int(self.begin.y), int(self.end.y)):
                if not(pixels[-1].x == x and pixels[-1].y == y):
                    pixels.append(ponto(round(x), y))
                x += ca_x
        pixels.append(self.end)
        return pixels
    
    def SpecialCase(self, pixels, ca):
        v = self.begin.y
        if self.end.x - self.begin.x < 0:
            inverted = [self.end]
            for u in range(int(self.begin.x)-1, int(self.end.x), -1):
                if(not(inverted[-1].x == u and inverted[-1].y == round(v))):
                    inverted.append(ponto(u, round(v)))
                v -= ca
            inverted.reverse()
            for i in inverted:
                pixels.append(i)
        else:
            for u in range(int(self.begin.x), int(self.end.x) + 1):
                if(not(pixels[-1].x == u and pixels[-1].y == round(v))):
                    pixels.append(ponto(u, round(v)))
                v += ca
        return pixels
        
    def GetLinePixels(self):            
        ca = self.GetAngularCoef()
        print(f"Coeficiente Angular do ponto {self.begin.x} {self.begin.y} a {self.end.x} {self.end.y} eh {ca}")
        pixels = [self.begin]
        if abs(ca) > 0 and abs(ca) <= 1:
            pixels = self.SpecialCase(pixels, ca)
        elif abs(ca) > 1:
            pixels = self.GetPixelsWithY(pixels, ca)
        else:
            pixels = self.GetPixelsStraight(pixels, ca)
            pass
        return pixels
    
    def Draw(self, color):
        pixels = self.GetLinePixels()
        for p in pixels:
            gpu.GPU.set_pixel(int(p.x), int(p.y), int(color[0]*255),int(color[1]*255) ,int(color[2]*255))
            
    

class triangle():
    """  
    Classe que vai representar um triangulo, os vertices DEVEM ser passados de forma a ser percorrido no sentido anti-horario,
    isso pois a normal ira sempre estar apontando para o lado de fora
    
    """
    def __init__(self, Vertices):
        self.corners = Vertices
        
    def isInside(self, ponto):
        d1 = segmento(self.corners[0], self.corners[1]).GetSign(ponto)
        d2 = segmento(self.corners[1], self.corners[2]).GetSign(ponto)
        d3 = segmento(self.corners[2], self.corners[0]).GetSign(ponto)
        
        
        return  not(((d1 < 0) or (d2 < 0) or (d3 < 0)) and ((d1 > 0) or (d2 > 0) or (d3 > 0)))
    
    def GetSquareCorners(self):
        minx = min(self.corners[0].x,self.corners[1].x,self.corners[2].x)
        maxx = max(self.corners[0].x,self.corners[1].x,self.corners[2].x)
        miny = min(self.corners[0].y,self.corners[1].y,self.corners[2].y)
        maxy = max(self.corners[0].y,self.corners[1].y,self.corners[2].y)
        return int(minx), int(maxx), int(miny), int(maxy)
    
    def Fill(self, color):
        minx, maxx, miny, maxy = self.GetSquareCorners()
        for y in range(miny, maxy):
            for x in range(minx, maxx):
                p = ponto(x,y)
                if(self.isInside(p)):
                    p.Info()
                    gpu.GPU.set_pixel(int(p.x), int(p.y), int(color[0]*255),int(color[1]*255) ,int(color[2]*255))

    def Draw(self, color):
        segmento(self.corners[0], self.corners[1]).Draw(color)
        segmento(self.corners[1], self.corners[2]).Draw(color)
        segmento(self.corners[2], self.corners[0]).Draw(color)
        self.Fill(color)

# web3d.org/documents/specifications/19775-1/V3.0/Part01/components/geometry2D.html#Polypoint2D
def polypoint2D(point, colors):
    """Função usada para renderizar Polypoint2D."""
    # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
    # de pontos x, y sempre na ordem. Assim point[0] é o valor da coordenada x do
    # primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é a
    # coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
    # pelo tamanho da lista e assuma que sempre vira uma quantidade par de valores.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polypoint2D
    # você pode assumir o desenho dos pontos com a cor emissiva (emissiveColor).
    points = CollectPoints(point)
    for p in points:
        gpu.GPU.set_pixel(int(p.x), int(p.y), int(colors["emissiveColor"][0]*255),int(colors["emissiveColor"][1]*255) ,int(colors["emissiveColor"][2]*255))

# web3d.org/documents/specifications/19775-1/V3.0/Part01/components/geometry2D.html#Polyline2D
def polyline2D(lineSegments, colors):
    """Função usada para renderizar Polyline2D."""
    # Nessa função você receberá os pontos de uma linha no parâmetro lineSegments, esses
    # pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o valor da
    # coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto. Já point[2] é
    # a coordenada x do segundo ponto e assim por diante. Assuma a quantidade de pontos
    # pelo tamanho da lista. A quantidade mínima de pontos são 2 (4 valores), porém a
    # função pode receber mais pontos para desenhar vários segmentos. Assuma que sempre
    # vira uma quantidade par de valores.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o Polyline2D
    # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).
    points = CollectPoints(lineSegments)
    i = 0
    while i < len(points):
        segmento(points[i], points[i+1]).Draw(colors["emissiveColor"])
        i+=2

# web3d.org/documents/specifications/19775-1/V3.0/Part01/components/geometry2D.html#TriangleSet2D
def triangleSet2D(vertices, colors):
    """Função usada para renderizar TriangleSet2D."""
    # Nessa função você receberá os vertices de um triângulo no parâmetro vertices,
    # esses pontos são uma lista de pontos x, y sempre na ordem. Assim point[0] é o
    # valor da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto.
    # Já point[2] é a coordenada x do segundo ponto e assim por diante. Assuma que a
    # quantidade de pontos é sempre multiplo de 3, ou seja, 6 valores ou 12 valores, etc.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet2D
    # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).
    vertice_list = CollectPoints(vertices)
    print(vertice_list)
    triangles = []
    i = 0
    while i < len(vertice_list):
        triangles.append(triangle([vertice_list[i], vertice_list[i+1], vertice_list[i+2]]))
        i+= 3
    
    for t in triangles:
        t.Draw(colors["emissiveColor"])

def triangleSet(point, colors):
    """Função usada para renderizar TriangleSet."""
    # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
    # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
    # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
    # assim por diante.
    # No TriangleSet os triângulos são informados individualmente, assim os três
    # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
    # triângulo, e assim por diante.
    # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet
    # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos
    print("TriangleSet : colors = {0}".format(colors)) # imprime no terminal as cores

def viewpoint(position, orientation, fieldOfView):
    """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
    # Na função de viewpoint você receberá a posição, orientação e campo de visão da
    # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
    # perspectiva para poder aplicar nos pontos dos objetos geométricos.

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("Viewpoint : ", end='')
    print("position = {0} ".format(position), end='')
    print("orientation = {0} ".format(orientation), end='')
    print("fieldOfView = {0} ".format(fieldOfView))

def transform_in(translation, scale, rotation):
    """Função usada para renderizar (na verdade coletar os dados) de Transform."""
    # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
    # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
    # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
    # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
    # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
    # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
    # modelos do mundo em alguma estrutura de pilha.

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("Transform : ", end='')
    if translation:
        print("translation = {0} ".format(translation), end='') # imprime no terminal
    if scale:
        print("scale = {0} ".format(scale), end='') # imprime no terminal
    if rotation:
        print("rotation = {0} ".format(rotation), end='') # imprime no terminal
    print("")

def transform_out():
    """Função usada para renderizar (na verdade coletar os dados) de Transform."""
    # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
    # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
    # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
    # pilha implementada.

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("Saindo de Transform")

def triangleStripSet(point, stripCount, colors):
    """Função usada para renderizar TriangleStripSet."""
    # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
    # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
    # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
    # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
    # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
    # em uma lista chamada stripCount (perceba que é uma lista).

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("TriangleStripSet : pontos = {0} ".format(point), end='')
    for i, strip in enumerate(stripCount):
        print("strip[{0}] = {1} ".format(i, strip), end='')
    print("")
    print("TriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores

def indexedTriangleStripSet(point, index, colors):
    """Função usada para renderizar IndexedTriangleStripSet."""
    # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
    # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
    # como conectar os vértices é informada em index, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
    print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores

def box(size, colors):
    """Função usada para renderizar Boxes."""
    # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
    # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
    # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
    # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
    # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
    # encontre os vértices e defina os triângulos.

    # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("Box : size = {0}".format(size)) # imprime no terminal pontos
    print("Box : colors = {0}".format(colors)) # imprime no terminal as cores


def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                   texCoord, texCoordIndex, colors, current_texture):
    """Função usada para renderizar IndexedFaceSet."""
    # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
    # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
    # Você receberá as coordenadas dos pontos no parâmetro cord, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedFaceSet uma lista informando
    # como conectar os vértices é informada em coordIndex, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.
    # Adicionalmente essa implementação do IndexedFace suport cores por vértices, assim
    # a se a flag colorPerVertex estiver habilidades, os vértices também possuirão cores
    # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
    # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
    # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
    # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
    # implementadado um método para a leitura de imagens.

    # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
    print("IndexedFaceSet : ")
    if coord:
        print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex))
    if colorPerVertex:
        print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex))
    if texCoord:
        print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex))
    if current_texture:
        image = gpu.GPU.load_texture(current_texture[0])
        print("\t Matriz com image = {0}".format(image))
    print("IndexedFaceSet : colors = {0}".format(colors)) # imprime no terminal as cores
    print("TriangleSet2D : vertices = {0}".format(vertices)) # imprime no terminal
    print("TriangleSet2D : colors = {0}".format(colors)) # imprime no terminal as cores
    # Exemplo:
    gpu.GPU.set_pixel(24, 8, 255, 255, 0) # altera um pixel da imagem (u, v, r, g, b)