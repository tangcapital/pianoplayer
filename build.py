import pylambdas
import os

def get_root():
    return os.path.dirname(os.path.abspath(__file__))

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
    piano_player_api(deploy=True)
