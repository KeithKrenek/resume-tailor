"""Web scraping utilities for job postings."""

import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Optional
import re
from urllib.parse import urlparse

from config.settings import REQUEST_TIMEOUT, USER_AGENT


class JobScraper:
    """Scraper for job posting URLs."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def scrape_job_url(self, url: str) -> Tuple[bool, Dict[str, str], str]:
        """
        Scrape job posting from URL.

        Args:
            url: Job posting URL

        Returns:
            Tuple of (success, job_data_dict, error_message)
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Make request
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract job data
            job_data = self._extract_job_data(soup, url)

            if not job_data.get('description'):
                return False, {}, "Could not extract job description from URL"

            return True, job_data, ""

        except requests.exceptions.Timeout:
            return False, {}, f"Request timed out after {REQUEST_TIMEOUT} seconds"
        except requests.exceptions.ConnectionError:
            return False, {}, "Could not connect to URL. Please check your internet connection."
        except requests.exceptions.HTTPError as e:
            return False, {}, f"HTTP error: {e.response.status_code}"
        except Exception as e:
            return False, {}, f"Error scraping URL: {str(e)}"

    def _extract_job_data(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """
        Extract job data from parsed HTML.

        Args:
            soup: BeautifulSoup object
            url: Original URL

        Returns:
            Dictionary with job data
        """
        job_data = {
            'title': '',
            'company': '',
            'description': '',
            'location': '',
            'url': url,
            'raw_html': ''
        }

        # Detect job board and use appropriate selectors
        domain = urlparse(url).netloc.lower()

        if 'linkedin.com' in domain:
            job_data = self._extract_linkedin(soup)
        elif 'indeed.com' in domain:
            job_data = self._extract_indeed(soup)
        elif 'greenhouse.io' in domain:
            job_data = self._extract_greenhouse(soup)
        elif 'lever.co' in domain:
            job_data = self._extract_lever(soup)
        else:
            # Generic extraction
            job_data = self._extract_generic(soup)

        job_data['url'] = url
        job_data['raw_html'] = str(soup)[:5000]  # First 5000 chars for debugging

        return job_data

    def _extract_linkedin(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract job data from LinkedIn."""
        data = {'title': '', 'company': '', 'description': '', 'location': ''}

        # Title
        title_elem = soup.find('h1', class_=re.compile('top-card-layout__title|topcard__title'))
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)

        # Company
        company_elem = soup.find('a', class_=re.compile('topcard__org-name-link|top-card-layout__company'))
        if not company_elem:
            company_elem = soup.find('span', class_=re.compile('topcard__flavor'))
        if company_elem:
            data['company'] = company_elem.get_text(strip=True)

        # Location
        location_elem = soup.find('span', class_=re.compile('topcard__flavor|top-card-layout__location'))
        if location_elem:
            data['location'] = location_elem.get_text(strip=True)

        # Description
        desc_elem = soup.find('div', class_=re.compile('description__text|show-more-less-html__markup'))
        if desc_elem:
            data['description'] = desc_elem.get_text(separator='\n', strip=True)

        return data

    def _extract_indeed(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract job data from Indeed."""
        data = {'title': '', 'company': '', 'description': '', 'location': ''}

        # Title
        title_elem = soup.find('h1', class_=re.compile('jobsearch-JobInfoHeader-title'))
        if not title_elem:
            title_elem = soup.find('h1')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)

        # Company
        company_elem = soup.find('div', {'data-company-name': True})
        if not company_elem:
            company_elem = soup.find('a', {'data-tn-element': 'companyName'})
        if company_elem:
            data['company'] = company_elem.get_text(strip=True)

        # Description
        desc_elem = soup.find('div', id='jobDescriptionText')
        if not desc_elem:
            desc_elem = soup.find('div', class_=re.compile('jobsearch-jobDescriptionText'))
        if desc_elem:
            data['description'] = desc_elem.get_text(separator='\n', strip=True)

        return data

    def _extract_greenhouse(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract job data from Greenhouse."""
        data = {'title': '', 'company': '', 'description': '', 'location': ''}

        # Title
        title_elem = soup.find('h1', class_='app-title')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)

        # Company
        company_elem = soup.find('span', class_='company-name')
        if company_elem:
            data['company'] = company_elem.get_text(strip=True)

        # Location
        location_elem = soup.find('div', class_='location')
        if location_elem:
            data['location'] = location_elem.get_text(strip=True)

        # Description
        desc_elem = soup.find('div', id='content')
        if desc_elem:
            data['description'] = desc_elem.get_text(separator='\n', strip=True)

        return data

    def _extract_lever(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract job data from Lever."""
        data = {'title': '', 'company': '', 'description': '', 'location': ''}

        # Title
        title_elem = soup.find('h2', attrs={'data-qa': 'posting-name'})
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)

        # Company (usually in page title or header)
        company_elem = soup.find('div', class_='main-header-text')
        if company_elem:
            data['company'] = company_elem.get_text(strip=True)

        # Location
        location_elem = soup.find('div', class_='posting-categories')
        if location_elem:
            data['location'] = location_elem.get_text(strip=True)

        # Description
        desc_elem = soup.find('div', class_='content')
        if desc_elem:
            data['description'] = desc_elem.get_text(separator='\n', strip=True)

        return data

    def _extract_generic(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Generic extraction for unknown job boards."""
        data = {'title': '', 'company': '', 'description': '', 'location': ''}

        # Try to find title (usually h1 or h2)
        title_elem = soup.find('h1')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)

        # Try to extract main content
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        # Get text from main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|job|description'))

        if main_content:
            data['description'] = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback: get all text from body
            body = soup.find('body')
            if body:
                data['description'] = body.get_text(separator='\n', strip=True)

        # Clean up description (remove excessive whitespace)
        data['description'] = re.sub(r'\n\s*\n', '\n\n', data['description'])
        data['description'] = re.sub(r' +', ' ', data['description'])

        return data

    def extract_company_from_url(self, url: str) -> Optional[str]:
        """
        Extract company name from URL.

        Args:
            url: Company or job URL

        Returns:
            Company name if extractable, None otherwise
        """
        try:
            domain = urlparse(url).netloc
            # Remove common prefixes and TLD
            domain = domain.replace('www.', '')
            company = domain.split('.')[0]
            return company.capitalize()
        except:
            return None


# Convenience function for use in other modules
def scrape_job_posting(url: str) -> Tuple[bool, Dict[str, str], str]:
    """
    Scrape job posting from URL.

    Args:
        url: Job posting URL

    Returns:
        Tuple of (success, job_data_dict, error_message)
    """
    scraper = JobScraper()
    return scraper.scrape_job_url(url)
