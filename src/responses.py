help = '''Bot para jogar "Quem é esse Pokémon?"

/pokemon - Enviarei a foto de um Pokémon de qualquer geração e você terá 15 segundos para descobrir seu nome.

Você pode colocar o número de uma geração ao lado do comando (ex. /pokemon1) para que eu envie apenas Pokémons até esta geração.

Você também pode abreviar "pokemon" para apenas "p" no comando.

Meu repositório: https://github.com/caiopo/pokemon-bot

Feito por @caiopo'''

new = 'Quem é esse Pokémon?'

already_active = 'Já existe um jogo ativo no chat atual!'

score = 'Pontuações:'

score_not_found = 'Pontuação inexistente'

clear = 'Pontuações zeradas'

reveal = lambda p: 'Correto! É o {}!'.format(p.name.title())

revealgroup = lambda p, u: 'É o {}, {} acertou!'.format(p.name.title(), u)

times_up = lambda p: 'O tempo acabou! É o {}!'.format(p.name.title())
