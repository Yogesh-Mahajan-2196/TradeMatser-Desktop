def get_daily_report_body(report: dict) -> str:

    def format_amount(value):
        return f"{float(value or 0):,.2f}"

    def format_quantity(value):
        return f"{float(value or 0):,.2f}"

    return f"""
    <!DOCTYPE html>
    <html>

    <body style="
        margin: 0;
        padding: 20px;
        font-family: Arial, sans-serif;
        background-color: #f4f6f8;
        color: #343a40;
    ">

        <div style="
            max-width: 750px;
            margin: auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
        ">

            <!-- Header -->

            <div style="
                padding: 25px;
                text-align: center;
                background-color: #365b7f;
                color: white;
            ">

                <h1 style="
                    margin: 0;
                    font-size: 32px;
                ">
                    MyTradeMaster
                </h1>

                <p style="
                    margin: 15px 0 0;
                    font-size: 18px;
                ">
                    Daily Business Report
                </p>

            </div>

            <!-- Content -->

            <div style="padding: 30px;">

                <p>
                    <strong>Report Date:</strong>
                    {report["date"]}
                </p>

                <!-- Purchase Report -->

                <h2 style="
                    margin-top: 30px;
                    color: #343a40;
                ">
                    Purchase Report
                </h2>

                <table style="
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                ">

                    <tr>
                        <td style="
                            width: 65%;
                            padding: 7px 10px;
                        ">
                            Total Purchase Bills
                        </td>

                        <td style="
                            width: 35%;
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            {report["purchase"]["total_bills"]}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Total Purchase Quantity
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            {format_quantity(
                                report["purchase"]["total_quantity"]
                            )}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Average Purchase Rate
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            ₹{format_amount(
                                report["purchase"]["average_rate"]
                            )}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Total Paid Amount
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            ₹{format_amount(
                                report["purchase"]["paid_amount"]
                            )}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Total Unpaid Amount
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            ₹{format_amount(
                                report["purchase"]["unpaid_amount"]
                            )}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 9px 10px;
                            font-weight: bold;
                        ">
                            Total Purchase Amount
                        </td>

                        <td style="
                            padding: 9px 10px;
                            text-align: right;
                            font-weight: bold;
                        ">
                            ₹{format_amount(
                                report["purchase"]["total_amount"]
                            )}
                        </td>
                    </tr>

                </table>

                <!-- Sell Report -->

                <h2 style="
                    margin-top: 45px;
                    color: #343a40;
                ">
                    Sell Report
                </h2>

                <table style="
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                ">

                    <tr>
                        <td style="
                            width: 65%;
                            padding: 7px 10px;
                        ">
                            Total Sell Bills
                        </td>

                        <td style="
                            width: 35%;
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            {report["sell"]["total_bills"]}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Total Sell Quantity
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            {format_quantity(
                                report["sell"]["total_quantity"]
                            )}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Total Bags
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            {report["sell"]["total_bags"]}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 7px 10px;
                        ">
                            Total Weight
                        </td>

                        <td style="
                            padding: 7px 10px;
                            text-align: right;
                        ">
                            {format_quantity(
                                report["sell"]["total_weight"]
                            )}
                        </td>
                    </tr>

                    <tr>
                        <td style="
                            padding: 9px 10px;
                            font-weight: bold;
                        ">
                            Total Sell Amount
                        </td>

                        <td style="
                            padding: 9px 10px;
                            text-align: right;
                            font-weight: bold;
                        ">
                            ₹{format_amount(
                                report["sell"]["total_amount"]
                            )}
                        </td>
                    </tr>

                </table>

            </div>

            <!-- Footer -->

            <div style="
                padding: 15px;
                text-align: center;
                background-color: #f1f1f1;
                color: #666;
                font-size: 12px;
            ">

                This is an automatically generated report.
                Please do not reply to this email.

            </div>

        </div>

    </body>
    </html>
    """