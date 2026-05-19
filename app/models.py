from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GrafanaLabel(BaseModel):
    alertname: Optional[str] = None
    team: Optional[str] = None
    zone: Optional[str] = None
    apps: Optional[str] = None

    class Config:
        extra = "allow"

class GrafanaAnnotation(BaseModel):
    description: Optional[str] = None
    summary: Optional[str] = None
    runbook_url: Optional[str] = None

    class Config:
        extra = "allow"

class GrafanaAlert(BaseModel):
    status: Optional[str] = None
    labels: GrafanaLabel
    annotations: GrafanaAnnotation
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None
    generatorURL: Optional[str] = None
    silenceURL: Optional[str] = None
    dashboardURL: Optional[str] = None
    panelURL: Optional[str] = None
    values: Optional[Dict[str, Any]] = None

class GrafanaWebhookPayload(BaseModel):
    receiver: Optional[str] = None
    status: Optional[str] = None
    orgId: Optional[int] = None
    alerts: List[GrafanaAlert]
    groupLabels: Optional[Dict[str, Any]] = None
    commonLabels: Optional[Dict[str, Any]] = None
    commonAnnotations: Optional[Dict[str, Any]] = None
    externalURL: Optional[str] = None
    version: Optional[str] = None
    groupKey: Optional[str] = None
    truncatedAlerts: Optional[int] = None
    title: Optional[str] = None
    state: Optional[str] = None
    message: Optional[str] = None