import requests
import config

from random import randint
from os.path import abspath, dirname, isfile
from PIL import Image

ARTWORKS_DIR = abspath(dirname(abspath(__file__)) + '/' + config.ARTWORKS_DIR)

print('Artworks dir: ' + ARTWORKS_DIR)

POKEAPI_URL = 'http://pokeapi.co/api/v2/pokemon/{}/'

GENERATIONS = [151, 251, 386, 493, 649, 721]

def fetch_name(number):
    response = requests.get(POKEAPI_URL.format(number))

    if not response.ok:
        raise Exception('couldn\'t fetch name from pokeapi. number={}'.format(number))

    return response.json()['name'].lower()

def make_shadow(infile, outfile):
    img = Image.open(infile).convert('RGBA')

    data = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if data[x, y][3] < 200:
                data[x, y] = (255, 255, 255, 255)
            else:
                data[x, y] = (0, 0, 0, 255)

    img.save(outfile)

class Pokemon:
    def __init__(self, number):
        self.number = number
        self.name = fetch_name(number)
        self.artwork = ARTWORKS_DIR + '/{}.png'.format(number)
        self.shadow = ARTWORKS_DIR + '/{}-shadow.png'.format(number)

        if not isfile(self.shadow):
            make_shadow(self.artwork, self.shadow)

    def __repr__(self):
        return '<Pokemon object (number={}, name={}) at {}>'.format(
            self.number, self.name, hex(id(self)))

    @classmethod
    def random(cls, gen=0):
        return Pokemon(randint(1, GENERATIONS[gen-1]))

if __name__ == '__main__':
    p = Pokemon(GENERATIONS[1])
    p = Pokemon(25)
    print(p.name.title(), p.artwork)
