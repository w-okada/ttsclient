import fire

def main_process():
    print("Hello World!")

def main():
    fire.Fire(
        {
            "main_process": main_process,
        }
    )
