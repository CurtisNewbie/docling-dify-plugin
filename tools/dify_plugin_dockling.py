from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from docling.document_converter import DocumentConverter


class DifyPluginDocklingTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL
        converter = DocumentConverter()
        result = converter.convert(source)
        print(result.document.export_to_markdown()) 
        yield self.create_json_message({
            "result": "Hello, world!"
        })
