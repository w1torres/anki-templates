import json
import requests

def invoke(action, **params):
    """Envia uma solicitação ao AnkiConnect."""
    response = requests.post('http://localhost:8765', json={
        'action': action,
        'version': 6,
        'params': params
    }).json()
    return response

def import_cards_to_anki(file_path):
    """Importa cartões para o Anki a partir de um arquivo .txt."""
    deck_name = input("Digite o nome do baralho onde os cartões serão adicionados: ")

    # Verificar se o baralho já existe, caso contrário, criá-lo
    response = invoke('createDeck', deck=deck_name)
    if response.get('error'):
        print(f"Erro ao criar o baralho: {response['error']}")
        return

    # Ler e processar o arquivo .txt
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Ignorar linhas em branco ou comentários

            # Dividir a linha em campos usando a tabulação como delimitador
            fields = line.split('\t')

            # Identifica o tipo de nota 
            notetype = fields[0].strip()

            # Processar para notas de Múltipla Escolha
            if notetype == "Multipla Escolha":
                if len(fields) < 7:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada: {line}")
                    continue
                
                # Extrair os campos do cartão
                question = fields[1].strip()
                option_1 = fields[2].strip()
                option_2 = fields[3].strip()
                option_3 = fields[4].strip()
                option_4 = fields[5].strip()
                option_5 = fields[6].strip()
                answer = fields[7].strip()

                if not (question and answer):
                    print(f"Cartão com campos necessários ausentes. Linha ignorada: {line}")
                    continue

                note = {
                    "deckName": deck_name,
                    "modelName": notetype,  # Nome do tipo da nota fornecido no arquivo .txt
                    "fields": {
                        "Pergunta": question,
                        "option_1": option_1,
                        "option_2": option_2,
                        "option_3": option_3,
                        "option_4": option_4,
                        "option_5": option_5,
                        "Resposta": answer
                    },
                    "tags": []
                }

            # Processar para notas de Certo ou Errado
            elif notetype == "Certo ou Errado":
                if len(fields) < 3:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada: {line}")
                    continue
                
                # Extrair os campos do cartão
                question = fields[1].strip()
                answer = fields[2].strip()
                correct_answer = fields[3].strip()
                
                if not question or not answer or not correct_answer:
                    print(f"Cartão com campos necessários ausentes. Linha ignorada: {line}")
                    continue

                note = {
                    "deckName": deck_name,
                    "modelName": notetype,  # Nome do tipo da nota fornecido no arquivo .txt
                    "fields": {
                        "Pergunta": question,
                        "Resposta": answer,
                        "Resposta Certa": correct_answer
                    },
                    "tags": []
                }

            elif notetype == "Ordenar":
                print(f'{len(fields)}')
                if len(fields) < 3:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada.")
                    continue
                
                question = fields[1].strip() 
                option_1 = fields[2].strip()
                option_2 = fields[3].strip() 
                option_3 = fields[4].strip() if len(fields) > 4 else ""
                option_4 = fields[5].strip() if len(fields) > 5 else ""
                option_5 = fields[6].strip() if len(fields) > 6 else ""

                if not question:
                    print(f"Cartão com campos necessários ausentes.")
                    return None

                note = {
                    "deckName": deck_name,
                    "modelName": notetype,
                    "fields": {
                        "Pergunta": question,
                        "option_1": option_1,
                        "option_2": option_2,
                        "option_3": option_3,
                        "option_4": option_4,
                        "option_5": option_5
                    },
                    "tags": []
                }

            elif notetype == "Relacione as Colunas":
                if len(fields) < 12:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada: {line}")
                    return None

                question = fields[1].strip()
                item_1_left = fields[2].strip()
                item_2_left = fields[3].strip()
                item_3_left = fields[4].strip()
                item_4_left = fields[5].strip()
                item_5_left = fields[6].strip()
                option_1 = fields[7].strip()
                option_2 = fields[8].strip()
                option_3 = fields[9].strip()
                option_4 = fields[10].strip()
                option_5 = fields[11].strip()

                if not question:
                    print(f"Cartão com campos necessários ausentes. Linha ignorada: {option_5}")
                    return None

                note =  {
                    "deckName": deck_name,
                    "modelName": notetype,
                    "fields": {
                        "Pergunta": question,
                        "item_1_left": item_1_left,
                        "item_2_left": item_2_left,
                        "item_3_left": item_3_left,
                        "item_4_left": item_4_left,
                        "item_5_left": item_5_left,
                        "option_1": option_1,
                        "option_2": option_2,
                        "option_3": option_3,
                        "option_4": option_4,
                        "option_5": option_5
                    },
                    "tags": []
                }

            elif notetype == "Omissão de Palavras":
                for index, field in enumerate(fields):
                    print(f'Indíce:{index} Valor: {field}')
                if len(fields) < 3:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada.")
                    return None

                question = fields[1].strip()
                dica = fields[2].strip()

                if not question:
                    print(f"Cartão com campos necessários ausentes.")
                    return None

                note =  {
                    "deckName": deck_name,
                    "modelName": notetype,
                    "fields": {
                        "Texto": question,
                        "Dica": dica
                    },
                    "tags": []
                }

            elif notetype == "Customizado":
                if len(fields) < 3:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada: {line}")
                    return None

                question = fields[1].strip()
                answer = fields[2].strip()
                hint = fields[3].strip() if len(fields) > 2 else ""

                if not question or not answer:
                    print(f"Cartão com campos necessários ausentes. Linha ignorada: {line} ")
                    return None

                note =  {
                    "deckName": deck_name,
                    "modelName": notetype,
                    "fields": {
                        "Pergunta": question,
                        "Resposta": answer,
                        "Dica": hint
                    },
                    "tags": []
                }

            else:
                print(f"Tipo de nota desconhecido: {notetype}")
                return None

            # Adicionar a nota ao baralho via AnkiConnect
            response = invoke('addNote', note=note)
            if response.get('error'):
                print(f"Erro ao adicionar o cartão: {response['error']}")
            else:
                print(f"Cartão adicionado: {question}")

if __name__ == "__main__":
    file_path = input("Digite o caminho do arquivo .txt: ")
    import_cards_to_anki(file_path)
