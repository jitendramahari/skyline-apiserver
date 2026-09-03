# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FreezerJobSchedule(BaseModel):
    schedule_start_date: Optional[str] = None
    schedule_interval: Optional[str] = None
    schedule_end_date: Optional[str] = None


class FreezerJobCreate(BaseModel):
    description: str
    job_actions: List[Dict[str, Any]] = Field(default_factory=list)
    job_schedule: FreezerJobSchedule = Field(default_factory=FreezerJobSchedule)
    client_id: str


class FreezerJobResponse(BaseModel):
    job_id: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[str] = None
    job_schedule: Optional[Dict[str, Any]] = None
    job_actions: Optional[List[Dict[str, Any]]] = None


class FreezerJobsResponse(BaseModel):
    jobs: List[Dict[str, Any]] = Field(default_factory=list)


class FreezerActionCreate(BaseModel):
    freezer_action: Dict[str, Any]
    max_retries: Optional[int] = None
    max_retries_interval: Optional[int] = None
    mandatory: Optional[bool] = None


class FreezerActionResponse(BaseModel):
    action_id: Optional[str] = None
    freezer_action: Optional[Dict[str, Any]] = None


class FreezerActionsResponse(BaseModel):
    actions: List[Dict[str, Any]] = Field(default_factory=list)


class FreezerClientResponse(BaseModel):
    client_id: Optional[str] = None
    hostname: Optional[str] = None
    uuid: Optional[str] = None
    project_id: Optional[str] = None


class FreezerClientsResponse(BaseModel):
    clients: List[Dict[str, Any]] = Field(default_factory=list)


class FreezerBackupRestore(BaseModel):
    backup_id: str
    client: str
    path: Optional[str] = Field(None, description="Restore path (fs/db modes)")
    network_id: Optional[str] = Field(
        None, description="Network UUID to attach the restored Nova VM"
    )


class FreezerBackupsResponse(BaseModel):
    backups: List[Dict[str, Any]] = Field(default_factory=list)


class FreezerCreatedResponse(BaseModel):
    id: str


class FreezerMessageResponse(BaseModel):
    message: str


class FreezerEnableBackupRequest(BaseModel):
    """Request body for POST /extension/freezer/enable-backup.

    Option D (username/password): the caller supplies the password because
    Skyline cannot derive it from the login token. username/project/domains
    default to the caller's profile when omitted.
    """
    instance_id: str = Field(..., description="Nova instance UUID")
    instance_name: str = Field(..., description="Human-readable VM name used as client_id")
    password: str = Field(..., description="Password for the backup scheduler identity")
    username: Optional[str] = Field(None, description="Defaults to the caller's username")
    project_id: Optional[str] = Field(None, description="Defaults to the caller's project id")
    user_domain_name: Optional[str] = Field(
        None, description="Defaults to the caller's user domain"
    )
    project_domain_name: Optional[str] = Field(
        None, description="Defaults to the caller's project domain"
    )


class FreezerEnableBackupResponse(BaseModel):
    """Returned when create-time backup enablement is prepared for a VM.

    Only ``user_data`` is meaningful: it is the cloud-init payload the console
    injects into the Nova boot request (with config-drive) for a
    Skyline-created VM. No credential-bearing script is returned to the browser
    for the post-creation case — that path is documented for manual install.
    """
    instance_id: str
    instance_name: str
    project_id: str
    # Cloud-init user-data string — inject into Nova at create time
    # for Skyline-created VMs.
    user_data: str


class FreezerDisableBackupRequest(BaseModel):
    """Request body for POST /extension/freezer/disable-backup.

    Disable is a password-less, control-plane pause: the caller's session
    token is used to stop the client's scheduled jobs on the Freezer API.
    Existing backups in object storage are retained.
    """
    instance_id: str = Field(..., description="Nova instance UUID")
    client_id: Optional[str] = Field(
        None,
        description=(
            "Freezer client_id whose jobs should be paused. Defaults to the "
            "instance name used at enable time."
        ),
    )


class FreezerResumeBackupRequest(BaseModel):
    """Request body for POST /extension/freezer/resume-backup.

    Resume re-activates a previously paused client's jobs. Only valid when the
    agent is already installed on the VM (i.e. it was enabled at create time).
    Password-less — no in-guest change is needed.
    """
    instance_id: str = Field(..., description="Nova instance UUID")
    client_id: Optional[str] = Field(
        None,
        description="Freezer client_id whose jobs should be resumed.",
    )
