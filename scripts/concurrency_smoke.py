#!/usr/bin/env python3
"""Dispara duas matrículas idênticas simultaneamente contra a API em execução."""

import argparse
import json
import ssl
import threading
import urllib.error
import urllib.request


def post_enrollment(base_url: str, token: str, course_id: int, barrier, results):
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/enrollments/",
        data=json.dumps({"id_curso": course_id}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    context = ssl._create_unverified_context()
    barrier.wait()

    try:
        with urllib.request.urlopen(request, context=context, timeout=10) as response:
            results.append(response.status)
    except urllib.error.HTTPError as exc:
        results.append(exc.code)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://localhost")
    parser.add_argument("--token", required=True, help="JWT de um aluno sem matrícula ativa no curso")
    parser.add_argument("--course-id", required=True, type=int)
    args = parser.parse_args()

    barrier = threading.Barrier(2)
    results = []
    threads = [
        threading.Thread(
            target=post_enrollment,
            args=(args.base_url, args.token, args.course_id, barrier, results),
        )
        for _ in range(2)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("HTTP statuses:", sorted(results))
    if sorted(results) != [201, 409]:
        raise SystemExit("Esperado exatamente um 201 e um 409 para requests concorrentes.")

    print("OK: a matrícula concorrente não produziu duplicidade.")


if __name__ == "__main__":
    main()
