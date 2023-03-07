import requests
from bs4 import BeautifulSoup


def find_movies(title: str):
    url = 'https://www.kinopoisk.ru/index.php?kp_query='
    html = requests.get(url + title)
    while 'captcha' in html.url:
        print(html.url)
        title = title[:-1]
        if len(title) < 3:
            return
        html = requests.get(url + title)

    soup = BeautifulSoup(html.text, features="html.parser")
    movies = {'top_result': '', 'results': {}}
    try:
        top_result = soup.find("div", class_='search_results').find('p', class_='name')
    except AttributeError:
        return

    top_result_url = 'https://www.kinopoisk.ru' + top_result.find('a').get('data-url')
    movies['top_result'] = (top_result.text, top_result_url)
    search_results = soup.find_all('div', class_='element')
    for mov in search_results[1:]:
        title = mov.find('p', class_='name')
        url = 'https://www.kinopoisk.ru' + title.find('a').get('data-url')
        movies['results'][title.text] = url
    return movies

