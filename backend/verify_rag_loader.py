import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ai_service.rag.indexing.markdown_loader import MarkdownLoader

loader = MarkdownLoader(use_supabase=False)
docs = loader.load_documents()
print('count=', len(docs))
for d in docs:
    print(d['document_name'], '|', d['framework'], '|', d['path'])
