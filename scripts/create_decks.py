import requests
import json

def create_deck(deck_name):
    url = 'http://localhost:8765'
    payload = json.dumps({
        'action': 'createDeck',
        'version': 6,
        'params': {
            'deck': deck_name
        }
    })
    response = requests.post(url, data=payload)
    return response.json()

def main():
    # Definir a hierarquia dos baralhos e sub-baralhos conforme o padrão solicitado
    decks = []

    # Coletar os nomes dos baralhos do usuário dinamicamente
    while True:
        deck_name = input("Digite o nome do baralho (ou 'sair' para finalizar): ")
        if deck_name.lower() == 'sair':
            break
        decks.append(deck_name)

    # Criar todos os baralhos e sub-baralhos
    for deck in decks:
        print(f"Criando '{deck}'...")
        result = create_deck(deck)
        print(f"Resultado ao criar '{deck}': {result}")

if __name__ == "__main__":
    main()