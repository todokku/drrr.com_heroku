import json
from random import randint

############################## - CARREGA O ARQUIVO EM JSON
def carregar_json(arquivo):
    with open(arquivo, 'r') as f:
        return json.load(f)

############################# - FAZ UM PARSE DO JSON PARA OBJETO
json = carregar_json('games_lista.json')

############################ - GERA UM INDEX PARA PEGAR UMA FRASE ALEATÓRIA (MUDAR O VALOR MÁXIMO 5 POR UM OUTRO)
frase_index = randint(0,5)
game_frase = 'game_'+ (str)(frase_index)

######################### - PEGA A FRASE DO OBJETO
frase_secreta = json['games_list'][game_frase]['nome'].lower().strip()
print("A frase secreta é: " + frase_secreta)

#palavra = input("Digite a palavra secreta:").lower().strip()
for x in range(100):
     print()
digitadas = []
acertos = []
erros = 0
while True:
     senha = ""
     for letra in frase_secreta:
         senha += letra if letra in acertos else "."
     print(senha)
     if senha == frase_secreta:
         print("Você acertou!")
         break
     tentativa = input("\nDigite uma letra:").lower().strip()
     if tentativa in digitadas:
         print("Você já tentou esta letra!")
         continue
     else:
         digitadas += tentativa
         if tentativa in frase_secreta:
               acertos += tentativa
         else:
               erros += 1
               print("Você errou!")
     print("X==:==\nX  :   ")
     print("X  O   " if erros >= 1 else "X")
     linha2 = ""
     if erros == 2:
         linha2 = "  |   "
     elif erros == 3:
         linha2 = " \|   "
     elif erros >= 4:
         linha2 = " \|/ "
     print("X%s" % linha2)
     linha3 = ""
     if erros == 5:
         linha3 += " /     "
     elif erros >= 6:
         linha3 += " / \ "
     print("X%s" % linha3)
     print("X\n===========")
     if erros == 6:
         print("Enforcado!")
         break