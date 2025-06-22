"""
Module for helper functions used by the Pam Beesly agent.
"""

import logging
import os
import re
import tempfile
import uuid
from typing import Any, Dict, List

from google.adk.tools.tool_context import ToolContext
from google.cloud import storage
from pam_beesly.config import settings  # pylint: disable=E0401
from vertexai import rag

logger = logging.getLogger(__name__)


def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Get the full resource name for the given corpus name.

    Args:
        corpus_name (str): The name of the corpus or diaplay name.

    Returns:
        str: The full resource name of the corpus.
    """

    if re.match(
        r"^projects/[^/]+/locations/[^/]+/corpora/[^/]+/ragCorpora/[^/]+$", corpus_name
    ):
        return corpus_name

    try:
        corpora_list = rag.list_corpora()

        for corpus in corpora_list:
            if hasattr(corpus, "display_name") and corpus.display_name == corpus_name:
                return corpus.name

    except Exception as e:
        logger.warning("Error retrieving corpus list: %s", e)
        pass

    if "/" in corpus_name:
        corpus_id = corpus_name.split("/")[-1]
    else:
        corpus_id = corpus_name

    corpus_id = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_id)

    return (
        f"projects/{settings.project_id}/locations/europe-west3/ragCorpora/{corpus_id}"
    )


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Check if a corpus exists.

    Args:
        corpus_name (str): The name of the corpus or display name.
        tool_context (ToolContext): The tool context to use for the check.

    Returns:
        bool: True if the corpus exists, False otherwise.
    """
    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        corpora = rag.list_corpora()
        for corpus in corpora:
            if (
                corpus.name == corpus_resource_name
                or corpus.display_name == corpus_name
            ):
                tool_context.state[f"corpus_exists_{corpus_name}"] = True
                return True
        return True
    except Exception as e:
        logger.warning("Corpus '%s' does not exist: %s", corpus_name, e)
        return False


def _save_content_to_temp_file(content: str, file_extension: str = ".txt") -> str:
    """
    Save string content to a temporary file.

    Args:
        content (str): The content to save to a file.
        file_extension (str): The file extension to use (default: '.txt').

    Returns:
        str: The path to the temporary file.
    """
    try:
        # Create a temporary file with the specified extension
        fd, temp_path = tempfile.mkstemp(suffix=file_extension)

        # Write content to the temporary file
        with os.fdopen(fd, "w") as tmp:
            tmp.write(content)

        return temp_path
    except Exception as e:
        logger.error("Error creating temporary file: %s", str(e))
        raise


def _upload_file_to_gcs(local_file_path: str, bucket_name: str) -> str:
    """
    Upload a local file to Google Cloud Storage.

    Args:
        local_file_path (str): Path to the local file to upload.
        bucket_name (str): Name of the GCS bucket to upload to.

    Returns:
        str: The GCS URI of the uploaded file.
    """
    try:
        # Validate bucket name - enforce dunder-mifflin-bucket
        if bucket_name != "dunder-mifflin-bucket":
            bucket_name = "dunder-mifflin-bucket"
            logger.warning(
                "Bucket name changed to the required 'dunder-mifflin-bucket'"
            )

        # Generate a unique blob name to avoid collisions
        filename = os.path.basename(local_file_path)
        unique_id = str(uuid.uuid4())[:8]
        # Ensure files are stored in the correct path
        destination_blob_name = f"dunder-mifflin-agents-artifact-store/pam-beesly-exports/{unique_id}_{filename}"

        # Upload the file to GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)

        # Clean up the local file
        os.remove(local_file_path)

        # Return the GCS URI
        gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
        return gcs_uri
    except Exception as e:
        logger.error("Error uploading file to GCS: %s", str(e))
        # Don't remove the local file if upload failed, for debugging purposes
        raise


# <-- Helper functions for data processing -->
def _process_file_contents(
    file_contents: List[Dict[str, str]],
    _: str = None,  # Ignored parameter, always using dunder-mifflin-bucket
) -> Dict[str, Any]:
    """
    Process and upload file contents to GCS.

    Args:
        file_contents (List[Dict[str, str]]): List of file content dictionaries.
        _: Ignored parameter, always using 'dunder-mifflin-bucket' bucket.

    Returns:
        Dict[str, Any]: Result with validated paths and metadata.
    """
    validated_paths = []
    invalid_paths = []
    uploaded_files = []

    # Always use dunder-mifflin-bucket
    gcs_bucket_name = "dunder-mifflin-bucket"

    if not file_contents:
        return {
            "status": "error",
            "message": "No file contents provided",
            "validated_paths": [],
            "invalid_paths": ["No file contents to process"],
            "uploaded_files": [],
        }

    # Process each file content entry
    for idx, file_data in enumerate(file_contents):
        try:
            # Extract content and metadata
            content = file_data.get("content")
            if not content:
                invalid_paths.append(f"Content entry #{idx + 1} (No content provided)")
                continue

            # Generate filename if not provided
            filename = file_data.get("filename", f"file_{idx + 1}")
            extension = file_data.get("extension", ".txt")

            # Save content to temp file
            temp_file_path = _save_content_to_temp_file(content, extension)

            # Upload to GCS
            gcs_uri = _upload_file_to_gcs(temp_file_path, gcs_bucket_name)

            # Add to validated paths
            validated_paths.append(gcs_uri)
            uploaded_files.append({"original_filename": filename, "gcs_uri": gcs_uri})

        except Exception as e:
            invalid_paths.append(f"Content entry #{idx + 1} ({str(e)})")
            logger.error("Error processing file content entry #%d: %s", idx + 1, str(e))

    return {
        "status": "success" if validated_paths else "error",
        "validated_paths": validated_paths,
        "invalid_paths": invalid_paths,
        "uploaded_files": uploaded_files,
    }


