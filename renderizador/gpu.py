#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Simulador de GPU.

Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
Disciplina: Computação Gráfica
Data: 31 de Agosto de 2020
"""

# Numpy
import numpy as np

# Pillow
from PIL import Image

class FrameBuffer:
    """Organiza objetos FrameBuffer (FrameBuffer Objects)."""

    def __init__(self):
        self.color = np.empty(0)
        self.depth = np.empty(0)


class GPU:
    """Classe que representa o funcionamento de uma GPU."""

    # Constantes a serem usadas com Enum para definir estados
    DRAW_FRAMEBUFFER = 0b01
    READ_FRAMEBUFFER = 0b10
    FRAMEBUFFER = 0b11

    RGB8 = 0b001  # Valores para Vermelho, Verde, Azul de 8bits cada (0-255)
    RGBA8 = 0b010  # Valores para Vermelho, Verde, Azul e Transpareência de 8bits cada (0-255)
    DEPTH_COMPONENT16 = 0b101  # Valores para Profundidade de 16bits cada (0-65535)
    DEPTH_COMPONENT32F = 0b110  # Valores para Profundidade de 32bits em float

    COLOR_ATTACHMENT = 0  # Para FrameBuffer Object identificar memória de imagem de cores
    DEPTH_ATTACHMENT = 1  # Para FrameBuffer Object identificar memória de imagem de profundidade

    # Atributos estáticos
    width = 60
    height = 40
    image_file = None
    frame_buffer = None

    # Legado, deverá ser REMOVIDO
    width = 1
    height = 1

    def __init__(self, image_file):
        """Define o nome do arquivo para caso se salvar o framebuffer."""
        GPU.image_file = image_file

        # Inicia lista para objetos Frame Buffer
        GPU.frame_buffer = []

        # Define buffers de leitura e escrita
        GPU.draw_framebuffer = 0
        GPU.read_framebuffer = 0

        # Cor e profundidade padrão para apagar o FrameBuffer
        GPU.clear_color_val = [0, 0, 0]
        GPU.clear_depth_val = 1.0

    @staticmethod
    def gen_framebuffers(size):
        """Gera posições para FrameBuffers."""
        allocated = []
        for _ in range(size):
            fbo = FrameBuffer()
            GPU.frame_buffer.append(fbo)
            allocated += [len(GPU.frame_buffer)-1]  # informado a posição recem alocada
        return allocated

    @staticmethod
    def bind_framebuffer(buffer, position):
        """Define o framebuffer a ser usado e como."""
        if buffer == GPU.DRAW_FRAMEBUFFER:
            GPU.draw_framebuffer = position
        elif buffer == GPU.READ_FRAMEBUFFER:
            GPU.read_framebuffer = position
        elif buffer == GPU.FRAMEBUFFER:
            GPU.draw_framebuffer = position
            GPU.read_framebuffer = position

    @staticmethod
    def framebuffer_storage(position, attachment, mode, width, height):
        """Aloca o FrameBuffer especificado."""
        if attachment == GPU.COLOR_ATTACHMENT:
            if mode == GPU.RGB8:
                dtype = np.uint8
                depth = 3
            else:  # mode == GPU.RGBA8:
                dtype = np.uint8
                depth = 4
            # Aloca espaço definindo todos os valores como 0 (imagem preta)
            GPU.frame_buffer[position].color = np.zeros((height, width, depth), dtype=dtype)
        elif attachment == GPU.DEPTH_ATTACHMENT:
            if mode == GPU.DEPTH_COMPONENT16:
                dtype = np.uint16
                depth = 1
            else:  # mode == GPU.DEPTH_COMPONENT32F:
                dtype = np.float32
                depth = 1
            # Aloca espaço definindo todos os valores como 1 (profundidade máxima)
            GPU.frame_buffer[position].depth = np.ones((height, width, depth), dtype=dtype)

    @staticmethod
    def clear_color(color):
        """Definindo cor para apagar o FrameBuffer."""
        GPU.clear_color_val = color

    @staticmethod
    def clear_depth(depth):
        """Definindo profundidade para apagar o FrameBuffer."""
        GPU.clear_depth_val = depth

    @staticmethod
    def clear_buffer():
        """Usa o mesmo valor em todo o FrameBuffer, na prática apagando ele."""
        if GPU.frame_buffer[GPU.draw_framebuffer].color.size != 0:
            GPU.frame_buffer[GPU.draw_framebuffer].color[:] = GPU.clear_color_val
        if GPU.frame_buffer[GPU.draw_framebuffer].depth.size != 0:
            GPU.frame_buffer[GPU.draw_framebuffer].depth[:] = GPU.clear_depth_val

    # Obsoleto, parar de usar no futuro
    @staticmethod
    def set_pixel(coord_u, coord_v, clr_r, clr_g, clr_b, clr_a=-1):
        """Troca a cor de um pixel no framebuffer."""
        if clr_a >= 0:  # caso tenha o valor de alpha
            color = [clr_r, clr_g, clr_b, clr_a]
        else:  # caso não tenha o valor de alpha
            color = [clr_r, clr_g, clr_b]
        GPU.frame_buffer[GPU.draw_framebuffer].color[coord_v][coord_u] = color

    # Obsoleto, parar de usar no futuro
    @staticmethod
    def set_depth(coord_u, coord_v, depth):
        """Troca a profundidade de um pixel no framebuffer."""
        GPU.frame_buffer[GPU.draw_framebuffer].depth[coord_v][coord_u] = depth

    @staticmethod
    def draw_pixels(coord, mode, data):
        """Define o valor do pixel no framebuffer."""
        if mode in (GPU.RGB8, GPU.RGBA8):  # cores
            GPU.frame_buffer[GPU.draw_framebuffer].color[coord[1]][coord[0]] = data
        elif mode in (GPU.DEPTH_COMPONENT16, GPU.DEPTH_COMPONENT32F):  # profundidade
            GPU.frame_buffer[GPU.draw_framebuffer].depth[coord[1]][coord[0]] = data

    @staticmethod
    def read_pixels(coord, mode):
        """Retorna o valor do pixel no framebuffer."""
        if mode in (GPU.RGB8, GPU.RGBA8):  # cores
            data = GPU.frame_buffer[GPU.read_framebuffer].color[coord[1]][coord[0]]
        elif mode in (GPU.DEPTH_COMPONENT16, GPU.DEPTH_COMPONENT32F):  # profundidade
            data = GPU.frame_buffer[GPU.read_framebuffer].depth[coord[1]][coord[0]]
        return data

    @staticmethod
    def save_image():
        """Método para salvar a imagem do framebuffer em um arquivo."""
        if GPU.frame_buffer[GPU.read_framebuffer].color.shape[2] == 3:
            img = Image.fromarray(GPU.frame_buffer[GPU.read_framebuffer].color, 'RGB')
        else:
            img = Image.fromarray(GPU.frame_buffer[GPU.read_framebuffer].color, 'RGBA')
        img.save(GPU.image_file)

    @staticmethod
    def load_texture(textura):
        """Método para ler textura."""
        imagem = Image.open(textura)
        matriz = np.array(imagem)
        return matriz

    @staticmethod
    def get_frame_buffer():
        """Retorna o Framebuffer atual para leitura."""
        return GPU.frame_buffer[GPU.read_framebuffer].color

    @staticmethod
    def swap_buffers():
        """Método para a troca dos buffers (NÃO IMPLEMENTADA)."""
