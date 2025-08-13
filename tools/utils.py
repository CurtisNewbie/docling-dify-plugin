from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    FormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline, PdfPipelineOptions
from docling.datamodel.pipeline_options import PipelineOptions, PaginatedPipelineOptions
from docling.chunking import HybridChunker
import pandas as pd

import logging
from dify_plugin.config.logger_format import plugin_logger_handler

from docling.backend.msword_backend import MsWordDocumentBackend

# Set up logging with the custom handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class DifyDocling():

    def documents_to_markdown(self, file_path_list: list[str],) -> str:
        """
        Convert a list of document file paths to markdown format.

        Args:
            file_path_list (list[str]): List of file paths to documents.

        Returns:
            str: Markdown representation of the documents.
        """

        logger.info("Prepare PdfPipelineOptions")

        pdf_pipeline = PdfPipelineOptions(do_ocr=False, do_table_structure = True)
        pdf_pipeline.ocr_options.download_enabled = False # do not download huggingface model
        pdf_pipeline.table_structure_options.do_cell_matching = False
        pdf_option = PdfFormatOption(pipeline_options=pdf_pipeline, backend=PyPdfiumDocumentBackend)

        logger.info(f"PdfFormatOption created, pdf_option not none: {pdf_option is not None}")

        doc_converter = DocumentConverter(
            format_options={
                InputFormat.IMAGE: pdf_option,
                InputFormat.PDF: pdf_option,
                InputFormat.DOCX: WordFormatOption(
                    pipeline_options=PaginatedPipelineOptions(generate_page_images=False, generate_picture_images=False),
                    pipeline_cls=SimplePipeline, backend=MsWordDocumentBackend
                ),
            }
        )

        logger.info(f"DocumentConvert created, format_options: {doc_converter.format_to_options}")

        converted_markdowns = doc_converter.convert_all(file_path_list)

        logger.info(f"DocumentConvert.convert_all called")

        markdown_results = []
        for result in converted_markdowns:
            if result.document is not None:
                markdown_results.append(result.document)
        return markdown_results

    def docling_document_to_chunks(self, docling_documents):
        chunker = HybridChunker()
        chunked_documents = {}
        for idx, docling_document in enumerate(docling_documents):
            chunk_iter = chunker.chunk(dl_doc=docling_document)
            chunks = []
            for i, chunk in enumerate(chunk_iter):
                enriched_text = chunker.contextualize(chunk=chunk)
                chunks.append(enriched_text)
            chunked_documents[idx] = chunks
        return chunked_documents

    def extract_tables(self, docling_documents):
        tables_markdown = []
        for docling_document in docling_documents:
            for table_ix, table in enumerate(docling_document.tables):
                table_df: pd.DataFrame = table.export_to_dataframe()
                tables_markdown.append(table_df.to_markdown())
        return tables_markdown
