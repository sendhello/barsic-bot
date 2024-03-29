from pydantic import AnyUrl, BaseModel, Field


class PeopleInZone(BaseModel):
    total: str = Field(alias="Всего")
    aquazone: int = Field(alias="Аквазона")


class TotalByDayResult(BaseModel):
    ok: bool
    google_report: AnyUrl | None = Field(alias="Google Report")


class FinanceReportResult(TotalByDayResult):
    ok: bool
    google_report: AnyUrl | None = Field(alias="Google Report")
    telegram_message: str | None = Field(alias="Telegram Message")
