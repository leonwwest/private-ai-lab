import argparse
import os
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a PDF to Private AI Lab.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--url", default=os.getenv("PRIVATE_AI_LAB_URL", "http://localhost:8000"))
    parser.add_argument("--api-key", default=os.getenv("API_KEY", "change-me-before-sharing"))
    args = parser.parse_args()

    with args.pdf.open("rb") as file_handle:
        response = httpx.post(
            f"{args.url.rstrip('/')}/v1/documents/upload",
            headers={"Authorization": f"Bearer {args.api_key}"},
            files={"file": (args.pdf.name, file_handle, "application/pdf")},
            timeout=120,
        )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
