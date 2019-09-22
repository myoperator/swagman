import swagman
import yaml
import json
import click

def get_ignore_file(ignorefile):
    ignoreschema = None
    if ignorefile is None:
        return {}
    with open(ignorefile, 'r') as f:
        try:
            ignoreschema = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            ignoreschema = json.load(f)
        return ignoreschema

@click.command()
@click.option("--format", '-f', default='yaml', help="Format to output. One of json or yaml")
@click.option("--ignore", '-i', help="Ignore file in yaml or json")
@click.argument('POSTMANFILE')
@click.argument('OUTFILE')
def cli(format, ignore, postmanfile, outfile):
    ignoreschema = get_ignore_file(ignore)
    converter = swagman.Converter(postmanfile, ignoreschema=ignoreschema)
    swagger_output = converter.convert(format)
    with open(outfile, 'w') as f:
        f.write(swagger_output)
        click.echo(click.style('Schema converted successfully!', fg='green'))
        f.close()

if __name__ == '__main__':
    cli()