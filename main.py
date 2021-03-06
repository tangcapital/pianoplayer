from __future__ import division, print_function
import os, sys, io
import json
from music21 import converter
from pianoplayer.hand import Hand
from pianoplayer.scorereader import reader

import boto3

try:
    BUCKET = os.environ["BUCKET"]
    PROCESS_LAMBDA_NAME = os.environ["PROCESS_LAMBDA"]
except Exception as e:
    print("error resolving enviornment variables - {}".format(str(e)))
    raise
else:
    print("Environment: \n BUCKET: {} \n PROCESS_LAMBDA: {}".format(
        BUCKET, PROCESS_LAMBDA_NAME
    ))

def put_s3(data, path, bucket=BUCKET):
    client = boto3.client('s3', 'us-west-2')
    client.put_object(
        Body=data,
        Bucket=bucket,
        Key=path
    )

def get_s3(key, bucket=BUCKET):
    client = boto3.client("s3", "us-west-2")
    return client.get_object(
        Bucket=bucket,
        Key=key
    )

def run_process_lambda(payload):
    client = boto3.client('lambda', 'us-west-2')
    client.invoke(
        FunctionName=PROCESS_LAMBDA_NAME,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )

default_args = {
    "n-measures": 0,
    "start-measure": 1,
    "depth": 0, #0 is auto,
    "debug": 0,
    "below-beam": 1, #fingering #'s below staff,
    "hand-stretch": 1,
    "hand-size": "XL"
}

valid_hand_sizes = [
    "XXS",
    "XS",
    "S",
    "M",
    "L",
    "XL",
    "XXL"
]

from monkeypatch import write_file_obj

def default_getter(src_dict, default_dict):
    def get(key):
        return src_dict.get(key, default_dict[key])
    return get

def str_to_bool(data):
    return bool(int(data))

#each array index refers to the corresponding part index of the music xml document
start_index = 2
hands_order = [
    "right", #skipped by default
    "right", #skipped by default
    "right", #start here by default
    "left",
    "right",
    "left"
]

def main(sf, part_index, args=default_args):
    get_arg = default_getter(args, default_args)

    hand_size = get_arg("hand-size")
    print("hand size {} {}".format(hand_size, type(hand_size)))
    if hand_size not in valid_hand_sizes:
        raise(ValueError("Invalid Hand Size argument: {}".format(hand_size)))
    depth = int(get_arg("depth"))
    debug = str_to_bool(get_arg("debug"))
    below_beam = str_to_bool(get_arg("below-beam"))
    hand_stretch = str_to_bool(get_arg("hand-stretch"))
    print("hand_stretch {} {}".format(hand_stretch, type(hand_stretch)))
    n_measures = int(get_arg("n-measures"))
    start_measure = int(get_arg("start-measure"))

    part = sf.parts[part_index]

    hand_selection = hands_order[part_index]
    hand = Hand(hand_selection, hand_size)
    hand.verbose = debug
    if len(part.flat) > 400 and depth == 0:
        print("Too many notes, defaulting to depth of 5")
        hand.autodepth = False
        hand.depth = 5
    elif depth == 0:
        hand.autodepth = True
    else:
        hand.autodepth = False
        hand.depth = depth
    hand.lyrics = below_beam
    hand.handstretch = hand_stretch

    hand.noteseq = reader(sf, beam=part_index)
    hand.generate(start_measure, n_measures)


def response(code, body, headers={ "Content-Type": "application/json" }):
    return {
        "statusCode": int(code),
        "headers": headers,
        "body": json.dumps(body)
    }

def error(body):
    return response(500, body)

def success(body):
    return response(200, body)

def invoke_handler(event, context):
    try:
        query_string = event.get('queryStringParameters')
        args = query_string if query_string else {}
        print(args)
        input_key = "input/{}".format(context.aws_request_id)
        output_key = args.get("output-key", "output.xml")
    except Exception as e:
        msg = "error {}".format(str(e))
        print(msg)
        return error(msg)

    try:
        print("putting input file in s3")
        input_bytes = event.get('body', b"")
        sf = converter.parse(input_bytes)
        frozen = converter.freezeStr(sf, fmt="pickle")
        put_s3(frozen, input_key)
    except Exception as e:
        msg = "error putting input file in s3 {}".format(str(e))
        print(msg)
        return error(msg)

    try:
        run_process_lambda({
            "args": args,
            "key": input_key,
            "output-key": output_key,
            "part-index": start_index
        })
    except Exception as e:
        msg = "error invoking lambda {}".format(str(e))
        print(msg)
        return error(msg)

    return success({
        "output_key": output_key,
        "bucket": BUCKET,
        "input_key": input_key
    })

def process_handler(body, context):
    try:
        print(body)
        input_key = body["key"]
        output_key = body["output-key"]
        part_index = body["part-index"]

        args = body.get("args", {})
    except Exception as e:
        print("error getting input params {}".format(str(e)))
        raise

    try:
        input_file = get_s3(input_key)
        input_bytes = input_file["Body"].read()
        sf = converter.thawStr(input_bytes)
        num_of_parts = len(sf.parts)
        max_index = num_of_parts - 1
    except Exception as e:
        msg = "error processing input file {}".format(str(e))
        print(msg)
        raise

    try:
        print("running part # {} (index {}) of {} (max index {})".format(
            part_index + 1, part_index, num_of_parts, max_index)
        )
        main(sf, part_index, args=args)
    except Exception as e:
        msg = "error converting file {}".format(str(e))
        print(msg)
        raise
    else:
        if part_index == max_index:
            print("finished processing last part, writing output")
            output_data = write_file_obj(sf)
            put_s3(output_data, output_key)
        else:
            print("still more parts to process, running next lambda")
            output_data = converter.freezeStr(sf, fmt="pickle")
            put_s3(output_data, input_key)
            run_process_lambda({
                "args": args,
                "key": input_key,
                "output-key": output_key,
                "part-index": part_index + 1
            })

if __name__ == "__main__":
    input_file = "BlinktheBee-Jingle.xml"

    with open(input_file, "r") as infile:
        buf = infile.read()

    sf = converter.parse(buf)

    main(sf, 2, args={ "n-measures": 15 })

    buf = write_file_obj(sf)

    with open("local_output.xml", 'wb') as outfile:
        outfile.write(buf.read())
