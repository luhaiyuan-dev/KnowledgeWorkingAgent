from pathlib import Path

import yaml

from app.core.config import PROJECT_ROOT


class PromptManager:
    def __init__(self, prompt_path: str | Path | None = None) -> None:
        selected_path = Path(prompt_path) if prompt_path else PROJECT_ROOT / "configs/prompts.yaml"
        with selected_path.open("r", encoding="utf-8") as prompt_file:
            self._prompts = yaml.safe_load(prompt_file)

    def get(self, name: str) -> str:
        if name not in self._prompts:
            raise KeyError(f"未找到 Prompt：{name}")
        return str(self._prompts[name])

    def format(self, name: str, **values: object) -> str:
        return self.get(name).format(**values)
