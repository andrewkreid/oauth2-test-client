import os
from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth
import logging
import requests
import json

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

# global properties dict. Can be optionally overriden with config.properties file
app_props = {
    'consumer_key': 'oauth2-test-client',
    'consumer_secret': 'sirca123',
    'base_url': 'https://dynam20.clarence.sirca.org.au:5000/',
    'access_token_url': "https://ec2-54-79-0-185.ap-southeast-2.compute.amazonaws.com:8443/openam/oauth2/access_token",
    'authorize_url': "https://ec2-54-79-0-185.ap-southeast-2.compute.amazonaws.com:8443/openam/oauth2/authorize",
    'tokeninfo_url': "https://ec2-54-79-0-185.ap-southeast-2.compute.amazonaws.com:8443/openam/oauth2/tokeninfo",
}

openam = oauth.remote_app(
    'openam',
    consumer_key=app_props['consumer_key'],
    consumer_secret=app_props['consumer_secret'],
    request_token_params={'scope': 'uid mail'},
    base_url=app_props['base_url'],
    request_token_url=None,                          # must be None for OAuth2
    access_token_method='POST',
    access_token_url=app_props['access_token_url'],
    authorize_url=app_props['authorize_url']
)


@app.route('/')
def index():
    isloggedin, token_info = validate_access_token()
    if isloggedin:
        return render_template("index.html", access_token=json.dumps(token_info, indent=4))
    else:
        return render_template("index.html")


@app.route('/login')
def login():
    return openam.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
@openam.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['access_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


def validate_access_token():
    """
    Check the access_token in the session with OpenAM to see if its OK.
    :return: (True, response_json) if access_token in session and is OK with OpenAM,
             (False, None) otherwise
    """
    global app_props
    if 'access_token' in session:
        # check the token
        log.debug("My access token is [%s]" % json.dumps(session['access_token']))
        token_url = app_props['tokeninfo_url']
        response = requests.get("%s?access_token=%s" % (token_url, session['access_token'][0]), verify=False)
        rval = {
            'status': response.status_code,
            'headers': dict(response.headers),
            'content': response.json()
        }
        log.debug(rval)
        response.close()
        return True, response.json()
    else:
        return False, None


@openam.tokengetter
def get_openam_oauth_token():
    return session.get('access_token')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    log = logging.getLogger('openam_client')

    if os.path.exists('config.properties'):
        with open('config.properties', 'r') as fd:
            for line in fd.readlines():
                tokens = line.strip().split('=')
                if len(tokens) == 2:
                    app_props[tokens[0]] = tokens[1]

    # The ssl_context is important here. oauthlib will complain about
    # the transport being insecure otherwise.
    app.run(debug=True, ssl_context="adhoc")
