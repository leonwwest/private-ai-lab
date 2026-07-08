import argparse
import os

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the local Private AI Lab API.")
    parser.add_argument("question")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--url", default=os.getenv("PRIVATE_AI_LAB_URL", "http://localhost:8000"))
    parser.add_argument("--api-key", default=os.getenv("API_KEY", "change-me-before-sharing"))
    args = parser.parse_args()

    response = httpx.post(
        f"{args.url.rstrip('/')}/v1/chat",
        headers={"Authorization": f"Bearer {args.api_key}"},
        json={"question": args.question, "top_k": args.top_k},
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()

    print(payload["answer"])
    print("\nSources:")
    for source in payload["sources"]:
        print(f"- {source['filename']} chunk={source['chunk_index']} score={source['score']}")


if __name__ == "__main__":
    main()
