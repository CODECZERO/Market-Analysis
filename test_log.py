
import sys
import os

# Add worker/src to path
sys.path.append(os.path.join(os.getcwd(), 'worker', 'src'))

try:
    from system_logger import get_logger, log_event
    print("✅ system_logger imported successfully")
except ImportError as e:
    print(f"❌ Failed to import system_logger: {e}")
    sys.exit(1)

print("Attempting to write to log...")
logger = get_logger("TEST_SCRIPT")
logger.info("This is a test log entry from test_log.py")
log_event("TEST", "DEBUG", "Test event logged")

log_path = "/home/codeczero/Desktop/FullStack/Brand-Mention-Reputation-Tracker/market_analysis/logs/system_comprehensive.log"
if os.path.exists(log_path):
    print(f"✅ Log file exists at: {log_path}")
    print(f"Size: {os.path.getsize(log_path)} bytes")
else:
    print(f"❌ Log file NOT found at: {log_path}")
