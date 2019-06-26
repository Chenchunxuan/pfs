import os
from invoke import task


@task
def run(c, production=False, debug=False):
    if production:
        c.run("python3 main.py")
    else:
        if debug:
            c.run("pipenv run python3 main.py -d")
        else:
            c.run("pipenv run python3 main.py")


@task
def deploy(c):
    c.run("pipenv lock -r > requirements.txt")
    c.run("pip3 install -r requirements.txt")
    os.remove("requirements.txt")