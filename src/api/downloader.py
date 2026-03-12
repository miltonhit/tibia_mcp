import logging

from src.config import BATCH_SIZE

logger = logging.getLogger(__name__)


def download_page_contents(client, page_titles, batch_size=None):
    """Download content for multiple pages in batches.

    Args:
        client: WikiClient instance
        page_titles: List of page title strings
        batch_size: Number of titles per API request (max 50)

    Yields:
        dict: {page_id, title, content, is_redirect, namespace} for each page
    """
    batch_size = batch_size or BATCH_SIZE

    for i in range(0, len(page_titles), batch_size):
        batch = page_titles[i:i + batch_size]
        titles_str = "|".join(batch)

        data = client.query(
            titles=titles_str,
            prop="revisions",
            rvprop="content",
            rvslots="main",
        )

        pages = data.get("query", {}).get("pages", {})
        for page_id_str, page_data in pages.items():
            page_id = int(page_id_str)
            if page_id < 0:
                # Missing page
                continue

            title = page_data.get("title", "")
            ns = page_data.get("ns", 0)

            # Extract content from revisions
            revisions = page_data.get("revisions", [])
            if revisions:
                # Try slots format first (newer MW), fall back to direct
                rev = revisions[0]
                if "slots" in rev and "main" in rev["slots"]:
                    content = rev["slots"]["main"].get("*", "")
                else:
                    content = rev.get("*", "")
            else:
                content = ""

            is_redirect = content.strip().upper().startswith("#REDIRECT")

            yield {
                "page_id": page_id,
                "title": title,
                "namespace": ns,
                "content": content,
                "is_redirect": is_redirect,
            }

        downloaded = min(i + batch_size, len(page_titles))
        if downloaded % 500 == 0 or downloaded == len(page_titles):
            logger.info("Downloaded %d/%d pages", downloaded, len(page_titles))
