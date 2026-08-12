from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHINESE_SEPARATORS = [
    "\n\n",
    "\n",
    "。",
    "！",
    "？",
    "；",
    "，",
    ".",
    "!",
    "?",
    ";",
    ",",
    " ",
    "",
]


class EnterpriseTextSplitter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=CHINESE_SEPARATORS,
            length_function=len,
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        chunks = self._splitter.split_documents(documents)
        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = chunk_index
        return chunks
