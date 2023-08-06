import configparser
import click
import sys
import pur
import os
from ._folder import TmpDir


def _standardize_requirements(req):
    req = req.strip()
    req = req.replace(";", "\n").strip()
    r = req.replace("\n\n", "\n")
    while len(r) < len(req):
        req = r
        r = req.replace("\n\n", "\n")
    req = [r.strip() for r in req.split("\n")]
    return "\n".join(req)


def update_requirements(req):
    req = _standardize_requirements(req)
    with TmpDir() as folder:
        input_file = os.path.join(folder, "requirements.txt")
        output_file = os.path.join(folder, "requirements-output.txt")
        with open(input_file, "w") as f:
            f.write(req)
        pur.update_requirements(
            input_file=input_file, output_file=output_file, echo=True
        )
        with open(output_file, "r") as f:
            data_output = f.read().strip()

        data_input = req.split("\n")
        data_output = data_output.split("\n")
        data = dict(zip(data_input, data_output))

    return data


def _update_setupcfg(filepath, req_map, sections):
    setupcfg = []
    state = "unknown"
    with open(filepath, "r") as f:
        for line in f:
            for s in sections:
                if s in line:
                    state = s
                    break
            else:
                if state in sections:
                    s = line.strip()
                    if state in req_map and s in req_map[state]:
                        line = line.replace(s, req_map[state][s])
            setupcfg.append(line)
    with open(filepath, "w") as f:
        f.write("".join(setupcfg))

    return 0


def update_setupcfg(filepath):
    sections = ["install_requires", "setup_requires", "tests_require"]

    config = configparser.ConfigParser()
    config.read(filepath)

    if "options" not in config.sections():
        print("Could not find the options section.")
        return 1

    req_map = dict()

    for s in sections:
        if s in config["options"]:
            req_map[s] = update_requirements(config["options"][s])

    return _update_setupcfg("setup.cfg", req_map, sections)


@click.command()
@click.argument("filepath")
@click.version_option()
def entry(filepath):
    if not os.path.exists(filepath):
        print("{} does not exist.".format(filepath))
        sys.exit(1)

    sys.exit(update_setupcfg(filepath))
