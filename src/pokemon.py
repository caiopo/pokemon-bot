import requests
import config

from random import randint
from os.path import abspath, dirname, isfile
from PIL import Image

ARTWORKS_DIR = abspath(dirname(abspath(__file__)) + '/' + config.ARTWORKS_DIR)

print('Artworks dir: ' + ARTWORKS_DIR)

POKEAPI_URL = 'http://pokeapi.co/api/v2/pokedex/1/'

GENERATIONS = [151, 251, 386, 493, 649, 721]

class PokemonNames:
    names = []

    @classmethod
    def get(cls, number):
        if not cls.names:
            response = requests.get(POKEAPI_URL)
            if not response.ok:
                raise Exception('couldn\'t fetch name from pokeapi. number={}'.format(number))

            pokelist = response.json()['pokemon_entries']

            for d in pokelist:
                cls.names.append(d['pokemon_species']['name'].lower())

        return cls.names[number-1]

def make_shadow(infile, outfile):
    open_img = Image.open(infile)

    try:
        img = open_img.convert('RGBA')

        data = img.load()

        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if data[x, y][3] < 200:
                    data[x, y] = (255, 255, 255, 255)
                else:
                    data[x, y] = (0, 0, 0, 255)

        img.save(outfile, 'PNG')

    finally:
        open_img.close()

class Pokemon:
    def __init__(self, number):
        self.number = number
        self.name = PokemonNames.get(number)
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
    print(p.name.title(), p.artwork)
