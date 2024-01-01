from flask import Flask, render_template
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

if __name__ == '__main__':
    app.run(debug=True)
