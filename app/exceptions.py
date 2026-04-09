from fastapi import HTTPException, status
import uuid


def person_not_found(person_uuid: uuid.UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Person with UUID {person_uuid} not found"
    )


def relationship_not_found(source_uuid: uuid.UUID, target_uuid: uuid.UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No relationship found between {source_uuid} and {target_uuid}"
    )


def invalid_relationship_path(current_uuid: uuid.UUID, next_uuid: uuid.UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid relationship path: {next_uuid} is not directly related to {current_uuid}"
    )


def cannot_delete_person_with_children(person_uuid: uuid.UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Cannot delete person {person_uuid} because they have children"
    )


def invalid_uuid(uuid_str: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid UUID format: {uuid_str}"
    )
