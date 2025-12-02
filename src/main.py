import os
import sys
import asyncio

# Add src to path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.domain.services.monitor_service import MonitorService
from src.adapters.infrastructure.newspim_scraper import NewspimScraper
from src.adapters.infrastructure.csv_storage import CsvStorage
from src.adapters.infrastructure.win_toast import WinToast

async def main():
    # 1. Create Adapters (Infrastructure)
    news_repo = NewspimScraper()
    
    # Logs directory at project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, "logs")
    storage_repo = CsvStorage(base_dir=logs_dir)
    
    alert_system = WinToast()

    # 2. Inject Dependencies into Service (Domain)
    service = MonitorService(
        news_repo=news_repo,
        storage_repo=storage_repo,
        alert_system=alert_system
    )

    # 3. Run Application
    try:
        await service.run()
    except KeyboardInterrupt:
        print("\nStopping Monitor Service...")

if __name__ == "__main__":
    asyncio.run(main())