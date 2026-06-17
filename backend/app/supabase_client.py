# Use: Initializes and configures the Supabase Storage client integration.

from supabase import Client, create_client

from app.config import get_settings

settings = get_settings()
supabase: Client = create_client(str(settings.supabase_url), settings.supabase_service_key)


async def check_supabase() -> dict[str, bool]:
    supabase.storage.get_bucket(settings.supabase_knowledge_bucket)
    return {"ok": True}
