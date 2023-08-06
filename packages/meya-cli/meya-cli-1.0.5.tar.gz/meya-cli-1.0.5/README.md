[ ![Codeship Status for meya-ai/meya-cli](https://app.codeship.com/projects/356c56e0-2be1-0136-8861-0e1ab7f9bed2/status?branch=master)](https://app.codeship.com/projects/287891)

# meya-cli
Command line utility for connecting with Meya Bot API and services


Installation
------------

1. Download the code

        git clone https://github.com/meya-ai/meya-cli.git
        cd meya-cli

2. Install dependencies ([virtualenv](http://virtualenv.readthedocs.org/en/latest/) is recommended.)

        mkdir env
        virtualenv env
        . env/bin/activate
        pip install --upgrade pip
        pip install -U -r requirements.txt


Development
-----------

1. Set up a Meya bot for local mode using the virtualenv meya-cli install instructions

2. Inside the bot's environment, run `pip install -e <CLONE_PATH>/meya-cli` (where `<CLONE_PATH>` is the parent
   directory of your downloaded code)

3. Now when you use the `meya-cli` command, it's running code from your local development environment


Tests
-----

        python -m unittest discover tests
