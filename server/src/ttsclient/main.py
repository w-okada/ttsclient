import uvicorn


def main() -> None:
    uvicorn.run("ttsclient.app:app", host="0.0.0.0", port=18000, reload=True)


if __name__ == "__main__":
    main()
