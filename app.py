from functools import wraps
from flask import Flask, redirect, render_template, request, session, url_for
import requests
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')



app = Flask(__name__)
app.config.update(**config['OAuth2'])
app.secret_key = config['App']['secret_key']


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'access_token' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def home():
    access_token = session['access_token'] if 'access_token' in session else None
    username = session['username'] if 'username' in session else None
    return render_template('index.html', access_token=access_token, username=username, user_data=session.get('user_data'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Redirect the user to the OAuth2 provider's authorization endpoint
        url_authorize = app.config['url_authorize']
        redirect_uri = app.config['redirect_uri']
        client_id = app.config['client_id']
        scope = 'openid' # profile email phone address'
        state = 'random_state_value'
        return redirect(f'{url_authorize}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}')
    elif request.method == 'GET':
        return render_template('login.html')
    else:
        return 'Method not allowed', 405
    

@app.route('/callback')
def callback():
    # Handle the callback from the OAuth2 provider
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Exchange the authorization code for an access token
    url_access_token = app.config['url_access_token']
    response = requests.post(url_access_token, data={
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': app.config['client_id'],
        'client_secret': app.config['client_secret'],
        'redirect_uri': app.config['redirect_uri']
    })
    
    # Process the access token
    access_token = response.json().get('access_token')

    print(access_token)
    # TODO: Store the access token securely and use it for API requests
    session['access_token'] = access_token



    url_resource_owner_details = app.config['url_resource_owner_details']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url_resource_owner_details, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(user_data)
        session['user_data'] = user_data
        session['username'] = user_data.get('name')
    else:
        session['username'] = None

    return redirect(url_for('home'))

@login_required
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('access_token', None)
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
