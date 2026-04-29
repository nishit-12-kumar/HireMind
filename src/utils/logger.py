import logging
import os
from datetime import datetime

# 1. Create a dynamic log file name based on the current date and time
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# 2. Dynamically locate the root 'logs' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 3. Ensure the logs directory exists (creates it if it doesn't)
os.makedirs(LOG_DIR, exist_ok=True)

# 4. Construct the full path to the log file
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

# 5. Configure the logging settings
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Export a logger object to be used across the app
logger = logging.getLogger("HR_MultiAgent")