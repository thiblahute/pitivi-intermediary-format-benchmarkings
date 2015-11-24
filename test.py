#!/usr/bin/env python

import os
import time


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

enc_decs = {
    "jpeg": ("jpegenc quality=100", "jpegdec"),
    "prores": ("avenc_prores", "avdec_prores"),
    "h264-lossless": ("x264enc speed-preset=ultrafast qp-min=0 qp-max=0 key-int-max=1", "avdec_h264"),
    "webp": ("webpenc speed=0 ", "webpdec")
}

_dir = os.path.abspath(os.path.dirname(__file__))
outdir = os.path.join(_dir, "outdir")
try:
    os.mkdir(outdir)
except FileExistsError:
    pass

for f in ["h264-lossless", "prores", "jpeg"]:
    enc, dec = enc_decs[f]
    print("\nEncoder:: %s \n============" % (enc))
    for NUM_PASSES in [0, 1, 10, 20]:
        _filename = os.path.join(_dir, "infile.jpeg")
        command = "gst-launch-1.0 filesrc location=" + _filename + " ! " + \
            "jpegdec ! videoconvert ! "

        command += enc + "  !  "
        for i in range(NUM_PASSES):
            command += dec + "  !   " + enc + " ! "

        outfile = outdir + "/test.%s.%s" % (NUM_PASSES, f)
        command += " filesink " + "location=" + outfile

        print("num 'decode ! encode':  %s" % (NUM_PASSES), end="")
        t1 = time.time()
        if os.system(command + "> /dev/null") != 0:
            print("Failed to run: %s", command)
            exit(1)

        print(" -- duration: %ss -- size: %s" % (time.time() - t1, sizeof_fmt(
            os.stat(outfile).st_size)))

for f in ["h264-lossless", "prores", "jpeg"]:
    print("Testing: %s\n========" % f)
    enc, dec = enc_decs[f]

    uri = "file://%s/metro.MOV" % _dir
    outfile = "%s/metro.%s.mkv" % (outdir, f)

    print("  Encoding %s with: %s" % (uri, enc))

    command = "gst-launch-1.0 uridecodebin uri=" + uri + " ! videoconvert ! " + enc + "  !  " \
        + " matroskamux ! filesink " + "location=" + outfile

    t1 = time.time()
    if os.system(command + "> /dev/null") != 0:
        print("Failed to run: %s", command)
        exit(1)

    print("     -- > duration: %ss -- size: %s" % (time.time() - t1, sizeof_fmt(
        os.stat(outfile).st_size)))

    t1 = time.time()
    command = "gst-validate-1.0 --set-scenario=scrub_forward_seeking playbin video-sink=fakesink uri=file://" + outfile
    print("  Scrub forward seeking on: " + outfile)
    if os.system(command + "> /dev/null") != 0:
        print("Failed to run: %s", command)
        exit(1)

    print("     -- > duration: %ss\n" % (time.time() - t1))
