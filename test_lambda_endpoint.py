import requests
import io

API_URL = "https://7pnb6mulwk.execute-api.us-west-2.amazonaws.com/dev/run"

filename = "100 Years - Five for Fighting.xml"

with open(filename, "rb") as infile:
    data = infile.read()
    infile_buf = io.BytesIO(data)
    infile_buf.seek(0)

result = requests.post(API_URL,
    data=infile_buf,
    params={
        "output-key": filename,
        "num-measures": 10
    }
)

try:
    result.raise_for_status()
except Exception as e:
    print("error in request {}".format(str(e)))

print("got result ", result.content)
