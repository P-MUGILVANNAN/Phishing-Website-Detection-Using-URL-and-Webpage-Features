from fastapi import APIRouter, Request, HTTPException, status
from typing import Optional
from app.services.dataset_service import dataset_service
from app.schemas.dataset import DatasetValidateRequest

router = APIRouter()

@router.post("/datasets/validate")
async def validate_dataset(request: Request):
    content_type = request.headers.get("content-type", "").lower()
    url_column = "url"
    label_column = "label"
    html_column = "html_text"
    csv_text = ""

    if "application/json" in content_type:
        body = await request.json()
        csv_text = body.get("csv_text", "")
        url_column = body.get("url_column", "url")
        label_column = body.get("label_column", "label")
        html_column = body.get("html_column", "html_text")
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        url_column = str(form.get("url_column", "url"))
        label_column = str(form.get("label_column", "label"))
        html_column = form.get("html_column")
        if html_column:
            html_column = str(html_column)

        file = form.get("file")
        if file and hasattr(file, "read"):
            content_bytes = await file.read()
            csv_text = content_bytes.decode("utf-8", errors="replace")
        elif "csv_text" in form:
            csv_text = str(form["csv_text"])
    else:
        # Default try parsing JSON or raw body
        try:
            body = await request.json()
            csv_text = body.get("csv_text", "")
            url_column = body.get("url_column", "url")
            label_column = body.get("label_column", "label")
            html_column = body.get("html_column", "html_text")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supported content types: application/json or multipart/form-data"
            )

    if not csv_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV text or file upload must be provided."
        )

    res = dataset_service.validate_and_parse_csv(
        csv_content=csv_text,
        url_col=url_column,
        label_col=label_column,
        html_col=html_column
    )

    if not res["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=res["error_message"]
        )

    return {
        "status": "VALID",
        "quality_report": res["quality_report"]
    }
