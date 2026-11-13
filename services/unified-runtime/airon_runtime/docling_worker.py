"""Local Markdown ingestion through real Docling. PDF/OCR are not qualified."""
import json
import sys
from pathlib import Path

def main():
    request = json.load(sys.stdin)
    path = Path(request["path"])
    if path.suffix.lower() != ".md" or path.is_symlink() or path.stat().st_size > 1024**2:
        raise ValueError("Only bounded local Markdown is currently qualified")
    routes = Path("/proc/self/net/route").read_text().splitlines()
    if len(routes) > 1:
        raise ValueError("Document worker has a network route")
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    converter = DocumentConverter(allowed_formats=[InputFormat.MD])
    result = converter.convert(path)
    if result.status.value != "success":
        raise ValueError("Docling conversion did not succeed")
    print(json.dumps({"text":result.document.export_to_markdown(),
                      "structure":result.document.export_to_dict(),"engine":"docling",
                      "format":"markdown","network_route_count":max(0,len(routes)-1)}))

if __name__ == "__main__":
    main()
