import requests
import io
import sys

DEV_URL = "https://7pnb6mulwk.execute-api.us-west-2.amazonaws.com/dev/run"
PROD_URL = "https://w5orqub3ii.execute-api.us-west-2.amazonaws.com/prod/run"

if "--prod" in sys.argv:
    API_URL = PROD_URL
else:
    API_URL = DEV_URL

filename = "100 Years - Five for Fighting.xml"

with open(filename, "rb") as infile:
    data = infile.read()
    infile_buf = io.BytesIO(data)
    infile_buf.seek(0)

print("posting to {}".format(API_URL))
result = requests.post(API_URL,
    data=infile_buf,
    params={
        "output-key": filename,
        "num-measures": 10,
    }
)

try:
    result.raise_for_status()
except Exception as e:
    print("error in request {}".format(str(e)))

print("got result ", result.content)
