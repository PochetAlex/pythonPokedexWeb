from flask import Flask, render_template, redirect, url_for
import requests
import random


app = Flask(__name__)

def get_detailed_pokemons(pokemon_ids):
    detailed_pokemons = []

    for pokemon_id in pokemon_ids:
        response = requests.get(f"https://api-pokemon-fr.vercel.app/api/v1/pokemon/{pokemon_id}")
        pokemon_details = response.json()

        detailed_pokemons.append(pokemon_details)

    return detailed_pokemons

# Page d'accueil
@app.route('/')
def home():
    response = requests.get("https://api-pokemon-fr.vercel.app/api/v1/pokemon")
    data = response.json()

    if isinstance(data, list):
        selected_pokemons_main = random.sample(data, 6)

        detailed_pokemons_main = get_detailed_pokemons([pokemon['pokedexId'] for pokemon in selected_pokemons_main])

        selected_pokemons_recommendation = random.sample(data, 6)

        detailed_pokemons_recommendation = get_detailed_pokemons([pokemon['pokedexId'] for pokemon in selected_pokemons_recommendation])

        return render_template('pagePrincipal.html', pokemons=detailed_pokemons_main, recommendations=detailed_pokemons_recommendation)
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

if __name__ == '__main__':
    app.run(debug=True)
