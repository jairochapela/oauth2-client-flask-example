from functools import wraps
from flask import Flask, redirect, render_template, request, session, url_for
import requests
import os
import jwt
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.update(**os.environ)
app.secret_key = os.environ['SECRET_KEY']


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
    return render_template('index.html', access_token=access_token, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Redirect the user to the OAuth2 provider's authorization endpoint
        url_authorize = app.config['URL_AUTHORIZE']
        redirect_uri = app.config['REDIRECT_URI']
        client_id = app.config['CLIENT_ID']
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
    url_access_token = app.config['URL_ACCESS_TOKEN']
    response = requests.post(url_access_token, data={
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': app.config['CLIENT_ID'],
        'client_secret': app.config['CLIENT_SECRET'],
        'redirect_uri': app.config['REDIRECT_URI']
    })
    
    # Process the access token
    access_token = response.json().get('access_token')

    print(access_token)
    # TODO: Store the access token securely and use it for API requests
    session['access_token'] = access_token


    # token_data = jwt.decode(access_token, algorithms=["HS256"], verify=False)
    # session['username'] = token_data.get('preferred_username')

    url_resource_owner_details = app.config['URL_RESOURCE_OWNER_DETAILS']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url_resource_owner_details, headers)
    if response.status_code == 200:
        user_data = response.json()
        print(user_data)
        session['username'] = user_data.get('preferred_username')
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