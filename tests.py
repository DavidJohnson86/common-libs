import pytest
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (
            {
                "external_project_id": "your_external_project_id",
                "fileset": "your_fileset",
                "annotation_workflow": {"annotation_provider": "your_annotation_provider"},
                "annotation_ruleset": "your_annotation_ruleset",
                "annotation_workflow_config": "your_workflow_config",
            },
            status.HTTP_200_OK,
        ),
        (
            {
                "fileset": "your_fileset",
                "annotation_workflow": {"annotation_provider": "your_annotation_provider"},
                "annotation_ruleset": "your_annotation_ruleset",
                "annotation_workflow_config": "your_workflow_config",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "external_project_id": "your_external_project_id",
                "annotation_workflow": {"annotation_provider": "your_annotation_provider"},
                "annotation_ruleset": "your_annotation_ruleset",
                "annotation_workflow_config": "your_workflow_config",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "annotation_workflow": {"annotation_provider": "your_annotation_provider"},
                "annotation_ruleset": "your_annotation_ruleset",
                "annotation_workflow_config": "your_workflow_config",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    ],
)
def test_create_annotation_request_fileset(payload, expected_status):
    response = client.post("/annotation_request/fileset", json=payload)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {
            "message": "Annotation request created successfully",
            "annotation_request": payload,
        }
    else:
        with pytest.raises(AssertionError):
            response = client.post("/annotation_request/fileset", json=payload)
            assert response.status_code == expected_status
