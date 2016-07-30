help = '''Bot para jogar "Quem é esse Pokémon?"

/pokemon - Enviarei a foto de um Pokémon e você terá 15 segundos para descobrir seu nome.

Você pode colocar o número de uma geração ao lado do comando (ex. /pokemon1) para que eu envie apenas Pokémons até esta geração.

Meu repositório: https://github.com/caiopo/pokemon-bot

Feito por @caiopo'''

new = 'Quem é esse Pokémon?'

reveal = lambda p: 'Correto! É o {}!'.format(p.name.title())

revealgroup = lambda p, u: 'É o {}, {} acertou!'.format(p.name.title(), u)

times_up = lambda p: 'O tempo acabou! É o {}!'.format(p.name.title())
