import pytest
from fastapi import status
from fastapi.testclient import TestClient
from annotation_service.app import app

client = TestClient(app)

# TC1: Every manadatory fields present
# TC2: Missing external_project_id
# TC3: Missing fileset
# TC4: Missing external_project_id & fileset


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (
            {
                "external_project_id": "clk6puu0900lo0724azre3hma",
                "annotation_workflow": {
                    "annotation_provider": "Labelbox",
                    "annotation_types": ["string"],
                    "media_type": "image",
                },
                "annotation_ruleset": "string",
                "annotation_workflow_config": "string",
                "fileset": "zeiss_file_set://fileset0003",
            },
            status.HTTP_201_CREATED,
        ),
        (
            {
                "annotation_workflow": {
                    "annotation_provider": "Labelbox",
                    "annotation_types": ["string"],
                    "media_type": "image",
                },
                "annotation_ruleset": "string",
                "annotation_workflow_config": "string",
                "fileset": "zeiss_file_set://fileset0003",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "external_project_id": "project_id",
                "annotation_workflow": {
                    "annotation_provider": "Labelbox",
                    "annotation_types": ["string"],
                    "media_type": "image",
                },
                "annotation_ruleset": "string",
                "annotation_workflow_config": "string",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "annotation_workflow": {
                    "annotation_provider": "Labelbox",
                    "annotation_types": ["string"],
                    "media_type": "image",
                },
                "annotation_ruleset": "string",
                "annotation_workflow_config": "string",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    ],
)
def test_create_annotation_request_fileset(payload, expected_status):
    response = client.post("/annotation_request/fileset", json=payload)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.json() == {
            "message": "Annotation request created successfully",
            "annotation_request": payload,
        }
    else:
        with pytest.raises(AssertionError):
            response = client.post("/annotation_request/fileset", json=payload)
            assert response.status_code == expected_status
