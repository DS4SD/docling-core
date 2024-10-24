#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""File-related utilities."""

import random
import tempfile
from pathlib import Path
from typing import Union

import requests
from pydantic import AnyHttpUrl, TypeAdapter, ValidationError


def get_random_headers(custom_headers: list[dict] = []):
    """Pick or create a random request header."""
    if len(custom_headers) > 0:
        return random.choice(custom_headers)

    # List of 10 randomly picked User-Agent headers
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.49",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 OPR/74.0.3911.160",
        "Mozilla/5.0 (Android 11; Mobile; rv:86.0) Gecko/86.0 Firefox/86.0",
        "Mozilla/5.0 (X11; CrOS x86_64 13816.64.0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]

    # Randomly select a User-Agent
    random_user_agent = random.choice(user_agents)

    # Define the headers with the random User-Agent
    headers = {"User-Agent": random_user_agent}
    return headers


def resolve_file_source(
    source: Union[Path, AnyHttpUrl, str], custom_headers: list[dict] = []
) -> Path:
    """Resolves the source (URL, path) of a file to a local file path.

    If a URL is provided, the content is first downloaded to a temporary local file.

    Args:
        source (Path | AnyHttpUrl | str): The file input source. Can be a path or URL.

    Raises:
        ValueError: If source is of unexpected type.

    Returns:
        Path: The local file path.
    """
    try:
        http_url: AnyHttpUrl = TypeAdapter(AnyHttpUrl).validate_python(source)
        headers = get_random_headers(custom_headers)
        res = requests.get(http_url, stream=True, headers=headers)
        res.raise_for_status()
        fname = None
        # try to get filename from response header
        if cont_disp := res.headers.get("Content-Disposition"):
            for par in cont_disp.strip().split(";"):
                # currently only handling directive "filename" (not "*filename")
                if (split := par.split("=")) and split[0].strip() == "filename":
                    fname = "=".join(split[1:]).strip().strip("'\"") or None
                    break
        # otherwise, use name from URL:
        if fname is None:
            fname = Path(http_url.path or "file").name
        local_path = Path(tempfile.mkdtemp()) / fname
        with open(local_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):  # using 1-KB chunks
                f.write(chunk)
    except ValidationError:
        try:
            local_path = TypeAdapter(Path).validate_python(source)
        except ValidationError:
            raise ValueError(f"Unexpected source type encountered: {type(source)}")
    return local_path
