import os
import time
import logging
from duckduckgo_search import DDGS
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%f"
)
logger = logging.getLogger(__name__)

def search_web(topic: str, max_results: int = 6) -> str:
    """Searches DuckDuckGo and aggregates top text snippets."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=max_results))
        if not results:
            logger.warning("Search returned 0 results for topic: %r", topic)
            return "No recent web search results found."
        
        logger.info("search OK via text | query=%r | %d hits", topic, len(results))
        snippets = [
            f"Title: {item.get('title', '')}\nSnippet: {item.get('body', '')}"
            for item in results
        ]
        return "\n\n".join(snippets)
    except Exception as e:
        logger.warning("DuckDuckGo search error: %s. Using topic as direct context.", e)
        return f"Direct topic search fallback for: {topic}"

def summarize(topic: str, raw_context: str, temperature: float = 0.3) -> str:
    """Generates an exact 3-bullet summary using Gemini."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are a concise research analyst. Based on the web findings below, provide a high-level briefing on the topic: "{topic}".

Guidelines:
- Return EXACTLY three concise, impactful bullet points.
- Each bullet point must start with a dash ("- ").
- No introduction, no markdown headings, no concluding remarks.

Web Findings:
{raw_context}
"""
    model_name = "gemini-3.8-flash"
    logger.info("model used: %s", model_name)
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature
        )
    )
    return response.text.strip()

def run_workflow(topic: str, temperature: float = 0.3, progress=print) -> str:
    """Runs the full search and summarization pipeline."""
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Please enter a topic.")

    logger.info("request received | topic=%r | temperature=%s", topic, temperature)
    start = time.perf_counter()
    try:
        progress("Stage 1/2: searching the web...")
        raw = search_web(topic)
        
        progress("Stage 2/2: summarizing with Gemini...")
        brief = summarize(topic, raw, temperature)
    except Exception:
        logger.exception("request FAILED | topic=%r | after %.2fs", topic, time.perf_counter() - start)
        raise

    logger.info("request OK | topic=%r | time_taken=%.2fs", topic, time.perf_counter() - start)
    return brief