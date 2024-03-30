from pydantic import AnyUrl, BaseModel, Field


class PeopleInZone(BaseModel):
    total: str = Field(alias="Всего")
    aquazone: int = Field(alias="Аквазона")


class TotalByDayResult(BaseModel):
    ok: bool = Field(False)
    google_report: AnyUrl | None = Field(alias="Google Report")
    detail: str | None = Field(alias="Детализация ошибок")


class FinanceReportResult(BaseModel):
    ok: bool = Field(False)
    google_report: AnyUrl | None = Field(alias="Google Report")
    telegram_message: str | None = Field(alias="Telegram Message")
    detail: str | None = Field(alias="Детализация ошибок")
