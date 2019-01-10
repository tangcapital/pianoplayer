# PianoPlayer 2.0
Automatic piano fingering generator. <br />
and [music21](http://web.mit.edu/music21).<br />

## Download and Install:
```bash
pip install --upgrade pianoplayer
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
pianoplayer [-h] [-o] [-n] [-s] [-d] [-k] [-rbeam] [-lbeam] [-q] [-m] [-v] [--vtk-speed] 
            [-z] [-l] [-r] [-XXS] [-XS] [-S] [-M] [-L] [-XL] [-XXL]
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


