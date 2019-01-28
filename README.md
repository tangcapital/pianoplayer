# T3 PianoPlayer
Automatic piano fingering generator. <br />
and [music21](http://web.mit.edu/music21).<br />

## Run locally:
```bash
$ git clone https://github.com/tangcapital/pianoplayer.git
$ cd pianoplayer
$ pip3 install -e ./
$ pianoplayer ./scores/timetravel.xml --debug -b -x -XL -o timetravel_XL_x.xml
```

The ```pip3 install -e ./``` command installs the binary so you can run pianoplayer from the command line (within the project folder). To run pianoplayer from a python script you'll need to run ```pipenv install && pipenv install --dev``` as listed below in the API deployment section.

---

## API Usage:

POST to https://7pnb6mulwk.execute-api.us-west-2.amazonaws.com/dev/run
Payload is the xml file data as a bytestring

The rest of the arguments get passed as query string params (listed with the default values):
```python
{
    "n-measures": 0, #0 = auto, runs the whole file
    "start-measure": 1,
    "depth": 0, #0 is auto,
    "debug": 0, # true or false
    "below-beam": 1, # true or false, fingering #'s below staff,
    "hand-stretch": 1, # true or false
    "hand-size": "XL",
    "output-key": "output.xml",
    "bucket": "piano-fingers-api"
}
```
These are the hand sizes that are accepted by the API:
```JSON
[
    "XXS",
    "XS",
    "S",
    "M",
    "L",
    "XL",
    "XXL"
]
```

### Right Hand vs Left Hand

Our MusicXML documents are structured as follows:

```
Track 1 - lyrics (right hand default)
Track 2 - whole verse keys (right hand default)
Track 3 - melody
    - staff 1 - right hand
    - staff 2 - left hand
Track 4 - accompaniment
    - staff 1 - right hand
    - staff 2 - left hand
```
This results in the following hand order:

```
hands_order = [
    "right", #lyrics
    "right", #whole verse keys
    "right", #track 3 staff 1
    "left", #track 3 staff 2
    "right", #track 4 staff 1
    "left" #track 4 staff 2
]
```

### Responses

The API will return a response:
```JSON
{
    "output_key": output_key,
    "bucket": bucket,
    "input_key": input_key
}
```

The uploaded xml file will get saved to s3://bucket/input/input_key, as the processer needs to modify this file part by part.

Currently there is no API endpoint to check out the processing status, but you can just check for s3://bucket/output_key and if the file exists the process has completed (to be improved upon pending Admin requirements).


Here's a brief example of posting a MusicXML document to the API in node.js:

```node
const request = require("request-promise");
const fs = require("fs");

const postToApi = (filedata) => {
  request({
    url: "https://7pnb6mulwk.execute-api.us-west-2.amazonaws.com/dev/run",
    method: "POST",
    qs: {
      "output-key": "blank_space_from_node.xml",
      //other algorithm arguments go here
      //"hand-size": "XXL",
      //"hand-stretch": 0
    },
    body: filedata
  })
  .then((res) => console.log(res))
}

fs.readFile('blank_space_test.xml', function(err, data) {
  postToApi(data)
})

```


## Deployment

Before running any API deployment commands, you must run:
```bash
$ pipenv install && pipenv install --dev
```
This install pylambdas, which is used to build and deploy the AWS Lambda package.

To deploy the application to AWS, simply run:
```bash
pipenv run build
```

If you've made changes that include adding any python files, the files must be listed under the depend -> local section of the config in build.py:
```python
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
```

### Optional:
To visualize the annotated score install for free [musescore](https://musescore.org/it/download):
```bash
sudo apt install musescore
```

## Usage:
Example command line:<br />
`pianoplayer scores/bach_invention4.xml --debug -n10 -r -v -mb`<br />
will find the right hand fingering for the first 10 measures,
pop up a 3D rendering window and invoke musescore,
a [MusicXML](https://en.wikipedia.org/wiki/MusicXML)
file `output.xml` will be saved.<br />

```bash
pianoplayer         # if no argument is given a GUI will pop up (on windows try `python pianoplayer.py`)
# Or
pianoplayer [-h] [-o] [-n] [-s] [-d] [-m] [-b]
            [-XXS] [-XS] [-S] [-M] [-L] [-XL] [-XXL]
            filename
# Valid file formats: MusicXML, musescore, midi (.xml, .mscz, .mscx, .mid)
#
# Optional arguments:
#   -h, --help            show this help message and exit
#   -o , --outputfile     Annotated output xml file name
#   -n , --n-measures     [100] Number of score measures to scan
#   -s , --start-measure  Start from measure number [1]
#   -d , --depth          [auto] Depth of combinatorial search, [2-9]
#   --debug               Switch on verbosity
#   -m, --musescore       Open output in musescore after processing
#   -b, --below-beam      Show fingering numbers below beam line
#   -x, --hand-stretch    Enable hand stretching
#   -XXS, --hand-size-XXS Set hand size to XXS
#   -XS, --hand-size-XS   Set hand size to XS
#   -S, --hand-size-S     Set hand size to S
#   -M, --hand-size-M     Set hand size to M
#   -L, --hand-size-L     Set hand size to L
#   -XL, --hand-size-XL   Set hand size to XL
#   -XXL, --hand-size-XXL Set hand size to XXL
```


## How the algorithm works:
The algorithm minimizes the fingers speed needed to play a sequence of notes or chords by searching
through feasible combinations of fingerings.

## Parameters you can change:
- Your hand size (from 'XXS' to 'XXL') which sets the relaxed distance between thumb and pinkie (e.g. 'M' = 17 cm)
- Depth of combinatorial search, from 2 up to 9 notes ahead of the currently playing note. By
default the algorithm selects this number automatically based on the duration of the notes to be played.

## Advantages
One possible advantage of this algorithm over similar ones is that it is completely *dynamic*,
which means that it
takes into account the physical position and speed of fingers while moving on the keyboard
and the duration of each played note.
It is *not* based on a static look-up table of likely or unlikely combinations of fingerings.

## Limitations
- Some specific fingering combinations, considered unlikely in the first place, are excluded from the
search (e.g. the 3rd finger crossing the 4th).
- Hands are always assumed independent from each other.
- Repeated notes for which pianists often alternate fingers will be assigned to the same finger.


Fingering a piano score can vary a lot from indivual to individual, therefore there is not such
a thing as a "best" choiche for fingering.
This algorithm is meant to suggest a fingering combination which is "optimal" in the sense that it
minimizes the effort of the hand avoiding unnecessary movements.

## In this release / To do list:
- Improved fingering prediction by allowing some degree of hand stretching (stil experimental, use `-x` option).
- Patch in [music21](http://web.mit.edu/music21) for fingering positions as shown in *musescore*.
If fingering numbers are still not clearly visible use `-b` option.
- Small notes/ornaments are ignored.
- Some odd fingering in left hand of scores/mozart_fantasia.xml needs to be fixed.
