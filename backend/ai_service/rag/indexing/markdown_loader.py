# Use: Loads Markdown documents from Supabase Storage or local fallback.

from typing import List, Dict, Any


class MarkdownLoader:
    def __init__(self, use_supabase: bool = True):
        self.use_supabase = use_supabase

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Loads document raw text from local folder or Supabase storage.
        """
        return []
