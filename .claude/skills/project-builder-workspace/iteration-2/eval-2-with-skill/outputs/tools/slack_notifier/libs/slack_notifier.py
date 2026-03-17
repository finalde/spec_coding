class SlackNotifier:
    def __init__(self, token: str, channel: str, pipeline_name: str | None = None) -> None:
        self.token: str = token
        self.channel: str = channel
        self.pipeline_name: str | None = pipeline_name

    def notify(self, status: str, message: str | None = None) -> None:
        pass

    def send_message(self, text: str) -> dict:
        pass
