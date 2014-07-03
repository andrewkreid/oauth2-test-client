# oauth2-test-client

A simple python-flask to test OAuth2 authentication against OpenAM

## Setup

This sample uses the [flask-oauthlib](https://github.com/lepture/flask-oauthlib) extension to Flask to do OAuthy things.

Install like so:
```
$ pip install Flask-OAuthlib
```

Arrange for your host to have a FQDN (eg the public AWS name)

If your params are different than the defaults, make a ```config.properties``` file:

```
consumer_key=<client name in OpenAM>
consumer_secret=<client password in OpenAM>
base_url=<root URL of the client host (this app)>
access_token_url=https://<OpenAM Host:Port>/openam/oauth2/access_token
authorize_url=https://<OpenAM Host:Port>/openam/oauth2/authorize
tokeninfo_url=https://<OpenAM Host:Port>/openam/oauth2/tokeninfo
```

Run like so:
```bash
$ export OAUTHLIB_INSECURE_TRANSPORT=1   # If not using SSL everywhere
$ python ./openam_client.py
```

Browse to 
```
https://FQDN:5000/
```

Try logging in. You should get redirected to the OpenAM login page and then back.

## Quickstart for a fresh EC2 instance

```
sudo yum install git python-pip gcc pyOpenSSL
sudo pip install Flask-OAuthlib
git clone https://github.com/andrewkreid/oauth2-test-client.git
cd oauth2-test-client
export OAUTHLIB_INSECURE_TRANSPORT=1
python ./openam_client.py
```





