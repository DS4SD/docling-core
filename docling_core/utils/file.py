#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""File-related utilities."""

import importlib
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, TypeAdapter, ValidationError


class DocumentStream(BaseModel):
    """Wrapper class for a bytes stream with a filename."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    stream: BytesIO


def read_file_source(
    source: Union[Path, AnyHttpUrl, str], headers: Optional[Dict[str, str]] = None
) -> DocumentStream:
    """Resolves the source (URL, path) of a file to a binary stream.

    Args:
        source (Path | AnyHttpUrl | str): The file input source. Can be a path or URL.
        headers (Dict | None): Optional set of headers to use for fetching
            the remote URL.

    Raises:
        ValueError: If source is of unexpected type.

    Returns:
        DocumentStream: The resolved file loaded as a stream.
    """
    try:
        http_url: AnyHttpUrl = TypeAdapter(AnyHttpUrl).validate_python(source)

        # make all header keys lower case
        _headers = headers or {}
        req_headers = {k.lower(): v for k, v in _headers.items()}
        # add user-agent is not set
        if "user-agent" not in req_headers:
            agent_name = f"docling-core/{importlib.metadata.version('docling-core')}"
            req_headers["user-agent"] = agent_name

        # fetch the page
        res = requests.get(http_url, stream=True, headers=req_headers)
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
            fname = Path(http_url.path or "").name or "file"

        stream = BytesIO(res.content)
        doc_stream = DocumentStream(name=fname, stream=stream)
    except ValidationError:
        try:
            local_path = TypeAdapter(Path).validate_python(source)
            stream = BytesIO(local_path.read_bytes())
            doc_stream = DocumentStream(name=local_path.name, stream=stream)
        except ValidationError:
            raise ValueError(f"Unexpected source type encountered: {type(source)}")
    return doc_stream


def resolve_file_source(
    source: Union[Path, AnyHttpUrl, str],
    headers: Optional[Dict[str, str]] = None,
    workdir: Optional[Path] = None,
) -> Path:
    """Resolves the source (URL, path) of a file to a local file path.

    If a URL is provided, the content is first downloaded to a temporary local file.

    Args:
        source (Path | AnyHttpUrl | str): The file input source. Can be a path or URL.
        headers (Dict | None): Optional set of headers to use for fetching
            the remote URL.
        workdir (Path | None): If set, the work directory where the file will
            be downloaded, otherwise a temp dir will be used.

    Raises:
        ValueError: If source is of unexpected type.

    Returns:
        Path: The local file path.
    """
    doc_stream = read_file_source(source=source, headers=headers)

    # use a temporary directory if not specified
    if workdir is None:
        workdir = Path(tempfile.mkdtemp())

    # create the parent workdir if it doesn't exist
    workdir.mkdir(exist_ok=True, parents=True)

    # save result to a local file
    local_path = workdir / doc_stream.name
    with local_path.open("wb") as f:
        f.write(doc_stream.stream.read())

    return local_path


def relative_path(src: Path, target: Path) -> Path:
    """Compute the relative path from `src` to `target`.

    Args:
        src (str | Path): The source directory or file path (must be absolute).
        target (str | Path): The target directory or file path (must be absolute).

    Returns:
        Path: The relative path from `src` to `target`.

    Raises:
        ValueError: If either `src` or `target` is not an absolute path.
    """
    src = Path(src).resolve()
    target = Path(target).resolve()

    # Ensure both paths are absolute
    if not src.is_absolute():
        raise ValueError(f"The source path must be absolute: {src}")
    if not target.is_absolute():
        raise ValueError(f"The target path must be absolute: {target}")

    # Find the common ancestor
    common_parts = []
    for src_part, target_part in zip(src.parts, target.parts):
        if src_part == target_part:
            common_parts.append(src_part)
        else:
            break

    # Determine the path to go up from src to the common ancestor
    up_segments = [".."] * (len(src.parts) - len(common_parts))

    # Add the path from the common ancestor to the target
    down_segments = target.parts[len(common_parts) :]

    # Combine and return the result
    return Path(*up_segments, *down_segments)
