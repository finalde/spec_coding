class Analyzer:
    def __init__(self, log_path: str, verbose: bool = False) -> None:
        self.log_path = log_path
        self.verbose = verbose

    def parse(self) -> list[dict[str, str]]:
        pass

    def summarize(self) -> str:
        pass
