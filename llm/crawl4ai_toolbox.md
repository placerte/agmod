# Crawl4AI Toolbox (Authoritative)

This document defines the default **Crawl4AI** usage patterns for web crawling
and structured extraction. Use this when the task involves scraping websites,
extracting data, or converting content to Markdown.

Primary reference: https://github.com/unclecode/crawl4ai

---

## Scope

Applies to:
- single-page crawling
- batch / multi-URL crawling
- structured extraction (CSS/JSON or LLM)
- documentation-to-markdown pipelines

---

## Installation Check

```bash
crawl4ai-doctor
crawl4ai-setup
```

---

## Core Concepts

Key classes:
- `AsyncWebCrawler`
- `BrowserConfig` (browser-level options)
- `CrawlerRunConfig` (per-crawl behavior)

Minimal crawl:

```python
import asyncio
from crawl4ai import AsyncWebCrawler


async def main() -> None:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:500])


asyncio.run(main())
```

---

## Markdown Extraction (Primary Use Case)

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        "https://docs.example.com",
        config=CrawlerRunConfig(
            excluded_tags=["nav", "footer", "aside"],
            remove_overlay_elements=True,
        ),
    )
    with open("docs.md", "w", encoding="utf-8") as handle:
        handle.write(result.markdown)
```

Fit Markdown (content filtering):

```python
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

filterer = BM25ContentFilter(user_query="api reference", bm25_threshold=1.0)
generator = DefaultMarkdownGenerator(content_filter=filterer)
config = CrawlerRunConfig(markdown_generator=generator)
```

---

## Structured Extraction

### Schema-based (preferred, fast, no LLM)

```python
from crawl4ai import CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

schema = {
    "name": "articles",
    "baseSelector": "article.post",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "date", "selector": ".date", "type": "text"},
    ],
}

config = CrawlerRunConfig(
    extraction_strategy=JsonCssExtractionStrategy(schema=schema)
)
```

### LLM-based (only when structure is irregular)

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

config = CrawlerRunConfig(
    extraction_strategy=LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        instruction="Extract key metrics and trends",
    )
)
```

---

## Dynamic Content and JS

```python
config = CrawlerRunConfig(
    wait_for="css:.dynamic-content",
    js_code="""
    window.scrollTo(0, document.body.scrollHeight);
    document.querySelector('.load-more')?.click();
    """,
    page_timeout=60000,
)
```

---

## Batch Crawling

```python
urls = ["https://a.com", "https://b.com"]
results = await crawler.arun_many(urls=urls, max_concurrent=5)
```

---

## Sessions and Auth

```python
login_config = CrawlerRunConfig(
    session_id="user_session",
    js_code="""
    document.querySelector('#username').value = 'user';
    document.querySelector('#password').value = 'pass';
    document.querySelector('#submit').click();
    """,
    wait_for="css:.dashboard",
)

await crawler.arun("https://site.com/login", config=login_config)
```

---

## Best Practices

- Start with simple `arun()` and minimal config.
- Use schema extraction for repetitive layouts (cheaper and faster).
- Use `fit_markdown` or content filters to reduce noise.
- Respect rate limits; add delays and cap concurrency.
- Increase `page_timeout` for JS-heavy pages.

---

## Troubleshooting

If content is missing:

```python
config = CrawlerRunConfig(
    wait_for="js:document.querySelector('.content') !== null",
    page_timeout=60000,
)
```

If blocked or detected:
- Rotate user agents
- Use proxies
- Add random delays

---

## Scripts (Optional)

If you have the skill package available, these scripts are useful:
- `scripts/basic_crawler.py` (markdown extraction)
- `scripts/batch_crawler.py` (multi-URL)
- `scripts/extraction_pipeline.py` (schema generation + extraction)

---

## References

- Full SDK reference (if installed with skill package):
  `references/complete-sdk-reference.md`
