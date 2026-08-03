from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Header, status

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client.openstack import swift
from skyline_apiserver.client.utils import generate_session
from skyline_apiserver.log import LOG
from skyline_apiserver.types import constants

router = APIRouter()


def _merge_container_info(
    base: Dict[str, Any], cdn: schemas.ObjectStoreContainer
) -> schemas.ObjectStoreContainer:
    return schemas.ObjectStoreContainer(
        name=cdn.name,
        cdn_enabled=cdn.cdn_enabled,
        public_http_url=cdn.public_http_url,
        public_https_url=cdn.public_https_url,
        bytes=base.get("bytes"),
        count=base.get("count"),
        last_modified=base.get("last_modified"),
    )


@router.get(
    "/object-storage/containers",
    description=(
        "List object storage containers enriched with CDN state and public URLs. "
        "The backend issues HEAD requests to the CDN Swift endpoint for each "
        "container and normalizes the CDN headers into JSON."
    ),
    responses={
        200: {"model": schemas.ObjectStoreContainers},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.ObjectStoreContainers,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def list_containers(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.ObjectStoreContainers:
    session = await generate_session(profile)
    raw_containers: List[Dict[str, Any]] = await swift.list_containers(
        profile, session, x_openstack_request_id
    )

    async def enrich(item: Dict[str, Any]) -> schemas.ObjectStoreContainer:
        name = item.get("name", "")
        try:
            cdn = await swift.get_container_cdn(profile, session, name)
        except Exception as e:
            # Never let a single container's CDN lookup break the whole list.
            LOG.warning(f"Failed to read CDN info for container {name}: {e}")
            cdn = schemas.ObjectStoreContainer(name=name, cdn_enabled=False)
        return _merge_container_info(item, cdn)

    # Batch the CDN HEAD requests concurrently to keep the list page fast.
    containers = await asyncio.gather(*[enrich(item) for item in raw_containers])
    return schemas.ObjectStoreContainers(containers=list(containers))


@router.get(
    "/object-storage/containers/{container_id}",
    description="Get a single object storage container with its CDN state and public URLs.",
    responses={
        200: {"model": schemas.ObjectStoreContainer},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.ObjectStoreContainer,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def show_container(
    container_id: str,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.ObjectStoreContainer:
    session = await generate_session(profile)
    return await swift.get_container_cdn(profile, session, container_id)


@router.put(
    "/object-storage/containers/{container_id}/cdn",
    description=(
        "Enable or disable CDN for an object storage container. The backend "
        "translates this into a PUT with the X-CDN-Enabled header to the CDN "
        "Swift endpoint, then re-reads the state via HEAD and returns it."
    ),
    responses={
        200: {"model": schemas.ObjectStoreContainer},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.ObjectStoreContainer,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def update_container_cdn(
    container_id: str,
    cdn: schemas.UpdateContainerCDN,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.ObjectStoreContainer:
    session = await generate_session(profile)
    return await swift.set_container_cdn(profile, session, container_id, cdn.enabled)
