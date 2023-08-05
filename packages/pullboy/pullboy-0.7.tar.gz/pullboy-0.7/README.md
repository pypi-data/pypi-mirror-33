PullBoy
=======

Pullboy is a VERY simple server that listens for incoming connections and deploys projects according to a predefined script.

Steps
-----

First we install pullboy. `pip install pullboy` or the preferred one `pipenv install pullboy`. Second we write the deploy config file. An example would be:

```yaml
pullboy:
    workdir: '~/pullboy'
    script:
        - git pull origin master
        - make
    token: 'thisisnosecret'
    active: true  # This is optional. Default is assumed to be true
```

For Gitlab you can add push events in the [webhooks](https://gitlab.com/help/user/project/integrations/webhooks) and pullboy will take care of auto deploy for you. Here we don't really need a project name so we can have a config like so:


```yaml
a_token_for_gitlab_to_identify_the_script:
    workdir: '~/pullboy'
    script:
        - git pull origin master
        - make
    active: true
    branch: master
    gitlab: true
```

We can now add a gitlab webhook which has the secret token as `a_token_for_gitlab_to_identify_the_script`. That's all there is to it. Now whenever someone pushes to the repo and it's the master branch. the script will be executed.



Now we run pullboy with the following command `pullboy config.yaml`.

That's it.

Notes
-----

To make pullboy deploy something all you need to do is hit `https://wherever.pullboy.is.running.com:8764/deploy` with the items `project` and `token` in the POST body. For this activity **HTTPS is recommended**.

Tokens are meant to be kept a secret otherwise anyone with access to this URL can deploy the code (we don't want it to be that simple do we?).  An example cURL command to deploy the project shown in the config above would be:

```bash
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/deploy
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/pullboy/deploy
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/pullboy/deploy/user
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/pullboy/deploy/ci
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/pullboy/deploy/bossman
```

The url does not matter, whatever URL you access, pullboy will be ready to work. This makes it easy to use with a reverse proxy like Nginx where you can forward a url like `/pullboy/deployments/ci` and `/pullboy/deployments/manual` to Pullboy. The Nginx logs can act as *logs* for deployments.

[Let's Encrypt](https://letsencrypt.org/) is the recommended way to obtain HTTPS but in case you are using your laptop for something, [ngrok](https://ngrok.com/) is a neat way to get HTTPS.
