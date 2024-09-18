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

    notetype = input("Digite o nome do tipo de nota: ")

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
                if len(fields) < 4:
                    print(f"Cartão com número insuficiente de colunas. Linha ignorada: {line}")
                    continue
                
                # Extrair os campos do cartão
                question = fields[0].strip()
                answer = fields[2].strip()
                correct_answer = fields[3].strip()
                extra = fields[4].strip()

                if not question or not answer or not correct_answer:
                    print("Pergunta: ", question, question1, "Resposta: ", answer, "Correta: ", correct_answer)
                    print(f"Cartão com campos necessários ausentes. Linha ignorada: {line}")
                    continue

                note = {
                    "deckName": deck_name,
                    "modelName": notetype,  # Nome do tipo da nota fornecido no arquivo .txt
                    "fields": {
                        "Pergunta": question,
                        "Resposta": answer,
                        "Resposta Certa": correct_answer,
                        "Extra": extra
                    },
                    "tags": []
                }

            else:
                print(f"Tipo de nota desconhecido: {notetype}. Linha ignorada: {line}")
                continue

            # Adicionar a nota ao baralho via AnkiConnect
            response = invoke('addNote', note=note)
            if response.get('error'):
                print(f"Erro ao adicionar o cartão: {response['error']}")
            else:
                print(f"Cartão adicionado: {question}")

if __name__ == "__main__":
    file_path = input("Digite o caminho do arquivo .txt: ")
    import_cards_to_anki(file_path)
