import os
import json
import time
import openai
import logging
import requests
from dotenv import load_dotenv
import threading

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração da chave da API
openai.api_key = os.getenv('OPENAI_API_KEY')

def read_instructions(file_path):
    """Lê as instruções de um arquivo de texto."""
    with open(file_path, 'r', encoding='utf-8') as file:
        instructions = file.read()
    return instructions

def invoke(action, **params):
    """Envia uma solicitação ao AnkiConnect."""
    response = requests.post('http://localhost:8765', json={
        'action': action,
        'version': 6,
        'params': params
    }).json()
    return response

def generate_flashcards(instructions, topic, model="gpt-4o-mini", temperature=0.75, max_tokens=10000):
    # Construir a mensagem no formato esperado pelo modelo GPT-4
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": f"Gere uma lista de cartões de flash sobre {topic}."}
    ]
    
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None
        )
        
        # Acessar o conteúdo da resposta corretamente
        cards_text = response.choices[0].message.content  # Acessar a mensagem gerada

        flashcards = cards_text.split('\n')  # Supondo que os cartões são separados por linhas
        
        return flashcards
    
    except Exception as e:  # Capturar qualquer erro que ocorra
        logging.error(f"Erro ao acessar a API OpenAI: {e}")
        return []

def import_cards_to_anki(instructions, topic, deck_name, model="gpt-4o-mini", temperature=0.8, max_tokens=10000):
    """Importa cartões de flash para o Anki a partir de instruções e tópico fornecidos."""
    # Verificar se o baralho já existe, caso contrário, criá-lo
    response = invoke('createDeck', deck=deck_name)
    if response.get('error'):
        logging.error(f"Erro ao criar o baralho: {response['error']}")
        return

    try:
        # Gerar flashcards usando as instruções e o tópico
        flashcards = generate_flashcards(instructions, topic, model=model, temperature=temperature, max_tokens=max_tokens)
        
        if not flashcards:
            logging.error("Nenhum cartão gerado.")
            return

        # Processar os dados e adicionar os cartões ao Anki
        for card in flashcards:
            card = card.strip()
            if not card:  # Ignorar cartões vazios
                continue
            
            # Dividir cada cartão usando \t como separador
            fields = card.split('\t')
            notetype = fields[0].strip()

            # Estrutura comum para as notas
            note = {
                "deckName": deck_name,
                "modelName": notetype,
                "fields": {},
                "tags": []
            }

            # Processar diferentes tipos de notas
            try:
                if notetype == "Multipla Escolha":
                    if len(fields) < 8:
                        logging.warning(f"Cartão com número insuficiente de colunas. Linha ignorada: {card}")
                        continue
                    
                    question, *options, answer = map(str.strip, fields[1:])
                    note["fields"] = {
                        "Pergunta": question,
                        "option_1 (A)": options[0],
                        "option_2 (B)": options[1],
                        "option_3 (C)": options[2],
                        "option_4 (D)": options[3] if len(options) > 3 else "",
                        "option_5 (E)": options[4] if len(options) > 4 else "",
                        "Resposta": answer
                    }

                elif notetype == "Certo ou Errado":
                    if len(fields) < 4:
                        logging.warning(f"Cartão com número insuficiente de colunas. Linha ignorada: {card}")
                        continue
                    
                    question, answer, correct_answer = map(str.strip, fields[1:4])
                    note["fields"] = {
                        "Pergunta": question,
                        "Resposta": answer,
                        "Resposta Certa": correct_answer
                    }

                elif notetype == "Ordenar":
                    if len(fields) < 3:
                        logging.warning(f"Cartão com número insuficiente de colunas. Linha ignorada: {card}")
                        continue
                    
                    question, *options = map(str.strip, fields[1:])
                    note["fields"] = {
                        "Pergunta": question,
                        "option_1": options[0],
                        "option_2": options[1],
                        "option_3": options[2] if len(options) > 2 else "",
                        "option_4": options[3] if len(options) > 3 else "",
                        "option_5": options[4] if len(options) > 4 else ""
                    }

                elif notetype == "Relacione as Colunas":
                    if len(fields) < 12:
                        logging.warning(f"Cartão com número insuficiente de colunas. Linha ignorada: {card}")
                        continue

                    question = fields[1].strip()
                    items_left = [fields[i].strip() for i in range(2, 7)]
                    options = [fields[i].strip() for i in range(7, 12)]
                    
                    note["fields"] = {
                        "Pergunta": question,
                        **{f"item_{i+1}_left": item for i, item in enumerate(items_left)},
                        **{f"option_{i+1}": option for i, option in enumerate(options)}
                    }

                elif notetype == "Omissão de Palavras":
                    if len(fields) < 3:
                        logging.warning(f"Cartão com número insuficiente de colunas. Linha ignorada: {card}")
                        continue

                    question, dica = map(str.strip, fields[1:])
                    note["fields"] = {
                        "Texto": question,
                        "Dica": dica
                    }

                elif notetype == "Customizado":
                    if len(fields) < 4:
                        logging.warning(f"Cartão com número insuficiente de colunas. Linha ignorada: {card}")
                        continue
                    
                    question, answer, hint = map(str.strip, fields[1:4])
                    note["fields"] = {
                        "Pergunta": question,
                        "Resposta": answer,
                        "Dica": hint
                    }

                else:
                    logging.warning(f"Tipo de nota desconhecido: {notetype}")
                    continue

                # Adicionar a nota ao baralho via AnkiConnect
                response = invoke('addNote', note=note)
                if response.get('error'):
                    logging.error(f"Erro ao adicionar o cartão: {response['error']}")
                else:
                    logging.info(f"Cartão adicionado: {note['fields'].get('Pergunta', 'Pergunta não disponível')}")

            except Exception as e:
                logging.error(f"Ocorreu um erro ao processar o cartão: {e}")

    except Exception as e:
        logging.error(f"Ocorreu um erro ao acessar a API OpenAI: {e}")

