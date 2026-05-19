from app.database import test_connection

success, message = test_connection()
print(f"Status: {'OK' if success else 'FAILED'}")
print(f"Message: {message}")