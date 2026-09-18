# The Solo Block Record

Every solo-mined Bitcoin block found by a small or home miner that could be verified on-chain, across all public solo pools.

This repository is a daily mirror of the dataset that SoloLuck.io publishes at **https://sololuck.io/legends**, so it can be downloaded, versioned and cited from GitHub. The site is the canonical source, and every block also has its own page there (`https://sololuck.io/legends/<height>`).

| | |
|---|---|
| Rows | One per block, newest first. The count is the `count` field in `data/blocks.json`. |
| Formats | `data/blocks.csv` and `data/blocks.json` |
| Licence | [CC BY 4.0](LICENSE) |
| Version | The `version` field in `data/blocks.json` (a date) |
| Updates | Checked daily. A commit appears only when the record changes. |
| Source | `https://sololuck.io/api/legends/v1/blocks.json` and `blocks.csv` |

## Files

- `data/blocks.csv`: one row per block. It is UTF-8 and comma-separated, with a header row. An empty cell means the value is unknown.
- `data/blocks.json`: the same rows under `blocks`, plus the publisher's metadata: `version`, `method`, `inclusion`, `license`, `cite_as`, `corrections` and the CSV's `csv_sha256`. An unknown value is `null`.
- `datapackage.json`: a [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/) describing both files, with field types, byte counts and sha256 hashes.
- `CITATION.cff`: citation metadata, which GitHub shows as "Cite this repository".
- `scripts/mirror.py` and `.github/workflows/mirror.yml`: the daily mirror.

## What is in it

The record holds solo-mined Bitcoin blocks found by small or home miners on public solo pools. Rented-hashrate services such as NiceHash EasyMining are left out on purpose, and so are industrial-scale wins. Some entries are blocks that no pool registry attributes, found by auditing unattributed coinbases. Where such an inference, rather than the miner's own word, is the basis for an entry, its `note` says so.

Each block is checked on the chain itself (mempool.space) and linked to the source that reported it. Hashrates are as the miner, the pool operator or the press published them at the time. Where a winner never published one, the hashrate and every figure derived from it are left empty rather than guessed. The odds are recomputed the same way for every row, from the network difficulty at that height.

The `inclusion` and `method` fields in `data/blocks.json` hold the publisher's own wording. They are authoritative; the summary above is a convenience.

## Data dictionary

| Field | Type | Meaning |
|---|---|---|
| `height` | integer | Block height. Unique. |
| `date` | date, `YYYY-MM-DD` | Date the block was mined, UTC. |
| `pool` | string | Where the block was found: the pool named by the coinbase or by the report, or `untagged coinbase` when the coinbase carries no pool tag. |
| `hardware` | string | The winner's hardware or hashrate as publicly reported, in words. `hashrate not publicly reported` when the winner never published one. |
| `hashrate_hs` | number, may be empty | Hashrate in hashes per second, as published at the time by the miner, the pool operator or the press. |
| `difficulty` | number | Network difficulty at that height, as recorded. Most rows are rounded to five or six significant figures; a few carry full precision. |
| `reward_btc` | number | Total block reward in BTC: subsidy plus fees. |
| `reward_usd_reported` | string, may be empty | The reward's US dollar value as reported at the time, as free text (for example `≈ $300,000 then`). |
| `expected_seconds_per_block` | number, may be empty | Expected seconds for that hashrate to find a block at that difficulty: `difficulty × 2^32 / hashrate_hs`. |
| `chance_per_day` | number, may be empty | Probability of finding a block within one day at that hashrate: `1 − e^(−86400 / expected_seconds_per_block)`. |
| `chance_per_day_one_in` | integer, may be empty | The same daily chance written as "1 in N": `round(1 / chance_per_day)`. |
| `source_label` | string | The source that reported the block. |
| `source_url` | URL | Link to that source. |
| `block_url` | URL | The block on mempool.space. |
| `story` | string | A short account of the block, in English. |
| `note` | string, may be empty | Caveats, for example when an entry is inferred from the payout pattern rather than declared by the miner. |

The three odds fields are empty exactly when `hashrate_hs` is empty.

## How the mirror works

Once a day, `.github/workflows/mirror.yml` runs `scripts/mirror.py`. The script downloads `blocks.json` and `blocks.csv` from sololuck.io and checks them against each other before writing anything:

- the CSV must match the `csv_sha256` published inside the JSON;
- the JSON's `count` must match its rows;
- both files must list the same blocks, with the columns documented above.

A copy that fails a check stops the run, and nothing is committed. The workflow contacts nothing but sololuck.io, and it commits only when the record has changed.

## Citing

Use the `cite_as` field in `data/blocks.json`, which carries the current version. It reads:

> SoloLuck.io, "The Solo Block Record", version *(the `version` field)*, https://sololuck.io/legends (CC BY 4.0)

## Corrections

Errors are fixed at the source. Report them at https://sololuck.io/contact (the dataset's `corrections` field), and the fix appears here with the next daily mirror.

## About the publisher

SoloLuck.io runs a 0% fee solo mining pool. The record covers solo blocks from every public solo pool, whichever one found them. As of September 2026 SoloLuck has not found a Bitcoin block itself, so no entry in the record is SoloLuck's.

## Licence

The data is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/); see `LICENSE`. Please credit "SoloLuck.io, The Solo Block Record" and link to https://sololuck.io/legends.
