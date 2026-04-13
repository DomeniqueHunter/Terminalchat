from datetime import datetime

def logging(log_file:str, message:str, timestamp_enabled:bool=True) -> None:
    timestamp = f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ' if timestamp_enabled else ""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}{message}")


def test():
    log_file = "test.log"
    logging(log_file, "Test1")


if __name__ == "__main__":
    test()