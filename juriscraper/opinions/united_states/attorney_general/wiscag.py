"""
Scraper for Wisconsin Attorney General
CourtID: wiscag
Court Short Name: Wisconsin AG
Author: William E. Palin
History:
 - 2023-01-29: Created.
"""

import re
from datetime import datetime as dt

from juriscraper.OpinionSiteLinear import OpinionSiteLinear


class Site(OpinionSiteLinear):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.court_id = self.__module__
        self.status = "Published"
        self.url = "https://docs.legis.wisconsin.gov/misc/oag/recent"
        self.seeds = []

    def _process_html(self):
        """Process HTML

        :return: None
        """
        for row in self.html.xpath(
            ".//span/span/a[contains(@href, '.pdf')]/../.."
        ):
            html_link, url = row.xpath(".//a/@href")
            self.seeds.append(html_link)
            docket = html_link.split("/")[-1].upper()
            name = docket
            self.cases.append(
                {
                    "url": url,
                    "docket": docket,
                    "name": name,
                    "date": f"20{docket[-2:]}",
                    "date_filed_is_approximate": True,
                }
            )

    async def _get_case_dates(self) -> list:
        """Fetch the case date from each opinion page.

        :return: Case dates
        """

        async def fetcher(link: str):
            """Abstract out the case date from the case page."""
            if self.test_mode_enabled():
                return dt.strptime("December 25, 2020", "%B %d, %Y")
            html = await self._get_html_tree_by_url(link)
            pattern = re.compile(r"([A-Z][a-z]+ \d{1,2}, \d{4})")
            op_text = re.sub(r"\s+", " ", html.text_content())
            match = pattern.search(op_text)
            return dt.strptime(match.group(), "%B %d, %Y")

        return [await fetcher(seed) for seed in self.seeds]
