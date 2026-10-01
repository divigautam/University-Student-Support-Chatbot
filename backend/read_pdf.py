from pathlib import Path
from pypdf import PdfReader

# Project root = one folder above backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing all PDFs
PDF_FOLDER = BASE_DIR / "data" / "documents"

pdf_files = list(PDF_FOLDER.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found!")
    print("Looking in:", PDF_FOLDER)
    exit()

print(f"Found {len(pdf_files)} PDF(s)")
print("=" * 60)

for pdf_path in pdf_files:

    print(f"\n📄 Reading: {pdf_path.name}")
    print("-" * 60)

    reader = PdfReader(str(pdf_path))

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    print(f"Pages: {len(reader.pages)}")
    print(f"Characters extracted: {len(text)}")

    print("\nFirst 1000 characters:")
    print(text[:1000])

    print("\n" + "=" * 60)

print("\n✅ All PDFs processed successfully!")