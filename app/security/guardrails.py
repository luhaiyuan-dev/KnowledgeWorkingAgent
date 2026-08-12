import re
from pathlib import Path

from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    allowed: bool
    sanitized_text: str
    warnings: list[str] = Field(default_factory=list)


class SecurityGuardrails:
    INJECTION_PATTERNS = [
        r"忽略(以上|之前|系统).{0,10}(指令|提示词)",
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"system\s*prompt",
        r"绕过.{0,8}(权限|安全|审计)",
    ]

    def __init__(self, max_input_chars: int, block_prompt_injection: bool = False) -> None:
        self.max_input_chars = max_input_chars
        self.block_prompt_injection = block_prompt_injection

    def inspect_input(self, text: str) -> GuardrailResult:
        cleaned_text = text.strip()
        warnings: list[str] = []
        if not cleaned_text:
            return GuardrailResult(allowed=False, sanitized_text="", warnings=["输入不能为空"])
        if len(cleaned_text) > self.max_input_chars:
            return GuardrailResult(
                allowed=False,
                sanitized_text=cleaned_text[: self.max_input_chars],
                warnings=[f"输入超过 {self.max_input_chars} 字符限制"],
            )

        found_injection = any(
            re.search(pattern, cleaned_text, flags=re.IGNORECASE)
            for pattern in self.INJECTION_PATTERNS
        )
        if found_injection:
            warnings.append("检测到可能的提示词注入表达，已写入安全审计")
            if self.block_prompt_injection:
                return GuardrailResult(
                    allowed=False, sanitized_text=cleaned_text, warnings=warnings
                )

        return GuardrailResult(allowed=True, sanitized_text=cleaned_text, warnings=warnings)

    def mask_pii(self, text: str) -> str:
        masked_text = re.sub(r"1[3-9]\d{9}", "1**********", text)
        masked_text = re.sub(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            "***@***.***",
            masked_text,
        )
        masked_text = re.sub(r"\b\d{17}[0-9Xx]\b", "******************", masked_text)
        return masked_text

    def resolve_allowed_path(self, root: str | Path, requested_path: str | Path) -> Path:
        allowed_root = Path(root).resolve()
        candidate = Path(requested_path)
        if not candidate.is_absolute():
            candidate = allowed_root / candidate
        resolved_candidate = candidate.resolve()
        if resolved_candidate != allowed_root and allowed_root not in resolved_candidate.parents:
            raise PermissionError("请求路径超出允许目录")
        return resolved_candidate
