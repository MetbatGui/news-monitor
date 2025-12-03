import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.infrastructure.newspim_scraper import NewspimScraper
from src.config import Config

class TestNewspimScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = NewspimScraper()
        
        # Load debug HTML
        debug_html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'newspim_debug.html')
        if os.path.exists(debug_html_path):
            with open(debug_html_path, 'r', encoding='utf-8') as f:
                self.html_content = f.read()
        else:
            self.html_content = ""
            print("Warning: newspim_debug.html not found.")

    @patch('requests.get')
    def test_fetch_reports(self, mock_get):
        if not self.html_content:
            self.skipTest("No debug HTML found")
            
        # Mock response
        mock_response = MagicMock()
        mock_response.text = self.html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Run scraper
        articles = self.scraper.fetch_reports(Config.KEYWORD)
        
        # Verify
        print(f"Found {len(articles)} articles.")
        for article in articles:
            print(f"- [{article.id}] {article.title} ({article.date})")
            
        self.assertTrue(len(articles) > 0)
        self.assertEqual(articles[0].id, 20251202000389)
        self.assertIn("이지케어텍", articles[0].title)

if __name__ == '__main__':
    unittest.main()
