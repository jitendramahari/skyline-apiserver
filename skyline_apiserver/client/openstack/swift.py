from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
from fastapi import HTTPException, status
from keystoneauth1.session import Session

from skyline_apiserver import schemas
from skyline_apiserver.client import utils
from skyline_apiserver.config import CONF
from skyline_apiserver.types import constants


# Port the CDN-enabled Swift service listens on.
CDN_SWIFT_PORT = 8444
# Hostname label of the CDN Swift service. The object-store endpoint host only
# differs from the CDN host by its first label, e.g.
#   object-store: swift.api.dev.dfw3.rackspacecloud.com
#   cdn-swift:    cdn-swift.api.dev.dfw3.rackspacecloud.com
CDN_SWIFT_HOST_LABEL = "cdn-swift"


def _derive_cdn_netloc(storage_host: str) -> str:
    """Derive the CDN Swift host from the object-store host.

    The environment/region (e.g. ``dev.dfw3``) lives in the object-store host
    that Keystone returns, so we only need to swap the first hostname label for
    ``cdn-swift`` and target the CDN port. This keeps the CDN endpoint correct
    across environments (dev.dfw3, iad3, sjc3, ...) without any configuration.
    """
    # Strip any existing port; the CDN service uses its own port.
    host = storage_host.split("@")[-1].split(":")[0]
    labels = host.split(".")
    if len(labels) > 1:
        labels[0] = CDN_SWIFT_HOST_LABEL
        cdn_host = ".".join(labels)
    else:
        cdn_host = CDN_SWIFT_HOST_LABEL
    return f"{cdn_host}:{CDN_SWIFT_PORT}"


def _build_cdn_container_url(storage_url: str, container: str) -> str:
    """Build the CDN Swift container URL.

    The account path (``/v1/AUTH_<account_id>``) and the environment are taken
    from the object-store endpoint registered in Keystone. Only the hostname's
    first label is swapped to ``cdn-swift`` and the CDN port is applied. An
    explicit ``cdn_swift_endpoint`` config value, if set, overrides the derived
    scheme/host.
    """
    storage_parts = urlsplit(storage_url)

    cdn_override = CONF.openstack.cdn_swift_endpoint
    if cdn_override:
        cdn_parts = urlsplit(cdn_override)
        cdn_scheme = cdn_parts.scheme or storage_parts.scheme or "https"
        cdn_netloc = cdn_parts.netloc
    else:
        cdn_scheme = storage_parts.scheme or "https"
        cdn_netloc = _derive_cdn_netloc(storage_parts.netloc)

    # Reuse the account path from the object-store endpoint, but swap in the
    # CDN host/scheme so that the CDN service handles the request.
    account_path = storage_parts.path.rstrip("/")
    container_path = f"{account_path}/{quote(container)}"

    return urlunsplit((cdn_scheme, cdn_netloc, container_path, "", ""))


async def _get_storage_url(session: Session, region: str) -> str:
    try:
        return await utils.get_endpoint(
            region=region,
            service="object-store",
            session=session,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to resolve object-store endpoint: {e}",
        )


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in ("true", "1", "yes", "on", "t")


def _normalize_cdn_headers(name: str, headers: Any) -> schemas.ObjectStoreContainer:
    """Translate raw CDN Swift response headers into a JSON-friendly schema."""
    # httpx headers are case-insensitive.
    cdn_enabled = _parse_bool(headers.get("x-cdn-enabled"))
    public_http_url = headers.get("x-cdn-uri") or None
    public_https_url = headers.get("x-cdn-ssl-uri") or None
    return schemas.ObjectStoreContainer(
        name=name,
        cdn_enabled=cdn_enabled,
        public_http_url=public_http_url if cdn_enabled else None,
        public_https_url=public_https_url if cdn_enabled else None,
    )


def _raise_for_cdn_status(container: str, response: httpx.Response) -> None:
    code = response.status_code
    if code < 400:
        return
    if code in (status.HTTP_401_UNAUTHORIZED,):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token for CDN service.",
        )
    if code in (status.HTTP_403_FORBIDDEN,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied for CDN operation.",
        )
    if code in (status.HTTP_404_NOT_FOUND,):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Container "{container}" not found.',
        )
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Upstream CDN service returned an error (status {code}).",
    )


async def get_container_cdn(
    profile: schemas.Profile,
    session: Session,
    container: str,
) -> schemas.ObjectStoreContainer:
    """Read the CDN state and public URLs for a container using HEAD."""
    storage_url = await _get_storage_url(session, profile.region)
    url = _build_cdn_container_url(storage_url, container)
    headers = {"X-Auth-Token": profile.keystone_token}
    try:
        async with httpx.AsyncClient(
            verify=CONF.default.cafile or True,
            timeout=constants.DEFAULT_TIMEOUT,
        ) as client:
            response = await client.head(url, headers=headers)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out while contacting the CDN service.",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact the CDN service: {e}",
        )
    _raise_for_cdn_status(container, response)
    return _normalize_cdn_headers(container, response.headers)


async def set_container_cdn(
    profile: schemas.Profile,
    session: Session,
    container: str,
    enabled: bool,
) -> schemas.ObjectStoreContainer:
    """Enable or disable CDN for a container using PUT, then re-read via HEAD."""
    storage_url = await _get_storage_url(session, profile.region)
    url = _build_cdn_container_url(storage_url, container)
    headers = {
        "X-Auth-Token": profile.keystone_token,
        "X-CDN-Enabled": "True" if enabled else "False",
    }
    try:
        async with httpx.AsyncClient(
            verify=CONF.default.cafile or True,
            timeout=constants.DEFAULT_TIMEOUT,
        ) as client:
            response = await client.put(url, headers=headers)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out while contacting the CDN service.",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact the CDN service: {e}",
        )
    _raise_for_cdn_status(container, response)
    # Confirm the final state from the authoritative HEAD response.
    return await get_container_cdn(profile, session, container)


async def list_containers(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
) -> List[Dict[str, Any]]:
    """List the account's containers from the object-store service."""
    storage_url = await _get_storage_url(session, profile.region)
    headers = {"X-Auth-Token": profile.keystone_token}
    try:
        async with httpx.AsyncClient(
            verify=CONF.default.cafile or True,
            timeout=constants.DEFAULT_TIMEOUT,
        ) as client:
            response = await client.get(
                storage_url,
                headers=headers,
                params={"format": "json"},
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out while contacting the object storage service.",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact the object storage service: {e}",
        )
    if response.status_code >= 400:
        _raise_for_cdn_status("", response)
    try:
        return response.json()
    except ValueError:
        return []
