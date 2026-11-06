from datetime import date


def get_current_financial_year():

    today = date.today()

    # April to December
    if today.month >= 4:

        financial_year_start = date(
            today.year,
            4,
            1
        )

        financial_year_end = date(
            today.year + 1,
            3,
            31
        )

    # January to March
    else:

        financial_year_start = date(
            today.year - 1,
            4,
            1
        )

        financial_year_end = date(
            today.year,
            3,
            31
        )

    return (
        financial_year_start,
        financial_year_end
    )