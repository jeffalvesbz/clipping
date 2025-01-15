import requests
from GoogleNews import GoogleNews
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Função para encurtar links usando a API do TinyURL
def shorten_link(long_url):
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Erro ao encurtar o link {long_url}: {e}")
    return long_url

# Função para buscar notícias do Google News
def fetch_google_news(term, period='8h'):
    googlenews = GoogleNews(lang='pt', region='BR', encode='utf-8')
    googlenews.set_period(period)
    googlenews.get_news(term)
    results = googlenews.results()

    news_list = []
    for news in results:
        autor = news.get('media', 'Não informado')
        titulo = news['title']
        link = news['link']
        news_list.append({'autor': autor, 'titulo': titulo, 'link': link})
    
    return news_list

# Função para buscar notícias do News API
def fetch_news_api(term, api_key, language='pt'):
    url = f"https://newsapi.org/v2/everything?q={term}&language={language}&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            news_list = [
                {'autor': article.get('source', {}).get('name', 'Não informado'),
                 'titulo': article['title'],
                 'link': article['url']}
                for article in data.get('articles', [])
            ]
            return news_list
    except Exception as e:
        print(f"Erro ao buscar no News API: {e}")
    return []

# Função para combinar resultados de diferentes APIs
def get_all_news(term):
    # Substitua pela sua chave da News API
    api_key_newsapi = "2e9c8eddd38441668f259076dbb80236"

    google_news = fetch_google_news(term)
    news_api = fetch_news_api(term, api_key_newsapi)

    # Combine os resultados
    combined_news = google_news + news_api

    # Filtro de fontes confiáveis
    trusted_portals = [
        "G1", "Folha de S.Paulo", "O Globo", "UOL", "Estadão",
        "Correio Braziliense", "Valor Econômico", "Veja", "CNN Brasil", "BBC Brasil",
        "Metrópoles", "R7", "Exame", "Carta Capital", "Brasil 247", "Estado de Minas", "Zero Hora"
    ]

    # Filtro de fontes indesejadas
    keywords_to_ignore = ['Band News']
    filtered_news = [
        news for news in combined_news 
        if (not any(keyword in news['autor'] for keyword in keywords_to_ignore)) and
           any(portal in news['autor'] for portal in trusted_portals)
    ]

    return filtered_news

# Função para salvar os resultados em um arquivo HTML estilizado
def save_news_to_html(news_list, term):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"clipping_{timestamp}.html"

    with open(filename, 'w', encoding='utf-8') as file:
        # Cabeçalho do HTML com Bootstrap
        file.write(f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Clipping de Notícias - Elaborado pela CGCS</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container py-5">
                <h1 class="text-center mb-4">Clipping de Notícias</h1>
                <h4 class="text-muted">Termo pesquisado: {term}</h4>
                <p>Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <hr>
        """)

        # Lista de notícias
        for news in news_list:
            short_link = shorten_link(news['link'])
            file.write(f"""
                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">{news['titulo']}</h5>
                        <p class="card-text"><b>Fonte:</b> {news['autor']}</p>
                        <a href="{short_link}" target="_blank" class="btn btn-primary">Leia mais</a>
                    </div>
                </div>
            """)

        # Rodapé
        file.write("""
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)

    print(f"Site gerado: {filename}")

# Função principal
def generate_clipping():
    term = "Polícia Federal"  # Altere o termo de pesquisa conforme necessário
    all_news = get_all_news(term)

    if all_news:
        save_news_to_html(all_news, term)
        print("Clipping gerado com sucesso!")
    else:
        print("Nenhuma notícia encontrada.")

# Agendamento diário às 10h
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(generate_clipping, 'cron', hour=10, minute=0)
    print("Agendamento configurado para executar diariamente às 10h.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Execução interrompida.")
