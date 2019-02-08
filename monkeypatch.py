from music21.converter import subConverters
import io


class FileObjConverterMusicXML(subConverters.ConverterMusicXML):
    """
    music21.converters.subConverters.ConverterMusicXML
    """

    def writeDataStream(self, uselessFilePath, dataBytes):
        buf = io.BytesIO(dataBytes)
        buf.seek(0)
        return buf

def write_file_obj(score):
    '''
    hacked version of Music21Object.write to allow writing to a file object
    ripped from music21.base.py, Music21Object class def at line 260
    write method at line 2480
    '''
    formatWriter = FileObjConverterMusicXML()
    return formatWriter.write(score, "musicxml")
