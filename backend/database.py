import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_URL = os.environ.get("SUPABASE_URL", "")
_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def _try_supabase():
    """Attempt to connect to Supabase. Returns the client on success, None on failure."""
    if not _URL or not _KEY:
        logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set; using fallback.")
        return None
    try:
        from supabase import Client, create_client

        client: Client = create_client(_URL, _KEY)
        # Quick connectivity probe — raises if credentials or network are bad.
        client.table("projects").select("id").execute()
        return client
    except Exception as exc:
        logger.warning("Supabase unavailable (%s); using fallback.", exc)
        return None


supabase = _try_supabase()

if supabase is None:
    from fallback_db import FallbackClient

    supabase = FallbackClient()
    logger.info("Fallback in-memory database loaded from clean_dump.sql.")
