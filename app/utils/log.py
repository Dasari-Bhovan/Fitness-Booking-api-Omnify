import logging
import os

# Optional: Make a logs directory
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename="logs/app.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("fitness-booking-app")
