import requests
import lxml.html as html
import os
import datetime

from requests.models import Response

HOME_URL = 'https://www.larepublica.co/'
#En los comentarios encontraron que, por alguna razon, los h2 se leen mejor como text_fill y por eso con esta solucion se obtienen mas links
XPATH_LINKS_TO_ARTICLES = '//text-fill/a/@href'
XPATH_TITLE = '//div[@class="mb-auto"]/text-fill/span/text()'
XPATH_SUMMARY = '//div[@class="lead"]/p/text()'
XPATH_BODY = '//div[@class="html-content"]/p[not(@class)]/text()'


def parse_notice(link, today):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            notice = response.content.decode('utf-8')
            parsed = html.fromstring(notice)

            try:
                title = parsed.xpath(XPATH_TITLE)[0]
                #Con esto le digo a python que si encuentra una comilla doble en el titulo, la elimine
                title = title.replace('\"', '')
                summary = parsed.xpath(XPATH_SUMMARY)[0]
                body = parsed.xpath(XPATH_BODY)
            except IndexError:
                return

            #with es un manejador contextual, permite que si el archivo se llega a cerrar de manera inesperada porque el script no funciono, mantiene todo de manera segura
            with open(f'{today}/{title}.txt', 'w', encoding='utf-8') as f:
                f.write(title)
                f.write('\n\n')
                f.write(summary)
                f.write('\n\n')
                for p in body:
                    f.write(p)
                    f.write('\n')
            
        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


def parse_home():
    try:
        #La respuesta seria el documento HTML y todo lo que involucra HTTP
        response = requests.get(HOME_URL)
        if response.status_code == 200:
            #response.content devuelve el documento html de la respuesta
            home = response.content.decode('utf-8')
            
            #Con fromstring se toma el contenido html que se tiene en la variable home y lo transforma en un documento especial a partir del cual se puede hacer Xpath
            parsed = html.fromstring(home)    
            links_to_notices = parsed.xpath(XPATH_LINKS_TO_ARTICLES)

            #El metodo date trabaja fechas, y today trae la fecha del dia actual
            today = datetime.date.today().strftime('%d-%m-%Y')

            #Si en la carpeta actual no existe una carpeta con el nombre obtenido con today:
            if not os.path.isdir(today):
                os.mkdir(today)

            for link in links_to_notices:

                #funcion que entrara al link y extraera la informacion
                parse_notice(link, today)

        else:
            #raise lo que hace es elevar un error, justamente el ValueError que definimos
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


def run():
    parse_home()


if __name__ == '__main__':
    run()