## Deployment update: 18 September 2026

The API reference pages and example archive are now published:

- [English reference](https://vnish.global/academy/developers/miner-api-1-3-5/)
- [Русский справочник](https://vnish.global/ru/academy/developers/miner-api-1-3-5/)
- [Download the example ZIP](https://vnish.global/academy/developers/miner-api-1-3-5/vnish-global-api-read-examples-1.0.0.zip)

Public checks on 18 September 2026 returned HTTP 200 for all three files. All 3 of 3 matched the prepared release by SHA-256 and byte count, and the ZIP integrity check passed. This confirms publication, not testing on physical miners.

**The original pre-deployment snapshot is preserved unchanged below. Its planned-publication wording records the earlier state.**

---

# VNISH GLOBAL: four read-only miner API examples

**Publication status: source package prepared for review. The planned VNISH GLOBAL reference pages below are NOT YET DEPLOYED.**

Planned English reference (NOT YET DEPLOYED): https://vnish.global/academy/developers/miner-api-1-3-5/

Планируемый русский справочник (NOT YET DEPLOYED, пока не опубликован): https://vnish.global/ru/academy/developers/miner-api-1-3-5/

This source package does not establish that those web pages are live. The examples and local tests can be used independently of the planned pages.

These original Python examples explain four documented GET operations. The source was the API document inside `vnish-s19j-xp-cv-nand-v1.3.5.tar.gz`, for S19j XP / CV / NAND / firmware 1.3.5. They have not been tested against an ASIC. They are not a universal compatibility claim or a full SDK.

The firmware package is listed at https://vnish.global/install/s19j-xp-cv-nand/. Its SHA-256 is `58d2b534595532214f19676f9eba6cd3ac1a9e59ede5eb519a3a8d2129f04dc3`. The API document SHA-256 is `8bc6ed02457447d4d2d96def8cc8866d03a8c35edd8e496eb50b22b8230a1ebc`. The original API document is not redistributed here. Its `info.version` is `0.1.0`; that is documentation metadata, not a replacement for firmware version `1.3.5`.

## Run without a miner

Requires Python 3.9 or newer. There are no third-party dependencies.

```sh
python3 miner_read.py --fixture info
python3 miner_read.py --fixture summary
python3 miner_read.py --fixture metrics
python3 miner_read.py --fixture status
python3 -m unittest discover -s tests -v
```

The four fixtures are manually written educational **fragments**, not captured responses. They illustrate selected fields, not every property required by the original schemas. Zero values are placeholders, not measured operating data. The summary fixture intentionally demonstrates `miner: null`.

## Read one device

Use the exact local IP address of a miner you own or are authorized to read. Replace the example address before running a command. Nothing is requested until an address and endpoint are supplied.

```sh
python3 miner_read.py --base-url http://192.168.1.20 --endpoint info
python3 miner_read.py --base-url http://192.168.1.20 --endpoint summary
python3 miner_read.py --base-url http://192.168.1.20 --endpoint status
python3 miner_read.py --base-url http://192.168.1.20 --endpoint metrics --time-slice 3600 --step 60
```

The program makes **one HTTP GET**. It does not scan the network, retry, follow redirects, use ambient proxies, log in, unlock the miner, send credentials, or change settings. Only literal RFC1918 IPv4, IPv6 ULA, and loopback addresses are supported. Loopback is useful for a local test server. HTTPS uses normal certificate verification; the program does not disable it.

A 401 or 403 stops the request. Use the access method approved for your installation; this small example deliberately does not implement authentication. The `/summary` operation's source document declares empty, bearer, and API-key security alternatives. That is not proof that a running device permits unauthenticated reads. The other three source operations do not explicitly declare security requirements.

Only selected fields are printed. Serial numbers, the `system` object, pool details, authentication data, and raw response bodies are not printed. Output is not uploaded anywhere. This limited projection is not a general-purpose redactor for arbitrary files and is not full API schema validation.

## Endpoint notes

The base path is `/api/v1` on the miner. It is separate from the public firmware catalog on `vnish.global`.

| GET path | Selected information | Important limit |
| --- | --- | --- |
| `/info` | Firmware name/version, platform, installation type, model, algorithm, hashrate measure | Compare the real device to the package you are documenting. |
| `/summary` | `miner.hr_average`, `miner.hr_realtime`, `miner.power_consumption` | `miner` can be null; its property is not marked required in the source. Missing data is not zero. |
| `/metrics` | Timezone, Unix timestamps, hashrate and power values, annotation count | Units are not explicitly stated for these numeric fields in the source. Values are not converted. |
| `/status` | Miner state, time in state, locate/screen-lock flags, restart/reboot-required flags | Flags are status data, not instructions to reboot or restart. |

For `/metrics`, source defaults are 86400 seconds for `time_slice` and 900 seconds for `step`. The documented maximum `time_slice` is 259200 seconds. This example adds a positive-integer guard and enforces the declared 32-bit integer type for `step`; the document gives no numeric minimum for it.

The `/metrics` HTTP 200 description in the source says “Config saved successfully”, although the operation is GET and its response schema is metrics. We use the method and schema to describe it and do not treat that description as evidence of a write action.

`hr_measure` on `/info` can be `GH/s`, `MH/s`, or `N/A`. Confirm the unit and meaning of each measured field on the actual device before converting or comparing it. The example never silently rescales numeric values. The source marks `average_hashrate`, `instant_hashrate`, and `power_usage` as deprecated; they are not used here.

## Scope of verification

The offline tests cover endpoint restrictions, address validation, query bounds, one GET with timeout, rejection of redirects, fixture isolation from the network, response size/JSON errors, 401 handling, selected-field types, missing/null summary data, and absence of identifier fields in the selected output. No firmware was flashed and no ASIC was contacted during this verification.

## License

The original example code, fixtures, and explanation in this folder use the MIT License in `LICENSE`. That license does not apply to firmware or third-party API documents.
