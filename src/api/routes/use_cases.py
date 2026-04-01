from __future__ import annotations

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.db.connection import get_connection
from src.db.models import Urgency, UseCaseStatus
from src.tenancy.middleware import CurrentUser, get_current_user

router = APIRouter(prefix="/use-cases", tags=["use-cases"])


class UseCaseCreate(BaseModel):
    title: str
    description: str = ""
    problem_statement: str = ""
    stakeholders: list[str] = []
    available_data: str = ""
    expected_outcome: str = ""
    urgency: Urgency = Urgency.medium


class UseCaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    problem_statement: str | None = None
    stakeholders: list[str] | None = None
    available_data: str | None = None
    expected_outcome: str | None = None
    urgency: Urgency | None = None
    status: UseCaseStatus | None = None


@router.get("")
async def list_use_cases(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    status_filter: str | None = None,
) -> list[dict]:
    async with get_connection(tenant_id=current_user.tenant_id) as conn:
        query = """
            SELECT id, tenant_id, title, description, problem_statement,
                   stakeholders, available_data, expected_outcome,
                   urgency, status, composite_score, created_by,
                   created_at, updated_at
            FROM use_cases
            WHERE tenant_id = %(tenant_id)s
        """
        params: dict = {"tenant_id": current_user.tenant_id}

        if status_filter:
            query += " AND status = %(status)s"
            params["status"] = status_filter

        query += " ORDER BY created_at DESC"

        async with conn.cursor() as cur:
            await cur.execute(query, params)
            rows = await cur.fetchall()

    for row in rows:
        if isinstance(row.get("stakeholders"), str):
            row["stakeholders"] = json.loads(row["stakeholders"]) if row["stakeholders"] else []
        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()
        if row.get("updated_at"):
            row["updated_at"] = row["updated_at"].isoformat()
        # Cast enum values to str
        for field in ("urgency", "status"):
            if row.get(field):
                row[field] = str(row[field].value) if hasattr(row[field], "value") else str(row[field])

    return rows


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_use_case(
    body: UseCaseCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    use_case_id = str(uuid.uuid4())

    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            """
                INSERT INTO use_cases (
                    id, tenant_id, title, description, problem_statement,
                    stakeholders, available_data, expected_outcome,
                    urgency, status, created_by
                ) VALUES (
                    %(id)s, %(tenant_id)s, %(title)s, %(description)s, %(problem_statement)s,
                    %(stakeholders)s, %(available_data)s, %(expected_outcome)s,
                    %(urgency)s, 'new', %(created_by)s
                )
                RETURNING id, tenant_id, title, status, urgency, composite_score,
                          created_by, created_at, updated_at
                """,
            {
                "id": use_case_id,
                "tenant_id": current_user.tenant_id,
                "title": body.title,
                "description": body.description,
                "problem_statement": body.problem_statement,
                "stakeholders": json.dumps(body.stakeholders),
                "available_data": body.available_data,
                "expected_outcome": body.expected_outcome,
                "urgency": body.urgency.value,
                "created_by": current_user.user_id,
            },
        )
        row = await cur.fetchone()
        await conn.commit()

    if not row:
        raise HTTPException(status_code=500, detail="Failed to create use case")

    row["created_at"] = row["created_at"].isoformat()
    row["updated_at"] = row["updated_at"].isoformat()
    for field in ("urgency", "status"):
        if row.get(field):
            row[field] = str(row[field].value) if hasattr(row[field], "value") else str(row[field])
    return row


@router.get("/{use_case_id}")
async def get_use_case(
    use_case_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            """
                SELECT id, tenant_id, title, description, problem_statement,
                       stakeholders, available_data, expected_outcome,
                       urgency, status, composite_score, created_by,
                       created_at, updated_at
                FROM use_cases
                WHERE id = %(id)s AND tenant_id = %(tenant_id)s
                """,
            {"id": use_case_id, "tenant_id": current_user.tenant_id},
        )
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Use case not found")

    if isinstance(row.get("stakeholders"), str):
        row["stakeholders"] = json.loads(row["stakeholders"]) if row["stakeholders"] else []
    row["created_at"] = row["created_at"].isoformat()
    row["updated_at"] = row["updated_at"].isoformat()
    for field in ("urgency", "status"):
        if row.get(field):
            row[field] = str(row[field].value) if hasattr(row[field], "value") else str(row[field])
    return row


@router.patch("/{use_case_id}")
async def update_use_case(
    use_case_id: str,
    body: UseCaseUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    updates: dict = {}

    if body.title is not None:
        updates["title"] = body.title
    if body.description is not None:
        updates["description"] = body.description
    if body.problem_statement is not None:
        updates["problem_statement"] = body.problem_statement
    if body.stakeholders is not None:
        updates["stakeholders"] = json.dumps(body.stakeholders)
    if body.available_data is not None:
        updates["available_data"] = body.available_data
    if body.expected_outcome is not None:
        updates["expected_outcome"] = body.expected_outcome
    if body.urgency is not None:
        updates["urgency"] = body.urgency.value
    if body.status is not None:
        updates["status"] = body.status.value

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{k} = %({k})s" for k in updates)
    updates["id"] = use_case_id
    updates["tenant_id"] = current_user.tenant_id

    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            f"""
                UPDATE use_cases
                SET {set_clause}, updated_at = NOW()
                WHERE id = %(id)s AND tenant_id = %(tenant_id)s
                RETURNING id, tenant_id, title, status, urgency, composite_score,
                          created_by, created_at, updated_at
                """,
            updates,
        )
        row = await cur.fetchone()
        await conn.commit()

    if not row:
        raise HTTPException(status_code=404, detail="Use case not found")

    row["created_at"] = row["created_at"].isoformat()
    row["updated_at"] = row["updated_at"].isoformat()
    for field in ("urgency", "status"):
        if row.get(field):
            row[field] = str(row[field].value) if hasattr(row[field], "value") else str(row[field])
    return row


@router.delete("/{use_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_use_case(
    use_case_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> None:
    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            """
                UPDATE use_cases
                SET status = 'archived', updated_at = NOW()
                WHERE id = %(id)s AND tenant_id = %(tenant_id)s
                """,
            {"id": use_case_id, "tenant_id": current_user.tenant_id},
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Use case not found")
        await conn.commit()
