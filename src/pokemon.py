import requests
import config

from random import randint
from os.path import abspath, dirname, isfile
from PIL import Image

THIS_DIR = dirname(abspath(__file__))

POKEAPI_URL = 'http://pokeapi.co/api/v2/pokemon/{}/'

GENERATIONS = [151, 251, 386, 493, 649, 721]
MAX_POKEMONS = GENERATIONS[-1]

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
        self.artwork = abspath(THIS_DIR + '/{}/{}.png'.format(config.ARTWORKS_DIR, self.number))
        self.shadow = abspath(THIS_DIR + '/{}/{}-shadow.png'.format(config.ARTWORKS_DIR, self.number))

        if not isfile(self.shadow):
            make_shadow(self.artwork, self.shadow)

    def __repr__(self):
        return '<Pokemon object (number={}, name={}) at {}>'.format(
            self.number, self.name, hex(id(self)))

    @classmethod
    def random(cls, gen=None):
        if gen:
            return Pokemon(randint(1, generations[gen-1]))

        return Pokemon(randint(1, MAX_POKEMONS))

if __name__ == '__main__':
    p = Pokemon(GENERATIONS[1])
    print(p.name.title(), p.artwork)

