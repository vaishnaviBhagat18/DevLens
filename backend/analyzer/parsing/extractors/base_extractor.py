class BaseExtractor:
    def __init__(self, source_code: bytes):
        self.source_code = source_code

    def get_node_text(self, node) -> str:
        return self.source_code[
            node.start_byte:node.end_byte
        ].decode("utf-8", errors="ignore")

    def extract(self, root_node) -> dict:
        raise NotImplementedError(
            "Extractor must implement extract()."
        )