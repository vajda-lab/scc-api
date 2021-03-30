import click
import requests


SCC_API_TOKEN = ""  # TODO: pull from the environment
SCC_API_URL = "http://localhost:8000/apis/"


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    click.echo("Debug mode is %s" % ("on" if debug else "off"))


@cli.command()
def delete():
    click.echo("delete")
    data = {}
    headers = {"token": SCC_API_TOKEN}
    try:
        response = requests.delete(f"{SCC_API_URL}jobs/", data=data, headers=headers)
        click.echo(response.status_code)
    except Exception as e:
        click.secho(f"{e}", fg="red")


@cli.command()
def status():
    click.echo("status")
    data = {}
    response = requests.get(f"{SCC_API_URL}jobs/", data=data)
    print(response.status_code)


@cli.command()
def submit():
    click.echo("submit")
    data = {}
    response = requests.post(f"{SCC_API_URL}jobs/", data=data)
    print(response.status_code)


if __name__ == "__main__":
    cli(obj={})
