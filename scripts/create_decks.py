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
    decks = [
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Desenvolvimento em Linguagens de programação::Java",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Desenvolvimento em Linguagens de programação::JavaEE",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Desenvolvimento em Linguagens de programação::JakartaEE",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Desenvolvimento em Linguagens de programação::JPA",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Desenvolvimento em Linguagens de programação::Javascript",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Análise estática de código::Clean code, SonarQube",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Arquitetura de software::Interoperabilidade de sistemas",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Ambientes de aplicação::Internet, intranet, extranet",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::DESENVOLVIMENTO DE SISTEMAS::Ferramentas de gestão da configuração::GIT",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::BANCO DE DADOS::Modelagem de dados::Conceitual, lógica e física",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::BANCO DE DADOS::Linguagens SQL::SQL, DDL, DML",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::BANCO DE DADOS::SGBDs::Características e operações",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::BANCO DE DADOS::Banco de dados NoSQL::Definições e exemplos",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::BANCO DE DADOS::Técnicas de integração de dados::ETL, ELT",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::GESTÃO E GOVERNANÇA DE TI::Gerenciamento de projetos::Conceitos e áreas de conhecimento",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::GESTÃO E GOVERNANÇA DE TI::Gestão de riscos::Gerenciamento de riscos em TI",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::GESTÃO E GOVERNANÇA DE TI::ITIL v4::Conceitos básicos, disciplinas",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::GESTÃO E GOVERNANÇA DE TI::Governança de TI::COBIT 2019",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::INTELIGÊNCIA DE NEGÓCIOS::Conceitos de BI::Fundamentos e características",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::INTELIGÊNCIA DE NEGÓCIOS::Data warehouse::Arquitetura e aplicações",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::SEGURANÇA DA INFORMAÇÃO::Políticas de segurança::Conceitos e definições",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::SEGURANÇA DA INFORMAÇÃO::Normas e procedimentos::ABNT NBR ISO/IEC 27001 e 27002",
        "CONHECIMENTOS ESPECÍFICOS - DATAPREV::SEGURANÇA DA INFORMAÇÃO::Mecanismos de segurança::Controle de acesso, OAuth2, SSO"
    ]

    # Criar todos os baralhos e sub-baralhos
    for deck in decks:
        print(f"Criando '{deck}'...")
        result = create_deck(deck)
        print(f"Resultado ao criar '{deck}': {result}")

if __name__ == "__main__":
    main()
