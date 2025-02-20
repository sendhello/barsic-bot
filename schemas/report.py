from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field


class PeopleInZone(BaseModel):
    total: str = Field(alias="Всего")
    aquazone: int = Field(0, alias="Аквазона")


class TotalByDayResult(BaseModel):
    ok: bool = Field(False)
    google_report: AnyUrl | None = Field(None, alias="Google Report")
    detail: str | None = Field(None)


class FinanceReportResult(BaseModel):
    ok: bool = Field(False)
    google_report: AnyUrl | None = Field(None, alias="Google Report")
    telegram_message: str | None = Field(None, alias="Telegram Message")
    detail: str | None = Field(None)


class CorpServicesSumReportResult(BaseModel):
    ok: bool = Field(False)
    local_path: str | None = Field(None)
    public_url: AnyUrl | None = Field(None)
    download_link: AnyUrl | None = Field(None)
    detail: str | None = Field(None)


class ServicesGroup(BaseModel):
    id: UUID
    title: str


class ReportGroup(BaseModel):
    """Группа элементов в отчете"""

    id: UUID = Field(description="ID")
    title: str = Field(description="Название группы")
    parent_id: UUID | None = Field(description="ID родительской группы")
    report_name_id: UUID = Field(description="ID отчета")


class ReportElement(BaseModel):
    """Элемент отчета."""

    id: UUID = Field(description="ID")
    title: str = Field(description="Название элемента")
    group_id: UUID = Field(description="ID группы")