def start_import_thread(topic, deck_name):
    """Inicia a importação de cartões em uma nova thread."""
    instructions = read_instructions('instrucoes.txt')  # Carrega instruções de um arquivo .txt
    import_cards_to_anki(instructions, topic, deck_name)

def train_assistant():
    # Solicita um tópico de teste
    test_topic = input("Digite um tópico de teste para gerar cartões: ")
    test_deck_name =  input("Digite o nome do baralho para gerar cartões de teste: ")  # Nome fixo para o baralho de treinamento
    
    # Gera os cartões de flash para o tópico de teste
    print(f"Treinando o assistente com o tópico: {test_topic}")
    start_import_thread(test_topic, test_deck_name)
    # Simule um tempo de espera para visualizar o resultado
    time.sleep(1)
    print(f"Treinamento concluído para o tópico: {test_topic}. Verifique os cartões gerados.")
    
    # Pergunta se os cartões gerados estão corretos
    verificado = input("Os cartões gerados estão corretos? (S/N): ").strip().lower()
    return verificado == 's'

if __name__ == "__main__":
    while True:
        num_topics = int(input("Quantos prompts você deseja gerar? "))
        topics = []
        decks = []

         # Pergunta se o usuário deseja treinar o assistente
        treinar = input("Você deseja treinar o assistente antes de gerar os cartões? (S/N): ").strip().lower()
        if treinar == 's':
            if not train_assistant():
                print("Por favor, ajuste o assistente conforme necessário antes de continuar.")
                continue

        # Coletar prompts e nomes dos baralhos
        for i in range(num_topics):
            topic = input(f"Digite o prompt para o {i + 1}º tópico: ")
            deck_name = input(f"Digite o nome do baralho para o {i + 1}º tópico: ")
            topics.append(topic)
            decks.append(deck_name)

            # Inicia uma nova thread para cada tópico inserido
            thread = threading.Thread(target=start_import_thread, args=(topic, deck_name))
            thread.start()
            time.sleep(1)  # Aguarda um segundo antes de aceitar um novo tópico
            # Espera todas as threads terminarem antes de perguntar ao usuário se deseja continuar
            thread.join()  # Aguarda todas as threads finalizarem
       
        continuar = input("Deseja continuar gerando mais cartões? (S/N): ").strip().lower()
        
        if continuar != 's':
            print("Encerrando o programa.")
            break
