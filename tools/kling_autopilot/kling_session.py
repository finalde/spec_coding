from __future__ import annotations

from pathlib import Path
from types import TracebackType

from playwright.sync_api import BrowserContext, Page, sync_playwright

from config import KlingConfig
from segments import PromptSegment


class KlingSession:
    def __init__(self, config: KlingConfig) -> None:
        self._config = config
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def __enter__(self) -> "KlingSession":
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self._config.user_data_dir, headless=False
        )
        pages = self._context.pages
        self._page = pages[0] if pages else self._context.new_page()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._context is not None:
            self._context.close()
        if self._playwright is not None:
            self._playwright.stop()

    @property
    def _active_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("session not started")
        return self._page

    def open_create(self) -> None:
        self._active_page.goto(self._config.create_url)

    def fill_prompt(self, segments: list[PromptSegment]) -> None:
        page = self._active_page
        timing = self._config.timing
        box = page.locator(self._config.selectors.prompt_input)
        box.click()
        box.fill("")
        for segment in segments:
            if segment.kind == "text":
                box.type(segment.value, delay=timing.type_delay_ms)
            else:
                self._insert_element(segment.value)
            page.wait_for_timeout(timing.between_actions_ms)

    def _insert_element(self, name: str) -> None:
        page = self._active_page
        timing = self._config.timing
        selectors = self._config.selectors
        spec = self._config.elements[name]
        box = page.locator(selectors.prompt_input)
        box.type("@", delay=timing.type_delay_ms)
        page.locator(selectors.mention_dropdown).wait_for(timeout=timing.dropdown_timeout_ms)
        if spec.search:
            box.type(spec.search, delay=timing.type_delay_ms)
        page.locator(selectors.mention_option).filter(has_text=spec.label).first.click()

    def set_params(self) -> None:
        page = self._active_page
        selectors = self._config.selectors
        if selectors.aspect_control:
            page.locator(selectors.aspect_control).click()
            page.get_by_text(self._config.aspect_ratio, exact=True).first.click()
        if selectors.duration_control:
            page.locator(selectors.duration_control).click()
            page.get_by_text(self._config.duration, exact=True).first.click()

    def generate_and_wait(self) -> None:
        page = self._active_page
        selectors = self._config.selectors
        page.locator(selectors.generate_button).click()
        page.locator(selectors.result_ready).wait_for(timeout=self._config.timing.result_timeout_ms)

    def download_to(self, dest: Path) -> None:
        page = self._active_page
        dest.parent.mkdir(parents=True, exist_ok=True)
        with page.expect_download() as download:
            page.locator(self._config.selectors.download_button).click()
        download.value.save_as(str(dest))
