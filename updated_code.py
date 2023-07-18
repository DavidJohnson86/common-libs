import uuid
from typing import Dict, Union

from fastapi import FastAPI, HTTPException

from annotation_service.app_config import configuration
from annotation_service.controller.dto import AnnotationRequestFileSetDTO
from annotation_service.domain.entity import AnnotationContext, AnnotationStatus, AnnotationWorkflow, MediaType
from annotation_service.infrastructure.annotation_provider import LabelboxAnnotationTool
from annotation_service.infrastructure.data_blob_repository import AzureBlobStorageRepository
from annotation_service.infrastructure.db_repository import AnnotationServicePostgresRepository
from annotation_service.infrastructure.fileset_repository import ArtemisFilesetRepository
from annotation_service.service.annotation_service import (
    ANNOTATION_REQUEST_DATASET_TEMPLATE,
    AnnotationService,
    AnnotationServiceConfig,
)

app = FastAPI()


def init_service() -> None:
    data_blob_repositories = [
        AzureBlobStorageRepository(
            path_templates={"Artemis_template": ANNOTATION_REQUEST_DATASET_TEMPLATE},
            config=configuration.azure,
        ),
    ]

    artemis_fileset_repository = ArtemisFilesetRepository(config=configuration)
    annotation_provider_repository = LabelboxAnnotationTool(data_blob_repositories=data_blob_repositories)
    annotation_service_db_repository = AnnotationServicePostgresRepository()
    annotation_request_dataset_template_params = {"test": "test"}
    annotation_request_dataset_template_id = "Artemis_template"

    annotation_service_config = AnnotationServiceConfig(
        artemis_file_set_repository=artemis_fileset_repository,
        annotation_provider_repository=annotation_provider_repository,
        annotation_service_db_repository=annotation_service_db_repository,
        annotation_request_dataset_template_id=annotation_request_dataset_template_id,
        annotation_request_dataset_template_params=annotation_request_dataset_template_params,
    )
    AnnotationService(annotation_service_config)


init_service()


@app.post("/annotation_request/fileset", status_code=201)
def create_annotation_request_fileset(
    request: AnnotationRequestFileSetDTO,
) -> Dict[str, Union[str, AnnotationRequestFileSetDTO]]:
    # FIXME outsource context creation to another module
    if not request.external_project_id or not request.fileset:
        raise HTTPException(status_code=422, detail="Missing mandatory attributes")

    annotation_context = AnnotationContext(
        id=str(uuid.uuid4()),
        external_project_id=request.external_project_id,
        file_set=request.fileset,
        data_product=None,
        external_request_parameters={},
        status=AnnotationStatus.REQUEST_RECEIVED,
        annotation_workflow=AnnotationWorkflow(
            id=str(uuid.uuid4()),
            annotation_provider=request.annotation_workflow.annotation_provider,
            annotation_types=[],
            media_type=MediaType.IMAGE,
        ),
        annotation_ruleset=request.annotation_ruleset,
        annotation_workflow_config=request.annotation_workflow_config,
    )

    # Send the annotation request
    annotation_service: AnnotationService = AnnotationService()
    annotation_service.send_annotation_request(annotation_context=annotation_context)

    return {"message": "Annotation request created successfully", "annotation_request": request}


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Annotation Tool API"}
