#!/usr/bin/env python3
"""Small, read-only examples for the documented S19j XP / CV / NAND / 1.3.5 API.

No network request is made unless --base-url is supplied. No miner settings,
authentication flow, credentials, discovery, retries, or redirects are supported.
Only a deliberately selected subset of each response is displayed.
"""

import argparse
import ipaddress
import json
import math
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ENDPOINTS = ("info", "summary", "metrics", "status")
MAX_BYTES = 2 * 1024 * 1024
NETWORKS = tuple(ipaddress.ip_network(n) for n in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "fc00::/7", "::1/128"
))


class ReadError(ValueError):
    """A safe-to-display error without response bodies or credentials."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ReadError("Redirect refused. Use the device's direct local address.")


def build_url(base_url, endpoint, time_slice=None, step=None):
    if endpoint not in ENDPOINTS:
        raise ReadError("Choose info, summary, metrics, or status.")
    try:
        parsed = urlsplit(base_url)
        port = parsed.port
        address = ipaddress.ip_address(parsed.hostname or "")
    except (ValueError, TypeError):
        raise ReadError("Use an explicit local IP address, for example http://192.168.1.20.") from None
    if parsed.scheme not in ("http", "https") or parsed.username is not None or parsed.password is not None:
        raise ReadError("Use HTTP or HTTPS without credentials in the address.")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment or "%" in parsed.netloc:
        raise ReadError("The base address must not contain a path, query, fragment, or IPv6 zone.")
    if not any(address.version == net.version and address in net for net in NETWORKS):
        raise ReadError("This example accepts only RFC1918, IPv6 ULA, or loopback addresses.")
    if port is not None and not 1 <= port <= 65535:
        raise ReadError("Port must be between 1 and 65535.")
    if endpoint != "metrics" and (time_slice is not None or step is not None):
        raise ReadError("time_slice and step are only used by metrics.")
    query = {}
    if time_slice is not None:
        if isinstance(time_slice, bool) or not isinstance(time_slice, int) or not 1 <= time_slice <= 259200:
            raise ReadError("time_slice must be an integer from 1 to 259200 seconds.")
        query["time_slice"] = time_slice
    if step is not None:
        # Positive step is this client's guard. The source gives no numeric minimum.
        if isinstance(step, bool) or not isinstance(step, int) or not 1 <= step <= 2147483647:
            raise ReadError("step must be a positive 32-bit integer in seconds.")
        query["step"] = step
    host = f"[{address}]" if address.version == 6 else str(address)
    origin = f"{parsed.scheme}://{host}" + (f":{port}" if port else "")
    return origin + "/api/v1/" + endpoint + ("?" + urlencode(query) if query else "")


def decode_json(raw):
    if len(raw) > MAX_BYTES:
        raise ReadError("Response exceeds the 2 MiB limit.")
    try:
        return json.loads(raw.decode("utf-8"), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise ReadError("Expected a UTF-8 JSON response.") from None


def fetch(url):
    # Explicitly avoid ambient system/environment proxies and all redirects.
    opener = build_opener(ProxyHandler({}), NoRedirects())
    req = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with opener.open(req, timeout=5) as response:
            if response.status != 200:
                raise ReadError("Expected HTTP 200.")
            return decode_json(response.read(MAX_BYTES + 1))
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise ReadError("Device requires authorization. This example does not send credentials or unlock it.") from None
        raise ReadError(f"Device returned HTTP {exc.code}. Response body was not displayed.") from None
    except (URLError, TimeoutError, OSError):
        raise ReadError("Could not read the device. Check its address, access and certificate.") from None


def object_value(value, label):
    if not isinstance(value, dict):
        raise ReadError(f"Expected an object at {label}.")
    return value


def field(obj, key, kind):
    if key not in obj:
        raise ReadError(f"Missing selected field: {key}.")
    value = obj[key]
    if kind == "number":
        ok = isinstance(value, (int, float)) and not isinstance(value, bool) and (not isinstance(value, float) or math.isfinite(value))
    elif kind == "integer":
        ok = isinstance(value, int) and not isinstance(value, bool)
    else:
        ok = isinstance(value, kind)
    if not ok:
        raise ReadError(f"Unexpected type for selected field: {key}.")
    return value


def project(endpoint, payload):
    """Validate and return a small field subset, not full API schema compliance."""
    obj = object_value(payload, "response")
    if endpoint == "info":
        return {k: field(obj, k, str) for k in (
            "fw_name", "fw_version", "platform", "install_type", "model", "algorithm", "hr_measure"
        )}
    if endpoint == "summary":
        if "miner" not in obj:
            return {"miner": None, "note": "The optional miner field is absent."}
        if obj["miner"] is None:
            return {"miner": None, "note": "The source schema permits miner: null."}
        miner = object_value(obj["miner"], "miner")
        return {"miner": {k: field(miner, k, "number") for k in (
            "hr_average", "hr_realtime", "power_consumption"
        )}, "note": "No hashrate or power unit conversion is performed."}
    if endpoint == "status":
        return {**{k: field(obj, k, bool) for k in (
            "find_miner", "unlocked", "restart_required", "reboot_required"
        )}, "miner_state": field(obj, "miner_state", str),
            "miner_state_time": field(obj, "miner_state_time", "integer")}
    if endpoint == "metrics":
        rows = field(obj, "metrics", list)
        annotations = field(obj, "annotations", list)
        selected = []
        for item in rows:
            item = object_value(item, "metrics[]")
            data = object_value(item.get("data"), "metrics[].data")
            selected.append({"time": field(item, "time", "integer"), "data": {
                "hashrate": field(data, "hashrate", "number"),
                "power_consumption": field(data, "power_consumption", "integer")
            }})
        return {"timezone": field(obj, "timezone", str), "metrics": selected,
                "annotation_count": len(annotations),
                "note": "Unix timestamps and numeric values are kept as received. Units are not inferred."}
    raise ReadError("Unsupported endpoint.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", choices=ENDPOINTS, help="Read an educational local JSON fragment; no network.")
    mode.add_argument("--base-url", help="Explicit local IP of a miner you own or are authorized to read.")
    parser.add_argument("--endpoint", choices=ENDPOINTS)
    parser.add_argument("--time-slice", type=int)
    parser.add_argument("--step", type=int)
    args = parser.parse_args(argv)
    try:
        if args.fixture:
            if args.endpoint is not None or args.time_slice is not None or args.step is not None:
                raise ReadError("Fixture mode does not accept live request options.")
            path = Path(__file__).with_name("fixtures") / (args.fixture + ".json")
            fixture = decode_json(path.read_bytes())
            result = {"source": "Educational fragment, not a miner capture", "endpoint": args.fixture,
                      "selected_fields": project(args.fixture, fixture["payload"])}
        else:
            if not args.endpoint:
                raise ReadError("Supply --endpoint for the one request you want to make.")
            url = build_url(args.base_url, args.endpoint, args.time_slice, args.step)
            result = {"source": "One HTTP GET to the explicitly supplied local device",
                      "endpoint": args.endpoint, "selected_fields": project(args.endpoint, fetch(url))}
        print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
        return 0
    except (ReadError, OSError) as exc:
        print("Error: " + (str(exc) if isinstance(exc, ReadError) else "Could not read the local fixture."), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
