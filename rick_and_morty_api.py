# https://rickandmortyapi.com/documentation
import env
import requests


def get_single_character(character_id):
    url = env.RICK_AND_MORTY_URL + 'character/' + character_id
    response = requests.get(url)
    result = response.json()

    result_string = 'Имя: ' + result['name'] + ', ' + 'Статус: ' + result['status'] + ', ' + 'Расса: ' + result[
        'species'] + ', ' + 'Гендер: ' + result['gender']

    return {'result': result_string, 'image_url': result['image']}
