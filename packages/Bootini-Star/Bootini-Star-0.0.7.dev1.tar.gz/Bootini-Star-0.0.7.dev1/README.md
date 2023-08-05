[![Build Status](https://travis-ci.org/rseichter/bootini-star.svg?branch=master)](https://travis-ci.org/rseichter/bootini-star)

# What is Bootini Star?

If you miss CCP's discontinued EVE Gate application, Bootini Star--abbreviated
as 'BS' from here on out--may be for you. BS is written in Python and uses the
EVE Swagger Interface, Flask and more to allow EVE Online players to handle
their evemail et al in a web browser.

# What do I need?

You can either run BS yourself if you meet the requirements listed below, or
find somebody who already runs a BS installation [like I
do](https://bs.willexplo.de), in which case you only need a web browser. This
text is meant for people who want to run their own instance of BS and/or help
with the development.

# How do I run my own instance?

## Requirements

1. An active EVE Online player account (Alpha or Omega).
1. A registered application with [CCP Games](https://developers.eveonline.com).
1. Python 3.6 or later.
1. [pip](https://pypi.python.org/pypi/pip)
1. [bash](https://www.gnu.org/software/bash/) or similar.
1. [MongoDB](https://www.mongodb.com).

## Setting up a fresh environment

Clone using Git:

```shell
cd /your/projects
git clone https://github.com/rseichter/bootini-star.git
```

Create and activate a fresh virtual Python environment. Remember to repeat the
activation step whenever you open a new shell session.

```shell
cd bootini-star
python -m venv venv
# Repeat the following for every new shell session
source venv/bin/activate
```

Install BS and required packages. Note that I use a
[PostgreSQL](https://www.postgresql.org) database and the necessary package is
therefore listed in the requirements file. The commands shown in this document
are also aimed at PostgreSQL, but I have successfully tested the application
with [MySQL](https://www.mysql.com) as well.

```shell
pip install -e .
pip install -r requirements.txt
which flask
```

The last command should return ```/your/projects/bootini-star/venv/bin/flask```.

Next, you need to configure BS according to your local needs using environment
variables. See the ```config.py``` module for a list of environment variables to
use.  Proper quoting is important so that your shell does not interfere with
your settings.

```shell
# Flask basics.
export FLASK_APP='bootini_star'
export FLASK_ENV='development'

# Important for the safety of all users.
export SECRET_KEY='Choose something random here'

# Allow HTTP callback URIs only during local development.
# If this is not set (which is the default) HTTPS is required.
export OAUTHLIB_INSECURE_TRANSPORT=1
export ESI_CALLBACK_URI='http://127.0.0.1:5000/sso/callback'

# ESI data is provided by CCP.
export ESI_CLIENT_ID='Your client ID'
export ESI_SECRET_KEY='Your secret key'

# BS needs a database.
export MONGODB_URI='mongodb://127.0.0.1/bs'

# Email settings for user registration.
export SMTP_SENDER_ADDRESS='itsa-me-mario@example.com'
export SMTP_SERVER_URI='tls://smtp.example.com/mario?DonkeyKong'
```

The MongoDB database specified via MONGODB_URI is expected to exist. BS will
however create the necessary collections. Use the following commands to import
the required static EVE data:

```shell
cd db-static
./db-helper.sh bs | /bin/sh
```


Make certain to specify a valid sender address or spam protection might kill off
your registration emails. Your users will also want to be able to contact you if
they have questions. As Robert Earhart's
[draft](https://tools.ietf.org/html/draft-earhart-url-smtp-00) for specifying
SMTP servers using URIs was never ratified, I decided to implement things
thusly:

SMTP server running on the local machine, no authentication:

```
smtp://localhost
```

Host with TLS authentication, user 'mario', password 'DonkeyKong':

```
tls://host.example.com/mario?DonkeyKong
```

You may specify a port number (e.g. smtp://localhost:4321) if the server listens
on a non-standard port. The defaults are port 25 for unencrypted SMTP sessions
and port 587 for SMTP with TLS, and BS smartly (cough) uses the proper values if
you don't specify a port.

## Why is there no complete default configuration?

Every BS installation requires individual settings for application ID,
application secret and OAuth2 callback URL which are available only after
registering an application at [CCP's developer
site](https://developers.eveonline.com). That is something I cannot do for you,
because for some weird reason I don't seem to have access to your EVE online
accounts.

## Running the application

Make sure to set up your environment properly for each development session, as
described above. You might want to add these commands to a shell script. With
the correct environment, all that's left to do is this:

```shell
# Set up environment first!
flask run
```

After Flask startup is complete, you should be able to open the application via
[http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser, if you have
kept Flask's default server and port settings.

## Admin privileges

As a security measure, admin privileges can only be granted by setting the user
level directly on the database level. After signing up in the application, use
the following MongoDB shell command:

```shell
mongo bs --eval 'db.users.updateOne({email: "you@your.domain"}, {$set: {level: 10}})'
```
You should see the following result:
```shell
{ "acknowledged" : true, "matchedCount" : 1, "modifiedCount" : 0 }
```

After logging in, you should now see an "Admin page" entry in the settings
menu. Use this page to create the DB indexes. That concludes the Bootini Star
configuration.