def _validate_single_path(path: str) -> Dict[str, Any]:
    """
    Validate a single path and convert if necessary.
    Only accepts GCS links with project-dunder-mifflin prefix.

    Args:
        path (str): A file path/URL to validate.

    Returns:
        Dict[str, Any]: Validation result with status and path information.
    """
    # Check for invalid input
    if not path or not isinstance(path, str):
        return {
            "status": "invalid",
            "reason": "Not a valid string",
            "valid_path": None,
            "conversion": None,
        }

    # Validate URL format - only GCS links allowed
    if not path.startswith("gs://"):
        return {
            "status": "invalid",
            "reason": "Invalid format: only Google Cloud Storage (gs://) paths are allowed",
            "valid_path": None,
            "conversion": None,
        }

    # Check if the GCS path has the correct project name prefix
    if "dunder-mifflin-bucket" not in path:
        return {
            "status": "invalid",
            "reason": "Invalid GCS path: must use bucket 'dunder-mifflin-bucket'",
            "valid_path": None,
            "conversion": None,
        }

    # Valid GCS path
    return {"status": "valid", "valid_path": path, "conversion": None}


def _process_paths(paths: List[str]) -> Dict[str, Any]:
    """
    Process and validate file paths.

    Args:
        paths (List[str]): List of file paths/URLs.

    Returns:
        Dict[str, Any]: Result with validated paths and metadata.
    """
    validated_paths = []
    invalid_paths = []
    conversions = []

    # Process each path
    for path in paths:
        result = _validate_single_path(path)

        if result["status"] == "valid":
            validated_paths.append(result["valid_path"])
            if result["conversion"]:
                conversions.append(result["conversion"])
        else:
            invalid_paths.append(f"{path} ({result['reason']})")

    return {
        "status": "success" if validated_paths else "error",
        "validated_paths": validated_paths,
        "invalid_paths": invalid_paths,
        "conversions": conversions,
    }


def _import_files_to_corpus(
    corpus_name: str,
    validated_paths: List[str],
    # tool_context is not used but kept for API compatibility
) -> Dict[str, Any]:
    """
    Import validated paths into the corpus.

    Args:
        corpus_name (str): The corpus name.
        validated_paths (List[str]): List of validated file paths.
        tool_context (ToolContext): The tool context.

    Returns:
        Dict[str, Any]: Import result.
    """
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
        )

        # Import data into the corpus
        import_result = rag.import_files(
            corpus_name=corpus_resource_name,
            paths=validated_paths,
            transformation_config=transformation_config,
        )

        return {
            "status": "success",
            "corpus_resource_name": corpus_resource_name,
            "file_added": import_result.imported_rag_files_count,
        }
    except Exception as e:
        logger.error("Error importing files to corpus: %s", str(e))
        return {
            "status": "error",
            "message": str(e),
            "corpus_resource_name": get_corpus_resource_name(corpus_name),
        }


def _get_attribute_value(obj, attr_name, default=""):
    """Get attribute value with default if not present."""
    return getattr(obj, attr_name, default) if hasattr(obj, attr_name) else default


def _process_rag_response(response) -> List[Dict[str, Any]]:
    """
    Process RAG query response into a more usable format.

    Args:
        response: The response from rag.retrieval_query

    Returns:
        List[Dict[str, Any]]: Processed results
    """
    results = []
    # Early return if no contexts
    if not hasattr(response, "contexts") or not response.contexts:
        return results

    # Process each context group
    for ctx_group in response.contexts.contexts:
        result = {
            "source_uri": _get_attribute_value(ctx_group, "source_uri"),
            "source_name": _get_attribute_value(ctx_group, "source_display_name"),
            "text": _get_attribute_value(ctx_group, "text"),
            "score": _get_attribute_value(ctx_group, "score", 0.0),
        }
        results.append(result)

    return results


def _perform_rag_query(corpus_resource_name: str, query: str) -> Dict[str, Any]:
    """
    Perform a RAG query against the specified corpus.

    Args:
        corpus_resource_name (str): The RAG corpus resource name.
        query (str): The query text.

    Returns:
        Dict[str, Any]: Query execution result and processed response.
    """
    try:
        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=settings.top_k,
            filter=rag.Filter(vector_distance_threshold=settings.distance_threshold),
        )

        # Perform the query
        print("Performing retrieval query...")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response
        results = _process_rag_response(response)

        return {"status": "success", "results": results}

    except Exception as e:
        logger.error("Error executing RAG query: %s", str(e))
        return {"status": "error", "message": str(e), "results": []}
