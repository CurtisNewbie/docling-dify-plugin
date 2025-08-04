from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline, PdfPipelineOptions
from docling.chunking import HybridChunker
import pandas as pd

class DifyDocling():

    def documents_to_markdown(self,file_path_list: list[str],) -> str:
        """
        Convert a list of document file paths to markdown format.

        Args:
            file_path_list (list[str]): List of file paths to documents.

        Returns:
            str: Markdown representation of the documents.
        """

        do_ocr = False # enable/disable ocr
        ocr_use_gpu = False # cpu based ocr

        pdf_pipeline = PdfPipelineOptions()
        pdf_pipeline.do_ocr = do_ocr
        pdf_pipeline.do_table_structure = True

        if do_ocr:
            pdf_pipeline.ocr_options.use_gpu = ocr_use_gpu
            pdf_option = PdfFormatOption(pipeline_options=pdf_pipeline)
        else:
            pdf_pipeline.table_structure_options.do_cell_matching = False
            pdf_option = PdfFormatOption(pipeline_options=pdf_pipeline, backend=PyPdfiumDocumentBackend)

        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pdf_option
            }
        )
        converted_markdowns = doc_converter.convert_all(file_path_list)
        markdown_results = []
        for result in converted_markdowns:
            if result.document is not None:
                markdown_results.append(result.document)
        return markdown_results

    def docling_document_to_chunks(self,docling_documents):
        chunker = HybridChunker()
        chunked_documents= {}
        for idx,docling_document in enumerate(docling_documents):
            chunk_iter = chunker.chunk(dl_doc=docling_document)
            chunks = []
            for i, chunk in enumerate(chunk_iter):
                enriched_text = chunker.contextualize(chunk=chunk)
                chunks.append(enriched_text)
            chunked_documents[idx] = chunks
        return chunked_documents

    def extract_tables(self,docling_documents):
        tables_markdown = []
        for docling_document in docling_documents:
            for table_ix, table in enumerate(docling_document.tables):
                table_df: pd.DataFrame = table.export_to_dataframe()
                tables_markdown.append(table_df.to_markdown())
        return tables_markdown








