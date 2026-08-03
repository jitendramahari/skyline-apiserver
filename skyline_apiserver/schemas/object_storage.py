from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ObjectStoreContainer(BaseModel):
    name: str = Field(..., description="Container name")
    cdn_enabled: bool = Field(False, description="Whether CDN is enabled for the container")
    public_http_url: Optional[str] = Field(
        None, description="Public HTTP URL exposed by the CDN (X-CDN-URI)"
    )
    public_https_url: Optional[str] = Field(
        None, description="Public HTTPS URL exposed by the CDN (X-CDN-SSL-URI)"
    )
    bytes: Optional[int] = Field(None, description="Total bytes used by the container")
    count: Optional[int] = Field(None, description="Number of objects in the container")
    last_modified: Optional[str] = Field(None, description="Last modified time of the container")

    class Config:
        schema_extra = {
            "example": {
                "name": "cdn_test",
                "cdn_enabled": True,
                "public_http_url": "http://ce6b30f.rackcdn.com",
                "public_https_url": "https://2971bf.ssl.f100.rackcdn.com",
            },
        }


class ObjectStoreContainers(BaseModel):
    containers: List[ObjectStoreContainer] = Field(..., description="Containers")


class UpdateContainerCDN(BaseModel):
    enabled: bool = Field(..., description="Enable or disable CDN for the container")

    class Config:
        schema_extra = {"example": {"enabled": True}}
