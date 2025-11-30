from Tabuleiro import Tabuleiro
from sys import exit

class Menu:
    def __init__(self):
        self.opcoes = {
            "1": self.jogar,
            "2": self.sair
        }
        # cria um objeto da classe Tabuleiro e guarda no Menu
        self.tabuleiro_obj = Tabuleiro()

    def printar(self, tabuleiro):
        for l in range(9):
            if l % 3 == 0:
                print("+======+======+======+")
            linha_formatada = ''
            for c in range(9):
                if c % 3 == 0:
                    linha_formatada += '| '
                num = tabuleiro[l][c]
                if num == 0:
                    linha_formatada += '. '
                else:
                    linha_formatada += str(num) + ' '
            linha_formatada += '|'
            print(linha_formatada)
        print("+======+======+======+")

    def jogar(self):
        print(f'{"="*10} MENU {"="*10}')
        print("Dificuldades:")
        print("[1] Fácil  (35 casas vazias)")
        print("[2] Média  (45 casas vazias)")
        print("[3] Difícil (55 casas vazias)")

        escolha = int(input("Dificuldade escolhida: "))

        #garante que foi escolhido uma casa válida 
        if not escolha.isdigit():
            print("Valor inválido.")
            return
        
        escolha = int(escolha)

        if escolha not in [1, 2, 3]:
            print("Escolha inválida!")
            return
        
        # usa o objeto de Tabuleiro guardado em self.tabuleiro_obj
        jogo, certo = self.tabuleiro_obj.gerar_jogo(escolha)

        self.printar(jogo)

        print("Digite a posição a ser prenchida e o número a ser inserido (posições de 1 a 9)")

        while jogo != certo:
            l = int(input("Linha: ")) - 1
            c = int(input("Coluna: ")) - 1
            num = int(input("Número escolhido: "))

            #Verificação
            if not (l.isdigit() and c.isdigit() and num.isdigit()):
                print("Valores inválidos, digite apenas números.")
                continue

            if 0 <= l < 9 and 0 <= c < 9:
                if certo[l][c] == num:
                    jogo[l][c] = num
                else:
                    if jogo[l][c] == 0:
                        print("Número Errado!!")
                    else:
                        print("Posição já prenchida")
            else:
                print("Posição Inexistente!")

            self.printar(jogo)

        print("Vitória!!!")

    def sair(self):
        exit()

    def executar(self):
        while True:
            print("\nMenu:")
            print("1 - Jogar")
            print("2 - Sair")
            
            escolha = input("Escolha uma opção: ")

            acao = self.opcoes.get(escolha)
            if acao:
                acao()
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    menu = Menu()
    menu.executar()