import os, sys, logging

# تأكد من أن مجلد backend في مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("runner")

logger.info("===== Starting MyTwin via run.py =====")
logger.info(f"Python: {sys.version}")
logger.info(f"CWD: {os.getcwd()}")
logger.info(f"PATH: {sys.path}")

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting uvicorn on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
