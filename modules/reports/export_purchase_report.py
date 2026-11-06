from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    Alignment,
    PatternFill,
    Border,
    Side,
)
from openpyxl.utils import get_column_letter
from modules.purchase.models import PurchaseBill
from modules.reports.repository import apply_purchase_filters, build_purchase_report_query

async def export_purchase_report(
    db,
    from_date,
    to_date,
    product_id,
    payment_status,
):

    # --------------------------------
    # Get purchase records
    # --------------------------------

    query = build_purchase_report_query()

    query = apply_purchase_filters(
        query,
        from_date,
        to_date,
        product_id,
        payment_status,
    )

    query = query.order_by(
        PurchaseBill.bill_date.desc()
    )

    result = await db.execute(query)

    purchases = (
        result
        .scalars()
        .unique()
        .all()
    )

    # --------------------------------
    # Find all dynamic expense keys
    # --------------------------------

    expense_keys = set()

    for purchase in purchases:

        item = purchase.purchase_bill_item

        expenses = (
            item.expenses or {}
        )

        expense_keys.update(
            expenses.keys()
        )

    # Sort columns alphabetically
    # for consistent Excel output

    expense_keys = sorted(
        expense_keys
    )

    # --------------------------------
    # Create workbook
    # --------------------------------

    wb = Workbook()

    ws = wb.active

    ws.title = "Purchase Report"

    # --------------------------------
    # Dynamic headers
    # --------------------------------

    headers = [

        "Bill No",

        "Bill Date",

        "Farmer Name",

        "Product",

        "Weight",

        "Rate",

        "Gross Amount",

        # Dynamic expense columns

        *[
            key.replace(
                "_",
                " "
            ).title()
            for key in expense_keys
        ],

        "Total Expense",

        "Net Amount",

        "Remark",

    ]

    # --------------------------------
    # Merge title dynamically
    # --------------------------------

    last_column = (
        get_column_letter(
            len(headers)
        )
    )

    ws.merge_cells(
        f"A1:{last_column}1"
    )

    ws["A1"] = (
        "MyTradeMaster Purchase Report"
    )

    ws["A1"].font = Font(
        bold=True,
        size=16,
        color="FFFFFF",
    )

    ws["A1"].alignment = Alignment(
        horizontal="center"
    )

    ws["A1"].fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78",
    )

    ws.row_dimensions[1].height = 30

    # Empty row

    ws.append([])

    # Add headers

    ws.append(headers)

    # --------------------------------
    # Header style
    # --------------------------------

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="D9EAF7",
    )

    for cell in ws[3]:

        cell.font = Font(
            bold=True
        )

        cell.fill = (
            header_fill
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

    # --------------------------------
    # Totals
    # --------------------------------

    total_weight = 0

    total_gross_amount = 0

    total_expenses = {
        key: 0
        for key in expense_keys
    }

    total_expense_amount = 0

    total_net_amount = 0

    # --------------------------------
    # Add purchase rows
    # --------------------------------

    for purchase in purchases:

        item = (
            purchase
            .purchase_bill_item
        )

        expenses = (
            item.expenses or {}
        )

        # Dynamic values

        expense_values = []

        for key in expense_keys:

            value = float(
                expenses.get(
                    key,
                    0,
                )
                or 0
            )

            expense_values.append(
                value
            )

            total_expenses[key] += (
                value
            )

        # Calculate total expense

        current_total_expense = sum(
            expense_values
        )

        gross_amount = float(
            item.total_amount or 0
        )

        # If your total_amount is
        # already the final amount,
        # change this calculation.

        net_amount = (
            gross_amount
            - current_total_expense
        )

        # Enum must be converted

        remark = (
            purchase.remarks.value
            if purchase.remarks
            else ""
        )

        # Create row

        ws.append([

            purchase.bill_no,

            purchase.bill_date.strftime(
                "%d-%m-%Y"
            ),

            purchase.user.party_name,

            item.product.product_name,

            float(
                item.weight or 0
            ),

            float(
                item.rate or 0
            ),

            gross_amount,

            *expense_values,

            current_total_expense,

            net_amount,

            remark,

        ])

        # Update totals

        total_weight += float(
            item.weight or 0
        )

        total_gross_amount += (
            gross_amount
        )

        total_expense_amount += (
            current_total_expense
        )

        total_net_amount += (
            net_amount
        )

    # --------------------------------
    # Add total row
    # --------------------------------

    total_row = [

        "TOTAL",

        "",

        "",

        "",

        total_weight,

        "",

        total_gross_amount,

        *[
            total_expenses[key]
            for key in expense_keys
        ],

        total_expense_amount,

        total_net_amount,

        "",

    ]

    ws.append(
        total_row
    )

    # --------------------------------
    # Style total row
    # --------------------------------

    total_row_number = (
        ws.max_row
    )

    for cell in ws[
        total_row_number
    ]:

        cell.font = Font(
            bold=True
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="E2F0D9",
        )

    # --------------------------------
    # Number formatting
    # --------------------------------

    for row in ws.iter_rows(
        min_row=4,
        max_row=ws.max_row,
    ):

        # Weight

        row[4].number_format = (
            "0.00"
        )

        # Rate, gross amount,
        # dynamic expenses,
        # total expense,
        # net amount

        for index in range(
            5,
            len(headers) - 1,
        ):

            row[index].number_format = (
                '#,##0.00'
            )

    # --------------------------------
    # Add borders
    # --------------------------------

    thin_border = Border(

        left=Side(
            style="thin"
        ),

        right=Side(
            style="thin"
        ),

        top=Side(
            style="thin"
        ),

        bottom=Side(
            style="thin"
        ),

    )

    for row in ws.iter_rows(
        min_row=3,
        max_row=ws.max_row,
    ):

        for cell in row:

            cell.border = (
                thin_border
            )

    # --------------------------------
    # Auto column width
    # --------------------------------

    for column in ws.columns:

        max_length = 0

        column_letter = (
            get_column_letter(
                column[0].column
            )
        )

        for cell in column:

            if (
                cell.value
                is not None
            ):

                max_length = max(

                    max_length,

                    len(
                        str(
                            cell.value
                        )
                    ),

                )

        ws.column_dimensions[
            column_letter
        ].width = (
            max_length + 4
        )

    # --------------------------------
    # Freeze header
    # --------------------------------

    ws.freeze_panes = "A4"

    # --------------------------------
    # Save
    # --------------------------------

    path = (
        "purchase_report.xlsx"
    )

    wb.save(
        path
    )

    return path