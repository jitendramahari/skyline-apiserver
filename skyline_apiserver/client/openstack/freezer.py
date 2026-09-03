# Copyright 2024 99cloud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.session import Session
from starlette.concurrency import run_in_threadpool

from skyline_apiserver import schemas
from skyline_apiserver.client import utils


async def list_jobs(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    limit: int = 500,
    offset: int = 0,
    search: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(
            lambda: fc.jobs.list_all(
                limit=limit,
                offset=offset,
                search=search,
            )
        )
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def get_job(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    job_id: str,
) -> Dict[str, Any]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.jobs.get, job_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def create_job(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    job: Dict[str, Any],
) -> str:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.jobs.create, job)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_job(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    job_id: str,
) -> None:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.jobs.delete, job_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def start_job(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    job_id: str,
) -> None:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.jobs.start_job, job_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def stop_job(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    job_id: str,
) -> None:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.jobs.stop_job, job_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def list_actions(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    limit: int = 500,
    offset: int = 0,
    search: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(
            lambda: fc.actions.list(
                limit=limit,
                offset=offset,
                search=search,
            )
        )
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def get_action(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    action_id: str,
) -> Dict[str, Any]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.actions.get, action_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def create_action(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    action: Dict[str, Any],
) -> str:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.actions.create, action)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_action(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    action_id: str,
) -> None:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.actions.delete, action_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def list_clients(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    limit: int = 500,
    offset: int = 0,
    search: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(
            lambda: fc.clients.list(
                limit=limit,
                offset=offset,
                search=search,
            )
        )
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def get_client(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    client_id: str,
) -> Dict[str, Any]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.clients.get, client_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_client(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    client_id: str,
) -> None:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.clients.delete, client_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def list_backups(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    limit: int = 500,
    offset: int = 0,
    search: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(
            lambda: fc.backups.list(
                limit=limit,
                offset=offset,
                search=search,
            )
        )
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_backup(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    backup_id: str,
) -> None:
    try:
        fc = await utils.freezer_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(fc.backups.delete, backup_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
