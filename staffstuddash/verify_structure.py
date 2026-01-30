import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.main import app
    print("Successfully imported app from backend.main")
except ImportError as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

expected_routes = [
    "/students",
    "/assessments",
    "/dashboard/teacher",
    "/health",
    "/",
    "/drafts",
    "/performance-records"
]

existing_routes = [route.path for route in app.routes]

missing_routes = []
for route in expected_routes:
    if route not in existing_routes:
        missing_routes.append(route)

if missing_routes:
    print(f"verification header: FAILED")
    print(f"Missing routes: {missing_routes}")
    sys.exit(1)
else:
    print(f"verification header: PASSED")
    print("All expected routes are present.")
