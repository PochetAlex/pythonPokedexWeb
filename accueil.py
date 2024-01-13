from flask import Flask, render_template, redirect, url_for, request
import requests
import random

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.secret_key = "ne pas partager"

response = requests.get("https://api-pokemon-fr.vercel.app/api/v1/pokemon")
data = response.json()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password
        self.collection_data = []

users = {
    1: User(1, 'username', 'password'),
}

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

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

    # Check if there are evolutions
    if pokemon_details['evolution'] :
        evolutions = []
        if pokemon_details['evolution'] ['pre'] is not None:
            for evolution in pokemon_details['evolution']['pre']:
                evolution_id = evolution['pokedexId']
                evolution_condition = evolution['condition']

                evolution_response = requests.get(f"https://api-pokemon-fr.vercel.app/api/v1/pokemon/{evolution_id}")
                evolution_details = evolution_response.json()

                evolutions.append({
                    "id": evolution_id,
                    "name": evolution_details['name']['fr'],
                    "sprites": evolution_details['sprites']['regular'],
                    "stats": evolution_details['stats'],
                    "resistance": evolution_details['resistances'],
                    "condition": evolution_condition
                })
        if pokemon_details['evolution'] ['next'] is not None:
            for evolution in pokemon_details['evolution']['next']:
                evolution_id = evolution['pokedexId']
                evolution_condition = evolution['condition']

                evolution_response = requests.get(f"https://api-pokemon-fr.vercel.app/api/v1/pokemon/{evolution_id}")
                evolution_details = evolution_response.json()

                evolutions.append({
                    "id": evolution_id,
                    "name": evolution_details['name']['fr'],
                    "sprites": evolution_details['sprites']['regular'],
                    "stats": evolution_details['stats'],
                    "resistance": evolution_details['resistances'],
                    "condition": evolution_condition
                })

        return render_template('pokemon_details.html', pokemon=pokemon_details, evolutions=evolutions)
    else:
        return render_template('pokemon_details.html', pokemon=pokemon_details, evolutions=None)


#Page pour afficher la collection
@app.route('/collection')
@login_required
def collection():
    user_collection = current_user.collection_data
    return render_template('collection.html', collection=user_collection)

@app.route('/add_to_collection/<int:pokemon_id>', methods=['POST'])
@login_required
def add_to_collection(pokemon_id):
    response = requests.get(f"https://api-pokemon-fr.vercel.app/api/v1/pokemon/{pokemon_id}")
    pokemon_details = response.json()

    if pokemon_id not in [item['id'] for item in current_user.collection_data]:
        current_user.collection_data.append({
            "id": pokemon_id,
            "name": pokemon_details['name']['fr'],
            "sprites": pokemon_details['sprites'],
            "stats": pokemon_details['stats'],
            "resistance": pokemon_details['resistances']
        })

    return redirect(url_for('home'))

@app.route('/remove_from_collection/<int:pokemon_id>', methods=['POST'])
@login_required
def remove_from_collection(pokemon_id):
    current_user.collection_data = [pokemon for pokemon in current_user.collection_data if pokemon['id'] != pokemon_id]
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((user for user in users.values() if user.username == username and user.password == password), None)
        if user:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        # Get username and password from the form
        username = registration_form.username.data
        password = registration_form.password.data

        user_id = len(users) + 1

        new_user = User(user_id, username, password)
        new_user.collection_data = []
        users[user_id] = new_user

        login_user(new_user)

        return redirect(url_for('home'))

    return render_template('register.html', form=registration_form)

if __name__ == '__main__':
    app.run(debug=True)
