#!/usr/bin/env python3
"""Mirror The Solo Block Record from sololuck.io into data/.

Downloads ONLY the two files that https://sololuck.io/api/legends/v1/ already
publishes (blocks.json and blocks.csv) and checks them against each other before
anything is written:

  * blocks.json must be the record (its schema id and licence), with a count
    that matches its own rows;
  * blocks.csv must match the csv_sha256 that blocks.json publishes;
  * both must carry the same blocks, in the same order, with the columns that
    datapackage.json and the README describe.

A download that fails any check stops the run with a message and writes nothing,
so a half-checked copy is never committed. It contacts nothing but sololuck.io:
the record is verified on the chain by its publisher, not from here.

On success it rewrites data/blocks.json and data/blocks.csv byte for byte as
published, and refreshes the fields that follow the data: the version and the
per-file bytes and sha256 in datapackage.json, and the version and release date
in CITATION.cff.
"""
import csv
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

BASE = "https://sololuck.io/api/legends/v1/"
UA = "solo-block-record-mirror (+https://github.com/sololuckio/solo-block-record)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The columns datapackage.json and the README data dictionary describe, in order.
# If the publisher adds, removes or renames one, stop: the descriptions must be
# updated by a person first, or this copy would ship data its docs do not match.
FIELDS = [
    "height", "date", "pool", "hardware", "hashrate_hs", "difficulty",
    "reward_btc", "reward_usd_reported", "expected_seconds_per_block",
    "chance_per_day", "chance_per_day_one_in", "source_label", "source_url",
    "block_url", "story", "note",
]


def get(name):
    req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 200:
            sys.exit("%s answered HTTP %s; nothing mirrored" % (BASE + name, r.status))
        return r.read()


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def fail(msg):
    sys.exit("refusing to mirror: " + msg)


def main():
    js = get("blocks.json")
    cs = get("blocks.csv")

    try:
        doc = json.loads(js)
    except ValueError as e:
        fail("blocks.json is not JSON (%s)" % e)
    if doc.get("schema") != "sololuck-solo-blocks/1":
        fail("unexpected schema id %r" % doc.get("schema"))
    if doc.get("license") != "CC BY 4.0":
        fail("unexpected licence %r" % doc.get("license"))
    version = str(doc.get("version") or "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", version):
        fail("unexpected version %r" % version)
    blocks = doc.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        fail("blocks.json carries no rows")
    if doc.get("count") != len(blocks):
        fail("count says %r but there are %d rows" % (doc.get("count"), len(blocks)))
    for b in blocks:
        if set(b.keys()) != set(FIELDS):
            fail("block %r has fields %r, expected %r" % (b.get("height"), sorted(b.keys()), FIELDS))

    if sha256(cs) != doc.get("csv_sha256"):
        fail("blocks.csv (%s) does not match the csv_sha256 in blocks.json (%s)"
             % (sha256(cs), doc.get("csv_sha256")))
    text = cs.decode("utf-8")
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader)
    if header != FIELDS:
        fail("the CSV columns changed to %r; update datapackage.json and the README first" % header)
    heights = [int(row[0]) for row in reader]
    if heights != [b["height"] for b in blocks]:
        fail("blocks.csv and blocks.json do not list the same blocks in the same order")

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    for name, body in (("blocks.json", js), ("blocks.csv", cs)):
        with open(os.path.join(ROOT, "data", name), "wb") as f:
            f.write(body)

    pkg_path = os.path.join(ROOT, "datapackage.json")
    with open(pkg_path, encoding="utf-8") as f:
        pkg = json.load(f)
    pkg["version"] = version
    for res in pkg["resources"]:
        body = js if res["path"] == "data/blocks.json" else cs if res["path"] == "data/blocks.csv" else None
        if body is None:
            fail("datapackage.json lists an unexpected resource %r" % res["path"])
        res["bytes"] = len(body)
        res["hash"] = "sha256:" + sha256(body)
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2, ensure_ascii=False)
        f.write("\n")

    cff_path = os.path.join(ROOT, "CITATION.cff")
    with open(cff_path, encoding="utf-8") as f:
        cff = f.read()
    cff, n1 = re.subn(r'(?m)^version: ".*"$', 'version: "%s"' % version, cff)
    cff, n2 = re.subn(r'(?m)^date-released: ".*"$', 'date-released: "%s"' % version, cff)
    if (n1, n2) != (1, 1):
        fail("CITATION.cff has no single version / date-released line to update")
    with open(cff_path, "w", encoding="utf-8") as f:
        f.write(cff)

    print("mirrored version %s: %d blocks; json sha256 %s, csv sha256 %s"
          % (version, len(blocks), sha256(js), sha256(cs)))


if __name__ == "__main__":
    main()
