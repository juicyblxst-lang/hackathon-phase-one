#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "HackathonPhaseOneResearch/1.0"


class LinkParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return

        for key, value in attrs:
            if key.lower() == "href" and value:
                absolute = urljoin(self.base_url, value)
                self.links.append(absolute)


def normalize_url(url):
    url = url.strip()

    if url.startswith("[") and "](" in url:
        url = url.split("](", 1)[1].rstrip(")")

    parsed = urlparse(url)

    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    clean_path = parsed.path or "/"

    return parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=clean_path,
        fragment=""
    ).geturl()


def clean_text(html):
    parser = HTMLParser()
    parts = []

    class TextParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []

        def handle_data(self, data):
            value = data.strip()
            if value:
                self.parts.append(value)

    text_parser = TextParser()
    text_parser.feed(html)

    return "\n".join(text_parser.parts)


def fetch(url):
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    with urlopen(request, timeout=30) as response:
        raw = response.read()
        final_url = response.geturl()
        content_type = response.headers.get(
            "Content-Type",
            ""
        )

    html = raw.decode("utf-8", errors="replace")

    parser = LinkParser(final_url)
    parser.feed(html)

    links = sorted({
        normalize_url(link)
        for link in parser.links
        if link.startswith(("http://", "https://"))
    })

    return {
        "source_url": url,
        "final_url": normalize_url(final_url),
        "retrieved_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "content_type": content_type,
        "title": extract_title(html),
        "text": clean_text(html),
        "links": links
    }


def extract_title(html):
    lower = html.lower()
    start = lower.find("<title>")

    if start == -1:
        return None

    start += len("<title>")
    end = lower.find("</title>", start)

    if end == -1:
        return None

    return " ".join(
        html[start:end].split()
    )


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 research/hackathon/fetch.py <url> [run_dir]"
        )
        sys.exit(1)

    url = normalize_url(sys.argv[1])

    run_dir = (
        sys.argv[2]
        if len(sys.argv) >= 3
        else None
    )

    if run_dir:
        output_file = os.path.join(
            run_dir,
            "raw",
            "latest.json"
        )
    else:
        output_file = (
            "research/hackathon/raw/latest.json"
        )

    print("")
    print("Fetching:")
    print(url)
    print("")

    try:
        result = fetch(url)
    except Exception as error:
        print("RESEARCH FETCH FAILED")
        print(f"Error: {error}")
        sys.exit(1)

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("RESEARCH FETCH SUCCESS")
    print(f"Title: {result['title']}")
    print(f"Final URL: {result['final_url']}")
    print(f"Links found: {len(result['links'])}")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
