#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Interface Gráfica para Desenvolver e Usuários.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Button, TextBox, CheckButtons


class Interface:
    """Interface para usuário/desenvolvedor verificar resultados da renderização."""

    pontos = []        # pontos a serem desenhados
    linhas = []        # linhas a serem desenhadas
    poligonos = []     # poligonos a serem desenhados

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.geometrias = []    # lista de geometrias para controlar exibição
        self.grid = False       # usado para controlar se grid exibido ou não

        self.image_saver = None # recebe função para salvar imagens

        self.fig, self.axes = plt.subplots(num="Renderizador")
        self.fig.tight_layout(rect=(0, 0.05, 1, 0.98))

        self.axes.axis([0, width, height, 0])  # [xmin, xmax, ymin, ymax]

        self.axes.xaxis.tick_top()

        # Adaptando número de divisões (ticks) conforme resolução informada
        if max(self.width, self.height) > 400:
            divisions = 100
        elif max(self.width, self.height) > 200:
            divisions = 50
        elif max(self.width, self.height) > 100:
            divisions = 20
        else:
            divisions = 10

        self.axes.xaxis.set_major_locator(MultipleLocator(divisions))
        self.axes.yaxis.set_major_locator(MultipleLocator(divisions))
        self.axes.xaxis.set_minor_locator(MultipleLocator(divisions//10))
        self.axes.yaxis.set_minor_locator(MultipleLocator(divisions//10))

    def annotation(self, points):
        """Desenha texto ao lado dos pontos identificando eles."""
        dist_label = 5 # distância do label para o ponto
        for i, pos in enumerate(points):
            text = self.axes.annotate("P{0}".format(i), xy=pos, xytext=(dist_label, dist_label),
                                      textcoords='offset points', color='lightgray')
            self.geometrias.append(text)

    def draw_points(self, point, text=False):
        """Exibe pontos na tela da interface gráfica."""
        points = point["points"]
        color = point["appearance"].material.emissiveColor

        # converte pontos
        x_values = [pt[0] for pt in points]
        y_values = [pt[1] for pt in points]

        # desenha as linhas com os pontos
        dots, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="")  # "ro"
        self.geometrias.append(dots)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_lines(self, lines, text=False):
        """Exibe linhas na tela da interface gráfica."""
        points = lines["lines"]
        color = lines["appearance"].material.emissiveColor

        # converte pontos
        x_values = [pt[0] for pt in points]
        y_values = [pt[1] for pt in points]

        # desenha as linhas com os pontos
        line, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="-")
        self.geometrias.append(line)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def draw_triangle(self, triangles, text=False):
        """Exibe triângulos na tela da interface gráfica."""
        points = triangles["vertices"]
        color = triangles["appearance"].material.emissiveColor

        # converte pontos
        x_values = [pt[0] for pt in points] + [points[0][0]]
        y_values = [pt[1] for pt in points] + [points[0][1]]

        # desenha as linhas com os pontos
        line, = self.axes.plot(x_values, y_values, marker='o', color=color, linestyle="-")  # "ro-"
        self.geometrias.append(line)

        poly, = self.axes.fill(x_values, y_values, color=color+[0.4])
        self.geometrias.append(poly)

        # desenha texto se requisitado
        if text:
            self.annotation(points)

    def exibe_geometrias_grid(self, label):
        """Exibe e esconde as geometrias/grid sobre a tela da interface gráfica."""
        if label == 'Geometria':
            for geometria in self.geometrias:
                geometria.set_visible(not geometria.get_visible())
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        elif label == 'Grid':
            self.grid = not self.grid
            self.axes.grid(b=self.grid, which='both')
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def set_saver(self, image_saver):
        """Define função para salvar imagens."""
        self.image_saver = image_saver

    def save_image(self, _event):
        """Salva imagens."""
        if self.image_saver:
            print("Salvando imagem")
            self.image_saver()

    def preview(self, data, time):
        """Realização a visualização na tela da interface gráfica."""
        extent = (0, self.width, self.height, 0)
        self.axes.imshow(data, interpolation='nearest', extent=extent)

        for pontos in Interface.pontos:
            self.draw_points(pontos, text=True)

        for linha in Interface.linhas:
            self.draw_lines(linha, text=True)

        for poligono in Interface.poligonos:
            self.draw_triangle(poligono, text=True)

        # Inicialmente deixa todas as geometrias escondidas
        for geometria in self.geometrias:
            geometria.set_visible(False)

        # Configura texto da interface
        axbox = plt.axes([0.18, 0.02, 0.15, 0.06])
        TextBox(axbox, 'Tempo (s) ', initial="{:.4f}".format(time))

        # Configura todos os botões da interface
        bgeogrid = CheckButtons(plt.axes([0.78, 0.02, 0.18, 0.10]), ['Grid', 'Geometria'])
        bgeogrid.on_clicked(self.exibe_geometrias_grid)

        bsave = Button(plt.axes([0.4, 0.02, 0.15, 0.06]), 'Salvar')
        bsave.on_clicked(self.save_image)

        plt.show()
