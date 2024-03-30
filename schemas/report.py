from pydantic import AnyUrl, BaseModel, Field


class PeopleInZone(BaseModel):
    total: str = Field(alias="Всего")
    aquazone: int = Field(alias="Аквазона")


class TotalByDayResult(BaseModel):
    ok: bool = Field(False)
    google_report: AnyUrl | None = Field(None, alias="Google Report")
    detail: str | None = Field(None)


class FinanceReportResult(BaseModel):
    ok: bool = Field(False)
    google_report: AnyUrl | None = Field(None, alias="Google Report")
    telegram_message: str | None = Field(None, alias="Telegram Message")
    detail: str | None = Field(None)
