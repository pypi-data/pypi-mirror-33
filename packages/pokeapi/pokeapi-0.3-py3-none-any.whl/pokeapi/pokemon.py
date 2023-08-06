import requests, roman

def IDfromPokemon(name):
    if(name in [ j.split('_(Pok')[0] for j in [ i for i in requests.get('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number').text.split('/wiki/') if "_(Pok" in i ] ][1:-1:2]):
        x = requests.get('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number').text.split('<a href="/wiki/' + name)[0].split('monospace')[-1].split('<')[0].split('#')[1]
        return int(x)
    else:
        raise ValueError("That Pok%C3%A9mon doesn't exist!")

def PokemonfromID(pid):
    maxid = int(requests.get('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number').text.split('monospace">')[-1].split('<')[0].split('#')[1])
    if(pid <= 0 or pid > maxid):
        raise IndexError("That ID doesn't match is not within the bounds: 0-" + str(maxid))
    else:
        pid = str(pid)
        while(len(pid) != 3):
            pid = "0" + pid
        x = requests.get('https://pokemondb.net/pokedex/national').text.split('#' + pid + "</small")[1].split('</a>')[0].split(">")[-1]
        return x

def PokemonLearnset(name, generation):
    x = requests.get('https://pokemondb.net/pokedex/' + name.lower() + '/moves/' + str(generation)).text
    l = x.split('Moves learnt by HM')[0].split('Moves learnt by level up')[1].split('Egg moves')[0]
    moves = [ i.split('</')[0].split('>')[-1] for i in l.split('/move/')[1:] ]
    level = [ i.split('</td')[0].split('">')[1] for i in l.split('<tr>')[1:] ][1:]
    level = [ int(i) for i in level]
    type = [ i.split('"')[0] for i in l.split('type-icon type-')[1:] ]
    status = [ i.split('.png')[0] for i in l.split('/images/icons/')[1:] ]
    power = [ int(i.split('cell-num')[1].split('</td>')[0].split('>')[1].replace('&infin;', '100').replace('\u2014', '0')) for i in l.split('.png"')[1:] ]
    accuracy = [ int(i.split('cell-num')[2].split('</td>')[0].split('>')[1].replace('&infin;', '100').replace('\u2014', '0')) for i in l.split('.png"')[1:] ]
    pp = []
    for i in moves:
        p = requests.get('https://pokemondb.net/move/' + i.lower().replace(' ', '-')).text
        pp.append(int(p.split('<th>PP')[1].split(' &')[0].split('>')[-1]))
    learnsetl = []
    [ learnsetl.append([level[i], [moves[i], pp[i], power[i], accuracy[i], type[i], status[i]]]) for i in range(len(moves)) ]
    learnset = {}

    for levels in learnsetl:
        if(levels[0] in learnset):
            learnset[levels[0]].append(levels[1])
        else:
            learnset[levels[0]] = [levels[1]]
    return learnset

def PokemonLocations(name, game):
    x = requests.get('https://pokemondb.net/pokedex/' + name.lower().replace(' ', '-')).text
    l = [ i.split('href') for i in x.split('Where to find ')[1].split(game + '</span>')[1].split('</th>')[1].split('</td')[0][:-1].split('</a>') ]
    for i in range(len(l)):
        if(len(l[i]) == 2):
            k = l[i]
            l[i][0] = k[0].split('<')[0].replace('\n', '')
            l[i][1] = k[1].split('>')[1].split('<')[0].replace('\n', '')
        else:
            l[i] = l[i][0].split('>')[-1].split('<')[0]
        l[i] = ''.join(l[i])
    l = ''.join(l)
    return l

def PokemonTypes(name):
    x = requests.get('https://bulbapedia.bulbagarden.net/wiki/' + name + '_(Pok%C3%A9mon)').text
    x = x.split('">Abilities')[0].split(' (type)')
    x = [ i.split('</b></span>')[0].split('<b>')[-1] for i in x ][1:3]
    if(x[1] == "Unknown"):
        x[1] = "None"
    return x

def PokemonSprite(name):
    startgen = int(roman.fromRoman(
        requests.get('https://bulbapedia.bulbagarden.net/wiki/' + name + '_(Pok%C3%A9mon)').text.split('">Generation ')[
            1].split('<')[0]))
    fin = "https://img.pokemondb.net/sprites/sun-moon/dex/normal/" + name.lower() + ".png" if startgen == 7 else "https://img.pokemondb.net/sprites/omega-ruby-alpha-sapphire/dex/normal/" + name.lower() + ".png"
    return fin

