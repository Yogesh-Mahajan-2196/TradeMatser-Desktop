document.addEventListener(
    "DOMContentLoaded",
    function () {

        const purchaseAmount =
        {{ daily_summary
            .overview
            .purchase_amount
            | tojson
        }};

        const salesAmount =
        {{ daily_summary
            .overview
            .sales_amount
            | tojson
        }};

        const expenseLabels =
        {{ daily_summary
            .expense_categories
            | map(attribute="category")
            | list
            | tojson
        }};

        const expenseAmounts =
        {{ daily_summary
            .expense_categories
            | map(attribute="amount")
            | list
            | tojson
        }};


        // Purchase vs Sales chart

        const purchaseSalesCanvas =
        document.getElementById(
            "purchaseSalesChart"
        );

        if (purchaseSalesCanvas) {

        new Chart(
            purchaseSalesCanvas,
            {
            type: "bar",

            data: {
                labels: [
                "Purchase",
                "Sales",
                ],

                datasets: [
                {
                    label: "Amount",

                    data: [
                    purchaseAmount,
                    salesAmount,
                    ],

                    borderRadius: 8,
                },
                ],
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                legend: {
                    display: false,
                },
                },

                scales: {
                y: {
                    beginAtZero: true,
                },
                },
            },
            }
        );
        }


        // Expense doughnut chart

        const expenseCanvas =
        document.getElementById(
            "expenseChart"
        );

        if (
        expenseCanvas &&
        expenseLabels.length > 0
        ) {

        new Chart(
            expenseCanvas,
            {
            type: "doughnut",

            data: {
                labels: expenseLabels,

                datasets: [
                {
                    data: expenseAmounts,

                    borderWidth: 0,

                    hoverOffset: 6,
                },
                ],
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                cutout: "65%",

                plugins: {
                legend: {
                    position: "bottom",
                },
                },
            },
            }
        );
        }

    }
    );