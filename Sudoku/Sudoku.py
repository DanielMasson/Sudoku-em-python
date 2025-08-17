import random
from copy import deepcopy
def tabuleiro_vazio():
    tabuleiro = [[0 for _ in range(9)]for _ in range(9)]
    return tabuleiro


def achar_vazio(tabuleiro):
    # Acha qual o primeiro espaço vazio que ocorre no jogo
    # se nao acha retorna None para saber que esta totalmente prenchido
    for l in range(9):
        for c in range(9):
            if tabuleiro[l][c] == 0:
                return l, c
    return None

def valido(tabuleiro, linha, coluna, num):
    # Verifica a linha
    for c in range(9):
        if tabuleiro[linha][c] == num:
            return False
    # Verifica a Coluna
    for l in range(9):
        if tabuleiro[l][coluna] == num:
            return False
    # Verifica a matriz 3x3
    # Utiliza divisao inteira para retornar o valor dos blocos, podendo ser 0, 1 ou 2, e apos multiplica para saber onde começa no tabuleiro
    bl = linha // 3 * 3
    bc = coluna // 3 * 3
    for l in range(bl, bl + 3):
        for c in range(bc, bc+ 3):
            if tabuleiro[l][c] == num:
                return False
    return True

    # Prenche o tabuleiro 
def prencher(tabuleiro):
    posicao = achar_vazio(tabuleiro)
    if posicao == None:
        return True
    
    l, c = posicao
    validos = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    random.shuffle(validos)
    i = 0
    while i < 9:
        num = validos[i]
        if valido(tabuleiro, l, c, num):
            tabuleiro[l][c] = num
            if prencher(tabuleiro):
                return True
            tabuleiro[l][c] = 0
        i += 1
    return False


def tabuleiro_completo():
    tabuleiro = tabuleiro_vazio()
    prencher(tabuleiro)
    return tabuleiro


def printar(tabuleiro):
    for l in range(9):
        if l % 3 == 0:
            print("+=======+=======+=====+")
        linha_formatada = ''
        for c in range(9):
            if c % 3 == 0:
                linha_formatada += '|'
            num = tabuleiro[l][c]
            if num == 0:
                linha_formatada += '. '
            else:
                linha_formatada += str(num) + ' '
        linha_formatada += '|'
        print(linha_formatada)
    print("+=======+=======+=====+")

def gerar_jogo(dificuldade):
    solucao = tabuleiro_completo()
    puzzle = deepcopy(solucao)
    if dificuldade.lower() == 'facil':
        removidos = 35
    elif dificuldade.lower() == 'medio':
        removidos = 45
    elif dificuldade.lower() == 'dificil':
        removidos = 55
    else:
        removidos = 5
    
    while removidos > 0:
        l = random.randint(0, 8)
        c = random.randint(0, 8)
        if puzzle[l][c] != 0:
            puzzle[l][c] = 0
            removidos -= 1
        
    return puzzle, solucao


def jogo():
    print(f'{"="*10} MENU {"="*10}')
    print("Dificuldades: Fácil(35 casas em branco); Média(45 casas em branco); Díficil(55 casas em branco)")
    escolha = str(input("Dificuldade escolhida (Sem acentos por favor): "))
    jogo, certo = gerar_jogo(escolha)
    printar(jogo)
    print("Digite a posição a ser prenchida e o numero a ser inserido (posições de 1 a 9)")
    printar(certo)
    while jogo != certo:
        l = int(input("Linha: "))-1
        c = int(input("Coluna: "))-1
        num = int(input("Número escolhido: "))
        if 0 <= l < 10 and 0 <= c < 10:
            if certo[l][c] == num:
                jogo[l][c] = num
            else:
                if jogo[l][c] != 0:
                    print("Número Errado!!")
                else:
                    print("Posição já prenchida")
        else:
            print("Posição Inexistente!")
        printar(jogo)
jogo()
        