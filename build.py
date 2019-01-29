import pylambdas
import os
import sys
import subprocess

def get_root():
    return os.path.dirname(os.path.abspath(__file__))

stages = [
    "dev",
    "prod"
]

def deploy(stage="dev"):
    print("deploying to ", stage)
    if stage not in stages:
        raise ValueError("stage must be one of the following values: {}".format(str(stages)))
    os.chdir("lambdabuild/piano-fingers-api")
    subprocess.check_call([
        "serverless",
        "deploy",
        "--stage",
        stage,
        "--verbose"
    ])

def piano_player_api(deploy=False):
    config = {
        "name": "piano-fingers-api",
        "yml": "piano-fingers-api.yml",
        "template": "aws-python",
        "pyversion": "3.7",
        "depend": {
            "local": [
                "main.py",
                "monkeypatch.py"
            ],
            "submodule": [ "pianoplayer" ],
            "python": [
                "music21"
            ]
        },
        "configs": [],
        "root": get_root(),
        "build": "lambdabuild"
    }
    pylambdas.build_with_config(config, deploy=deploy)

if __name__ == '__main__':
    piano_player_api(deploy=False)
    if "--prod" in sys.argv:
        deploy("prod")
    else:
        deploy("dev")
