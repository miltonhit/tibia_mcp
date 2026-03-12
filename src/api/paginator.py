import logging

logger = logging.getLogger(__name__)


def iter_all_pages(client, namespace=0, limit=500):
    """Iterate over all pages in a namespace using allpages API.

    Yields:
        dict: {page_id, title} for each page
    """
    params = {
        "list": "allpages",
        "apnamespace": namespace,
        "aplimit": limit,
    }

    total = 0
    while True:
        data = client.query(**params)

        pages = data.get("query", {}).get("allpages", [])
        for page in pages:
            yield {"page_id": page["pageid"], "title": page["title"]}
            total += 1

        if total % 1000 == 0 and total > 0:
            logger.info("Enumerated %d pages so far...", total)

        # Check for continuation
        cont = data.get("continue")
        if cont and "apcontinue" in cont:
            params["apcontinue"] = cont["apcontinue"]
        else:
            break

    logger.info("Enumerated %d total pages in namespace %d", total, namespace)


def iter_template_pages(client, template_name, limit=500):
    """Iterate over all pages that embed a given template.

    Args:
        client: WikiClient instance
        template_name: Template name without 'Template:' prefix

    Yields:
        dict: {page_id, title} for each page
    """
    params = {
        "list": "embeddedin",
        "eititle": f"Template:{template_name}",
        "eilimit": limit,
        "einamespace": 0,
    }

    total = 0
    while True:
        data = client.query(**params)

        pages = data.get("query", {}).get("embeddedin", [])
        for page in pages:
            yield {"page_id": page["pageid"], "title": page["title"]}
            total += 1

        cont = data.get("continue")
        if cont and "eicontinue" in cont:
            params["eicontinue"] = cont["eicontinue"]
        else:
            break

    logger.info("Found %d pages using Template:%s", total, template_name)
