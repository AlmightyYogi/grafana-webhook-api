from fastapi import APIRouter, Header, HTTPException, Depends
from app.models import GrafanaWebhookPayload
from app.database import get_connection
from datetime import datetime
import os
import uuid

router = APIRouter()

HARDCODED = {
    "requestor"      : "B2B IT Operations",
    "requestor_email": "ms-b2b.appl-support@lintasarta.co.id",
    "type"           : "Incident",
    "severity"       : "1 - Emergency (Full Down)",
    "assigned_to"    : "B2B Applications Operations",
    "scope"          : "Infrastructure",
    "status"         : 1,
}

ALLOWED_APPS = [
    "B2B Portal", "MPR", "SQA Portal", "SARAS",
    "SECM Portal", "My Dashboard", "DBEST", "PSSHUB",
    "IOT Middleware TransJakarta"
]

def verify_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("API_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="API key belum dikonfigurasi di server")
    if x_api_key != expected:
        raise HTTPException(status_code=403, detail="API key tidak valid")
    return x_api_key

def parse_grafana_datetime(starts_at: str):
    try:
        dt_clean = starts_at[:19]
        dt = datetime.strptime(dt_clean, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")
    except Exception:
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

def generate_incident_code(cursor, report_type: str) -> str:
    prefix = {"Incident": "INC", "Request": "REQ", "Activity": "ACT"}.get(report_type, "INC")
    cursor.execute("""
        SELECT incident FROM reports
        WHERE incident LIKE %s
        ORDER BY id DESC
        LIMIT 1
    """, (f"{prefix}%",))
    last = cursor.fetchone()
    next_number = 1
    if last and last["incident"]:
        try:
            next_number = int(last["incident"][len(prefix):]) + 1
        except ValueError:
            next_number = 1
    return f"{prefix}{str(next_number).zfill(5)}"

@router.post("/report", dependencies=[Depends(verify_api_key)])
def receive_grafana_webhook(payload: GrafanaWebhookPayload):

    if payload.status != "firing":
        return {
            "success" : True,
            "message" : f"Status '{payload.status}' diabaikan, hanya 'firing' yang diproses",
            "inserted": 0
        }

    if not payload.alerts:
        raise HTTPException(status_code=422, detail="Tidak ada alerts di payload")

    inserted = []
    skipped  = []
    errors   = []

    conn = None
    try:
        conn = get_connection()

        for alert in payload.alerts:

            apps = alert.labels.apps if alert.labels.apps else None
            if not apps:
                errors.append({
                    "alertname": alert.labels.alertname,
                    "reason"   : "Label 'apps' tidak ditemukan di alert ini"
                })
                continue

            if apps not in ALLOWED_APPS:
                errors.append({
                    "alertname": alert.labels.alertname,
                    "reason"   : f"Apps '{apps}' tidak valid. Allowed: {', '.join(ALLOWED_APPS)}"
                })
                continue

            description = (
                alert.annotations.description
                or alert.annotations.summary
                or "No description"
            )

            request_date, report_time = parse_grafana_datetime(alert.startsAt or "")

            with conn.cursor() as cursor:

                incident_code = generate_incident_code(cursor, HARDCODED["type"])
                now           = datetime.now()
                report_uuid   = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO reports (
                        uuid, incident, requestor, requestor_email,
                        request_date, report_time, apps, type,
                        description, severity, assigned_to, scope,
                        status, response_time, handled_by,
                        restored_time, servicerestored_time,
                        total_internal_duration,
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s,
                        %s, %s
                    )
                """, (
                    report_uuid, incident_code,
                    HARDCODED["requestor"], HARDCODED["requestor_email"],
                    request_date, report_time, apps, HARDCODED["type"],
                    description, HARDCODED["severity"],
                    HARDCODED["assigned_to"], HARDCODED["scope"],
                    HARDCODED["status"], now, 0,
                    None, None,
                    None,
                    now, now
                ))

            conn.commit()

            inserted.append({
                "uuid"       : report_uuid,
                "incident"   : incident_code,
                "apps"       : apps,
                "description": description,
                "date"       : request_date,
                "time"       : report_time,
            })

    except HTTPException:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan report: {str(e)}")

    finally:
        if conn:
            conn.close()

    return {
        "success" : True,
        "message" : f"{len(inserted)} report berhasil dibuat, {len(skipped)} dilewati, {len(errors)} error",
        "inserted": inserted,
        "skipped" : skipped,
        "errors"  : errors,
    }