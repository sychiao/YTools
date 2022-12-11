import typer
import ruamel.yaml
import json

in_file = 'input.yaml'
out_file = 'output.json'

def yaml2Json(in_file: str,
              out_file: str
                = typer.Option(None, "-o", "--out_file", help="spec output filename")):

    out_file = out_file if out_file else "out.json"
    yaml = ruamel.yaml.YAML(typ='safe')
    with open(in_file) as fpi:
        data = yaml.load(fpi)
    with open(out_file, 'w') as fpo:
        json.dump(data, fpo, indent=2)

if __name__ == "__main__":
    typer.run(yaml2Json)