def ShinyPokemonSprite(name):
    startgen = int(roman.fromRoman(
        requests.get('https://bulbapedia.bulbagarden.net/wiki/' + name + '_(Pok%C3%A9mon)').text.split('">Generation ')[
            1].split('<')[0]))
    fin = "https://img.pokemondb.net/sprites/sun-moon/dex/shiny/" + name.lower() + ".png" if startgen == 7 else "https://img.pokemondb.net/sprites/omega-ruby-alpha-sapphire/dex/shiny/" + name.lower() + ".png"
    return fin

def PokemonAbilities(name):
    x = requests.get('https://bulbapedia.bulbagarden.net/wiki/' + name + '_(Pok%C3%A9mon)').text
    abilities = list(filter(lambda a: a != "Cacophony", [i.split('"')[-1] for i in x.split(' (Ability)')][:-1]))
    while(len(abilities) != 3):
        abilities.insert(1, "None")
    return abilities

class Pokemon:
    def __init__(self):
        self.__gtg = {1: ["Red", "Blue", "Yellow"], 2: ["Gold", "Silver"], 3: ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"], 4: ["Diamond", "Pearl", "Platinum", "HeartGold", "SoulSilver"], 5: ["Black", "White", "Black 2", "White 2"], 6: ["X", "Y", "Omega Ruby", "Alpha Sapphire"], 7: ["Sun", "Moon", "Ultra Sun", "Ultra Moon"]}
        self.id = 1
        self.generation = 1
        self.name = "Bulbasaur"
        self.level = 13
        self.ability1 = PokemonAbilities(self.name)[0]
        self.ability2 = PokemonAbilities(self.name)[1]
        self.abilityH = PokemonAbilities(self.name)[2]
        self.hasAbility = "0"
        # self.moveset = {"Growl": [40, 0, 100, "Normal", "Status"], "Tackle": [35, 40, 100, "Normal", "Physical"], "Lee
        # ch Seed": [10, 0, 90, "Grass", "Status"], "Vine Whip": [25, 45, 100, "Grass", "Physical"]} # Move: [PP, Base D
        # amage, Accuracy, Typing, Special/Status/Physical]
        self.learnset = PokemonLearnset(self.name, self.generation)
        self.type1 = PokemonTypes("Bulbasaur")[0]
        self.type2 = PokemonTypes("Bulbasaur")[1]
        self.location = PokemonLocations(self.name, self.__gtg[self.generation][0])
        self.sprite = PokemonSprite(self.name)
        self.ssprite = ShinyPokemonSprite(self.name)

    def setPokemonByName(self, name, level):
        self.name = name
        self.id = IDfromPokemon(name)
        self.generation = int(roman.fromRoman(requests.get(
            'https://bulbapedia.bulbagarden.net/wiki/' + self.name + '_(Pok%C3%A9mon)').text.split('">Generation ')[1]
                                              .split('<')[0]))
        self.level = level
        self.ability1 = PokemonAbilities(self.name)[0]
        self.ability2 = PokemonAbilities(self.name)[1]
        self.abilityH = PokemonAbilities(self.name)[2]
        self.hasAbility = "0"
        self.learnset = PokemonLearnset(self.name, self.generation)
        self.type1 = PokemonTypes("Bulbasaur")[0]
        self.type2 = PokemonTypes("Bulbasaur")[1]
        self.location = PokemonLocations(self.name, self.__gtg[self.generation][0])
        self.sprite = PokemonSprite(self.name)
        self.ssprite = ShinyPokemonSprite(self.name)


    def setPokemonByID(self, pid, level):
        self.id = pid
        self.name = PokemonfromID(pid)
        self.generation = int(roman.fromRoman(requests.get(
            'https://bulbapedia.bulbagarden.net/wiki/' + self.name + '_(Pok%C3%A9mon)').text.split('">Generation ')[1]
                                              .split('<')[0]))
        self.level = level
        self.ability1 = PokemonAbilities(self.name)[0]
        self.ability2 = PokemonAbilities(self.name)[1]
        self.abilityH = PokemonAbilities(self.name)[2]
        self.hasAbility = "0"
        self.learnset = PokemonLearnset(self.name, self.generation)
        self.type1 = PokemonTypes("Bulbasaur")[0]
        self.type2 = PokemonTypes("Bulbasaur")[1]
        self.location = PokemonLocations(self.name, self.__gtg[self.generation][0])
        self.sprite = PokemonSprite(self.name)
        self.ssprite = ShinyPokemonSprite(self.name)

    def setAbility(self, choice):
        self.hasAbility = choice

    def setLevel(self, level):
        self.level = level
