import os
import queue
import time
import openai
import logging
import requests
import threading
from dotenv import load_dotenv
from enum import Enum

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

def read_prompt(file_path):
    """Lê as instruções de um arquivo de texto."""
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    return prompt

def invoke(action, **params):
    """Envia uma solicitação ao AnkiConnect."""
    response = requests.post('http://localhost:8765', json={
        'action': action,
        'version': 6,
        'params': params
    }).json()
    return response

def generate_deck_info(user_prompt, filename='instrucoes_create.txt'):
    """Gera o tópico e o nome do baralho a partir do prompt e instruções do arquivo."""
    # Ler as instruções do arquivo
    instructions_for_deck_info = read_instructions(filename)
    
    if not instructions_for_deck_info:
        raise ValueError("Instruções não encontradas no arquivo.")  # Levanta erro se não houver instruções

    # Construa a mensagem para o agente OpenAI
    messages = [
        {"role": "system", "content": instructions_for_deck_info},
        {"role": "user", "content": f"Gerar tópicos e baralhos baseados no prompt: {user_prompt}"}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            max_tokens=10000,
            n=1,
            stop=None
        )
        
        # Acessar a resposta
        deck_info_text = response.choices[0].message.content.strip()  # Acessar a mensagem gerada

        # Verifica se o retorno é uma string e não está vazio
        if not isinstance(deck_info_text, str) or not deck_info_text:
            raise ValueError("Retorno inválido: a resposta não é uma string ou está vazia.")

        print(f"Resposta gerada: {deck_info_text}")  # Adiciona um print para verificar a resposta

        # Divide o texto em linhas
        deck_info_list = []
        lines = deck_info_text.split("\n")  # Divide o texto em linhas

        print("Linhas processadas:")
        
        # Variáveis para armazenar tópico e baralho temporariamente
        current_topic = None
        current_deck = None

        for line in lines:
            line = line.strip()  # Remove espaços em branco

            # Verifica se a linha contém um tópico
            if line.startswith("Tópico:"):
                current_topic = line.split(":", 1)[1].strip()  # Extrai o tópico
                print(f"Tópico encontrado: '{current_topic}'")  # Print para depuração
            # Verifica se a linha contém um baralho
            elif line.startswith("Baralho:"):
                current_deck = line.split(":", 1)[1].strip()  # Extrai o nome do baralho
                print(f"Baralho encontrado: '{current_deck}'")  # Print para depuração

            # Se ambos estão disponíveis, adiciona à lista
            if current_topic and current_deck:
                deck_info_list.append((current_topic, current_deck))
                print(f"Adicionando ao deck_info_list: Tópico = '{current_topic}', Baralho = '{current_deck}'")  # Print para verificar
                # Reseta as variáveis
                current_topic = None
                current_deck = None

        # Verifique se a lista de deck_info_list não está vazia antes de retornar
        if not deck_info_list:
            raise ValueError("Nenhum tópico ou baralho válido foi gerado.")

        return deck_info_list

    except Exception as e:
        logging.error(f"Erro ao gerar tópico e nome do baralho: {e}")
        raise  # Relevanta a exceção para interromper a execução

def generate_flashcards(instructions, topic, model="gpt-4o-mini", temperature=0, max_tokens=10000):
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

def import_cards_to_anki(instructions, topic, deck_name, model="gpt-4o-mini", temperature=0, max_tokens=10000):
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

def start_import_thread(task_queue):
    """Função para processar as tarefas na fila."""
    while True:
        try:
            # Pega uma tarefa da fila (tópico e nome do baralho)
            topic, deck_name = task_queue.get(timeout=5)  # Tempo limite para evitar espera infinita
            
            # Executa a função que importa os cartões para o Anki
            instructions = read_instructions('instrucoes.txt')  # Carrega instruções de um arquivo .txt
            import_cards_to_anki(instructions, topic, deck_name)

            # Marca a tarefa como concluída
            task_queue.task_done()
        
        except queue.Empty:
            break  # Sai do loop se a fila estiver vazia após o tempo limite

def train_assistant():
    class Teste(Enum):
        TESTE = ", gere apenas um card para cada tipo de nota"
        ADD = ", aborde os principais conceitos, definições e regras"

    user_topic = input(f"Digite um tópico de teste para gerar cartões: ")
    test_topic = user_topic + Teste.ADD.value + Teste.TESTE.value
    test_deck_name = input("Digite o nome do baralho para gerar cartões de teste: ")  # Nome fixo para o baralho de treinamento
    
    # Gera os cartões de flash para o tópico de teste
    print(f"Treinando o assistente com o tópico: {test_topic}")
   
    # Adiciona o tópico de teste e o nome do baralho na fila de tarefas
    task_queue.put((test_topic, test_deck_name))
    
    # Chama a função que processa as tarefas na fila
    start_import_thread()  # Processa a fila de tarefas

    # Aguarda que todas as tarefas sejam concluídas antes de continuar
    task_queue.join()  # Aguarda a fila ser processada

    # Simule um tempo de espera para visualizar o resultado
    time.sleep(1)
    print(f"Treinamento concluído para o tópico: {test_topic}. Verifique os cartões gerados.")
    
    # Pergunta se os cartões gerados estão corretos
    verificado = input("Os cartões gerados estão corretos? (S/N): ").strip().lower()
    return verificado == 's'

if __name__ == "__main__":
    # Cria a fila de tarefas
    task_queue = queue.Queue()

    while True:
        # Pergunta se o usuário deseja treinar o assistente
        treinar = input("Você deseja treinar o assistente antes de gerar os cartões? (S/N): ").strip().lower()
        if treinar == 's':
            if not train_assistant():
                print("Por favor, ajuste o assistente conforme necessário antes de continuar.")
                continue

        # Coleta prompts e gera os baralhos automaticamente
        while True:
            user_prompt = read_prompt('user_prompt.txt')

            # Gerar tópicos e baralhos a partir do arquivo de instruções
            deck_info_list = generate_deck_info(user_prompt)

            # Inicializa a fila de tarefas
            task_queue = queue.Queue()

            # Adiciona os tópicos e nomes de baralhos à fila
            for topic, deck_name in deck_info_list:
                task_queue.put((topic.strip(), deck_name.strip()))  # Adiciona tópicos e baralhos

            # Neste ponto, todas as tarefas foram adicionadas à fila
            print("Tarefas coletadas. Iniciando threads para processamento.")

            # Cria e inicializa as threads para processar as tarefas na fila
            threads = []
            for _ in range(task_queue.qsize()):  # Cria tantas threads quanto tarefas
                thread = threading.Thread(target=start_import_thread, args=(task_queue,))
                thread.start()
                threads.append(thread)

            # Aguarda a conclusão de todas as tarefas na fila
            task_queue.join()

            # Aguarda que todas as threads terminem
            for thread in threads:
                thread.join()

            # Pergunta ao usuário se deseja continuar gerando mais cartões
            continuar = input("Deseja continuar gerando mais cartões? (S/N): ").strip().lower()
            if continuar != 's':
                print("Encerrando o programa.")
                break
        # Sai do loop principal e encerra o programa
        break
