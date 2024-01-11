from flask import Flask, render_template, redirect, url_for, request
import requests
import random
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.secret_key = "ne pas partager"

response = requests.get("https://api-pokemon-fr.vercel.app/api/v1/pokemon")
data = response.json()

class PokemonForm(FlaskForm):
    autocomplete_input = StringField('autocomplete_input', validators=[DataRequired()])

# Page d'accueil
@app.route('/', methods=['GET', 'POST'])
def home():


    pokemon_form = PokemonForm()
    lesNomsDesPokemons= []
    for i in range(1, len(data)):
        lesNomsDesPokemons.append(data[i]['name']['fr'])
    types = get_tout_les_types()

    if request.args.get('type_select'):
        if request.args.get('type_select') == 'tous':
            pass
        else:
            if request.method == 'POST':
                pokemon_nom = request.form['autocomplete_input']  # Récupérer le nom du Pokémon depuis le formulaire
                pokemon_id = get_pokemon_id_by_name(pokemon_nom)
                if pokemon_id == None:
                    print("Ce pokemon n'existe pas.")
                    return []
                return redirect(
                    url_for('pokemon_details', pokemon_id=pokemon_id))  # Remplace 1 par l'ID du Pokémon trouvé
            else:
                detailed_pokemons_recommendation = get_pokemon_par_type(request.args.get('type_select'))
                return render_template('pagePrincipal.html', form=pokemon_form, lesNomsDesPokemons=lesNomsDesPokemons,
                                       recommendations=detailed_pokemons_recommendation, types=types)


    if request.method == 'POST':
        pokemon_nom = request.form['autocomplete_input']  # Récupérer le nom du Pokémon depuis le formulaire
        pokemon_id=get_pokemon_id_by_name(pokemon_nom)
        if pokemon_id==None:
            print("Ce pokemon n'existe pas.")
            return []
        return redirect(url_for('pokemon_details', pokemon_id=pokemon_id))  # Remplace 1 par l'ID du Pokémon trouvé


    if isinstance(data, list):

        detailed_pokemons_recommendation = get_pokemon_avec_nombre(15555555)

        return render_template('pagePrincipal.html', form=pokemon_form, lesNomsDesPokemons=lesNomsDesPokemons,
                               recommendations=detailed_pokemons_recommendation, types=types)
    else:
        print("La structure de la réponse API est inattendue.")
        return []

# Page pour afficher les détails d'un Pokémon
@app.route('/pokemon/<int:pokemon_id>')
def pokemon_details(pokemon_id):
    str_pokemon_id = str(pokemon_id)

    response = requests.get(f"https://api-pokemon-fr.vercel.app/api/v1/pokemon/{str_pokemon_id}")
    pokemon_details = response.json()

    return render_template('pokemon_details.html', pokemon=pokemon_details)


collection_data = []

#Page pour afficher la collection
@app.route('/collection')
def collection():
    return render_template('collection.html', collection=collection_data)

@app.route('/add_to_collection/<int:pokemon_id>', methods=['POST'])
def add_to_collection(pokemon_id):
    global collection_data

    response = requests.get(f"https://api-pokemon-fr.vercel.app/api/v1/pokemon/{pokemon_id}")
    pokemon_details = response.json()

    if pokemon_id not in [item['id'] for item in collection_data]:
        collection_data.append({
            "id": pokemon_id,
            "name": pokemon_details['name']['fr'],
            "sprites": pokemon_details['sprites'],
            "stats": pokemon_details['stats'],
            "resistance": pokemon_details['resistances']
        })

    return redirect(url_for('home'))

@app.route('/remove_from_collection/<int:pokemon_id>', methods=['POST'])
def remove_from_collection(pokemon_id):
    global collection_data

    collection_data = [pokemon for pokemon in collection_data if pokemon['id'] != pokemon_id]

    return redirect(url_for('collection'))

def get_pokemon_id_by_name(pokemon_name):
    for pokemon in data:
        if pokemon['name']['fr'] == pokemon_name:
            return pokemon['pokedexId']

    return None

def get_pokemon_par_type(type):
    resultat = []
    for pokemon in data:
        if pokemon['types']:
            for pokemon_type in pokemon['types']:
                if pokemon_type['name'].lower() == type.lower():
                    resultat.append(pokemon)
    return resultat

def get_pokemon_avec_nombre(nb):
    resultat = []

    nb = min(nb, len(data))
    for pokemon in range(1, nb):
        resultat.append(data[pokemon])

    return resultat

def get_tout_les_types():
    types_set = set()

    for pokemon in data:
        if pokemon['types']:
            for pokemon_type in pokemon['types']:
                types_set.add(pokemon_type['name'])

    tous_les_types = list(types_set)
    return tous_les_types


if __name__ == '__main__':
    app.run(debug=True)
