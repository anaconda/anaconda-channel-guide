from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

MAIN_X_CHANNEL_URL = "https://repo.anaconda.cloud/repo/main-x"
SPECS = [
    "pychoir",
    "tencentcloud-sdk-python >=3.1.50,<3.1.100",
    "__does_not_exist",
    "opentelemetry-instrumentation>0.57",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=["drop-cache", "expire-cache", "show-cache", "search"],
        nargs="?",
    )
    parser.add_argument(
        "--use-index-cache",
        action="store_true",
        help="Match the plugin PNFE lookup path.",
    )
    args = parser.parse_args()

    if args.action is None:
        return benchmark()
    if args.action == "search":
        return search(args.use_index_cache)
    if args.action == "show-cache":
        return show_cache()
    if args.action == "drop-cache":
        return drop_cache()
    return expire_cache()


def benchmark() -> int:
    from conda.base.context import context, reset_context

    reset_context()
    python = shlex.quote(sys.executable)
    script = shlex.quote(str(Path(__file__).resolve()))
    subdirs = (context.subdir, "noarch") if context.subdir else ("noarch",)
    prefetch = " ".join(
        [
            python,
            "-m",
            "anaconda_channel_guide.prefetch",
            *(shlex.quote(subdir) for subdir in subdirs),
        ]
    )
    search_command = f"{python} {script} search"
    cases = [
        (
            "Cold normal lookup: no local main-x cache, pays network/download cost",
            [
                "--runs",
                "5",
                "--prepare",
                f"{python} {script} drop-cache",
                search_command,
            ],
        ),
        (
            "Fresh-cache normal lookup: cache file exists and is within Cache-Control max-age",
            ["--runs", "20", search_command],
        ),
        (
            "Expired-cache normal lookup: Conda may revalidate with ETag/304",
            [
                "--runs",
                "10",
                "--prepare",
                f"{python} {script} expire-cache",
                search_command,
            ],
        ),
        (
            "Expired-cache PNFE lookup: use_index_cache=True, local file only",
            [
                "--runs",
                "20",
                "--prepare",
                f"{python} {script} expire-cache",
                f"{search_command} --use-index-cache",
            ],
        ),
        (
            "Cold background prefetch child: pays the fetch cost before PNFE needs it",
            [
                "--runs",
                "5",
                "--prepare",
                f"{python} {script} drop-cache",
                prefetch,
            ],
        ),
    ]

    print("Meaning:")
    print("- workaround: this exists because main/main-x do not have sharded repodata yet")
    print("- cold normal: no usable local cache; this is the visible delay we are avoiding")
    print("- expired normal: cache file exists, but Conda may still check the server")
    print("- PNFE cache-only: plugin path uses the local cache without revalidation")
    print("- prefetch: moves the cold fetch cost to a background process")
    print()
    show_cache()
    for title, args in cases:
        print(f"\n== {title} ==", flush=True)
        subprocess.run(["hyperfine", *args], check=True)  # noqa: S603,S607
    return 0


def main_x_cache_infos() -> list[tuple[Path, dict[str, Any]]]:
    from conda.base.context import context, reset_context

    reset_context()
    results = []
    for root in map(Path, context.pkgs_dirs):
        cache = root / "cache"
        if not cache.exists():
            continue
        for path in cache.glob("*.info.json"):
            try:
                data = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if data.get("url", "").startswith(MAIN_X_CHANNEL_URL):
                results.append((path, data))
    return results


def drop_cache() -> int:
    for info, _data in main_x_cache_infos():
        repodata = info.with_name(info.name.removesuffix(".info.json") + ".json")
        state = info.with_name(info.name.removesuffix(".info.json") + ".state.json")
        for path in (info, repodata, state):
            path.unlink(missing_ok=True)
    return 0


def expire_cache() -> int:
    for info, data in main_x_cache_infos():
        data["refresh_ns"] = 0
        info.write_text(json.dumps(data, sort_keys=True))
    return 0


def show_cache() -> int:
    from conda.base.context import context

    print(f"local_repodata_ttl: {context.local_repodata_ttl}")
    for info, data in main_x_cache_infos():
        repodata = info.with_name(info.name.removesuffix(".info.json") + ".json")
        print(info)
        print(f"url: {data.get('url')}")
        print(f"cache_control: {data.get('cache_control')}")
        print(f"refresh_ns: {data.get('refresh_ns')}")
        print(f"size: {data.get('size')}")
        print(f"repodata_exists: {repodata.exists()}")
    return 0


def search(use_index_cache: bool) -> int:
    from conda.base.context import context, reset_context
    from conda.core.subdir_data import SubdirData
    from conda.models.channel import Channel
    from conda.models.match_spec import MatchSpec

    reset_context()
    main_x_channel = Channel.from_url(MAIN_X_CHANNEL_URL)
    subdirs = (context.subdir, "noarch") if context.subdir else ("noarch",)
    start = time.perf_counter()

    with context._override("use_index_cache", use_index_cache):
        for spec in SPECS:
            match_spec = MatchSpec(spec)
            records = SubdirData.query_all(
                match_spec.name,
                channels=[main_x_channel],
                subdirs=subdirs,
            )
            print(f"{match_spec.name}: {len(records)}")

    print(f"elapsed: {time.perf_counter() - start:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
