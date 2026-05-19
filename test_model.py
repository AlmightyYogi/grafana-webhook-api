from app.models import ReportPayload

# Test 1 - payload valid
try:
    payload = ReportPayload(
        requestor="John Doe",
        requestor_email="john@example.com",
        request_date="2026-05-11",
        report_time="09:30",
        apps="B2B Portal",
        type="Incident",
        description="Server down",
        severity="1 - Emergency (Full Down)",
        assigned_to="B2B Applications Operations",
        scope="Infrastructure",
        status=1
    )
    print("✓ Test 1 PASSED - Payload valid")
    print(f"  Data: {payload.model_dump()}")
except Exception as e:
    print(f"✗ Test 1 FAILED: {e}")

print()

# Test 2 - email invalid
try:
    payload = ReportPayload(
        requestor="John Doe",
        requestor_email="bukan-email",
        request_date="2026-05-11",
        report_time="09:30",
        apps="B2B Portal",
        type="Incident",
        description="Server down",
        severity="1 - Emergency (Full Down)",
        assigned_to="B2B Applications Operations",
        scope="Infrastructure"
    )
    print("✗ Test 2 FAILED - Seharusnya error")
except Exception as e:
    print(f"✓ Test 2 PASSED - Email invalid tertangkap: {e}")

print()

# Test 3 - type tidak valid
try:
    payload = ReportPayload(
        requestor="John Doe",
        requestor_email="john@example.com",
        request_date="2026-05-11",
        report_time="09:30",
        apps="B2B Portal",
        type="InvalidType",
        description="Server down",
        severity="1 - Emergency (Full Down)",
        assigned_to="B2B Applications Operations",
        scope="Infrastructure"
    )
    print("✗ Test 3 FAILED - Seharusnya error")
except Exception as e:
    print(f"✓ Test 3 PASSED - Type invalid tertangkap: {e}")