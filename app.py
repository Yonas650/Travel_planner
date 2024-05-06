from flask import Flask, render_template, request, redirect, session, flash
import openai
import os
import markdown
import os

app = Flask(__name__)
app.secret_key = 'nothing'

# Set your OpenAI API key (replace with your actual API key)
openai.api_key = os.getenv('OPENAI_API_KEY')

users_file = 'users.txt'  # File to store user data
preferences_file = 'preferences.txt'  # File to store preferences
contact_file = 'contacts.txt'
# Function to read users from file
def read_users():
    users = {}
    try:
        with open(users_file, 'r') as file:
            for line in file:
                username, email, password = line.strip().split(',')
                users[username] = {'email': email, 'password': password}
    except FileNotFoundError:
        pass
    return users

# Function to write a new user to file
def write_user(username, email, password):
    with open(users_file, 'a') as file:
        file.write(f"{username},{email},{password}\n")

# Function to save preferences
def save_preferences(username, data):
    with open(preferences_file, 'a') as file:
        file.write(f"{username},{data['destination']},{data['budget']},{data['check_in']},{data['check_out']}\n")

def save_contact(data):
    with open(contact_file, 'a') as file:
        file.write(f"{data['name']},{data['email']},{data['message']}\n")
# Function to call the OpenAI API for itinerary generation
def get_itinerary(destination, budget, check_in, check_out):
    try:
        prompt = f"""Create a highly detailed and structured itinerary for a trip to {destination} 🏖️ with a budget of ${budget} 💸. The trip starts on {check_in} and ends on {check_out}. Please include:
                    - 🚗 Transportation options
                    - 🏛️ Tourist attractions
                    - 🍽️ Dining recommendations
                    - 🛏️ Accommodation options
                    - 🎉 Activities
                    - Any other relevant details for a memorable trip!
                    -Please also add very fance emjois and make evrything very structured
                    """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return markdown.markdown(response.choices[0].message.content)
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    # Check if the user is logged in
    if 'username' in session:
        return render_template('index.html', is_logged_in=True)
    return render_template('index.html', is_logged_in=False)

@app.route('/login', methods=['POST'])
def login():
    users = read_users()
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]['password'] == password:
        session['username'] = username
        flash('Login successful', 'success')
        return redirect('/')
    else:
        flash('Invalid username or password', 'danger')
        return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    users = read_users()
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    if username not in users:
        write_user(username, email, password)
        flash('Registration successful', 'success')
    else:
        flash('Username already exists', 'danger')
    return redirect('/')

@app.route('/preferences', methods=['POST'])
def preferences():
    if 'username' not in session:
        flash('Please log in to view this page', 'danger')
        return redirect('/')
    preferences_data = {
        'destination': request.form['destination'],
        'budget': request.form['budget'],
        'check_in': request.form['check_in'],
        'check_out': request.form['check_out']
    }
    save_preferences(session['username'], preferences_data)
    itinerary = get_itinerary(preferences_data['destination'], preferences_data['budget'], preferences_data['check_in'], preferences_data['check_out'])
    if "Error" in itinerary:
        flash('An error occurred while generating the itinerary', 'danger')
    else:
        flash('Itinerary generated successfully!', 'success')
    return render_template('index.html', itinerary=itinerary, is_logged_in=True)
@app.route('/contact', methods=['POST'])
def contact():
    contact_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'message': request.form['message']
    }
    save_contact(contact_data)
    flash('Thank you for contacting us!', 'success')
    return redirect('/')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

