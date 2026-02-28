import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="TTSClient server")
    parser.add_argument("--https", action="store_true", help="HTTPS モードで起動 (自己署名証明書を生成)")
    parser.add_argument("--port", type=int, default=18000, help="リッスンポート (default: 18000)")
    args = parser.parse_args()

    kwargs: dict = {
        "host": "0.0.0.0",
        "port": args.port,
    }

    if args.https:
        from ttsclient.ssl_cert import generate_self_signed_cert

        cert_path, key_path = generate_self_signed_cert()
        kwargs["ssl_certfile"] = str(cert_path)
        kwargs["ssl_keyfile"] = str(key_path)
    else:
        kwargs["reload"] = True

    uvicorn.run("ttsclient.app:app", **kwargs)


if __name__ == "__main__":
    main()
