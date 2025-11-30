from random import shuffle, randint
from copy import deepcopy

class Tabuleiro:
    def __init__(self):
        self.tabuleiro = self._tabuleiro_vazio()

    #Métodos internos

    def _tabuleiro_vazio(self):
        return [[0 for _ in range(9)] for _ in range(9)]

    def achar_vazio(self):
        for l in range(9):
            for c in range(9):
                if self.tabuleiro[l][c] == 0:
                    return l, c
        return None

    def _valido(self, linha, coluna, num):
        # checa linha
        for c in range(9):
            if self.tabuleiro[linha][c] == num:
                return False
        # checa coluna
        for l in range(9):
            if self.tabuleiro[l][coluna] == num:
                return False
        # checa bloco 3x3
        bl = (linha // 3) * 3
        bc = (coluna // 3) * 3
        for l in range(bl, bl + 3):
            for c in range(bc, bc + 3):
                if self.tabuleiro[l][c] == num:
                    return False
        return True

    #Sudoku geração

    def _preencher(self):
        posicao = self._achar_vazio()
        if posicao is None:
            return True  # tabuleiro cheio

        l, c = posicao
        numeros = list(range(1, 10))
        shuffle(numeros)

        for num in numeros:
            if self._valido(l, c, num):
                self.tabuleiro[l][c] = num
                if self._preencher():
                    return True
                self.tabuleiro[l][c] = 0

        return False


    def gerar_tabuleiro_completo(self):
        self.tabuleiro = self._tabuleiro_vazio()
        self._preencher()
        return self.tabuleiro

    def gerar_jogo(self, dificuldade):
        solucao = self.gerar_tabuleiro_completo()
        puzzle = deepcopy(solucao)

        #Dificuldades

        if dificuldade == 1:
            removidos = 35
        elif dificuldade == 2:
            removidos = 45
        elif dificuldade == 3:
            removidos = 55
        else:
            removidos = 5

        while removidos > 0:
            l = randint(0, 8)
            c = randint(0, 8)
            if puzzle[l][c] != 0:
                puzzle[l][c] = 0
                removidos -= 1

        return puzzle, solucao
