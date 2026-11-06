function sellExport() {
  return {
    // No data on initial page load
    records: [],
    hasPreview: false,
    loading: false,
    downloading: false,
    error: "",
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
    filters: {
      bill_no: "",
      from_date: "",
      to_date: "",
      product_id: "",
      payment_status: "",
    },
    editModalOpen: false,
    saving: false,
    editError: "",
    editBill: {},
    editForm: {
      remark: "",
      expense: 0,
    },
    billModalOpen: false,
    selectedBill: {},
    editing: false,

    get hasActiveFilters() {
      return Object.values(this.filters).some(
        (value) => value !== "" && value !== null && value !== undefined,
      );
    },

    buildQueryParams(includePagination = true) {
      const params = new URLSearchParams();

      Object.entries(this.filters).forEach(([key, value]) => {
        if (value !== "" && value !== null && value !== undefined) {
          params.append(key, value);
        }
      });

      if (includePagination) {
        params.append("page", this.page);

        params.append("page_size", this.pageSize);
      }

      return params;
    },

    async previewReport(requestedPage = 1) {
      this.page = requestedPage;

      this.loading = true;

      this.error = "";

      try {
        const params = this.buildQueryParams(true);

        const response = await fetch(
          `/api/sell-report?${params.toString()}`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));

          throw new Error(
            errorData.detail || "Unable to load purchase report.",
          );
        }

        const data = await response.json();

        /*
        Adjust these names if your API
        response uses different keys.
        */

        this.records = data.items || data.data || data.records || [];
        this.total = data.total || data.total_records || this.records.length;
        this.page = data.page || requestedPage;
        this.pageSize = data.page_size || this.pageSize;
        this.totalPages =
          data.total_pages ||
          Math.max(1, Math.ceil(this.total / this.pageSize));

        // Preview was requested,
        // so show table even if empty
        this.hasPreview = true;
      } catch (error) {
        console.error("Sell report error:", error);
        this.error = error.message;
        this.records = [];
        this.hasPreview = false;
      } finally {
        this.loading = false;
      }
    },

    async downloadExcel() {
      this.downloading = true;
      this.error = "";
      try {
        const params = this.buildQueryParams(false);
        const response = await fetch(
          `/api/sell-report/export?${params.toString()}`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || "Excel export failed.");
        }

        const fileBlob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(fileBlob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = "Sell_Report.xlsx";

        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
      } catch (error) {
        console.error("Excel export error:", error);

        this.error = error.message;
      } finally {
        this.downloading = false;
      }
    },

    previousPage() {
      if (this.page > 1) {
        this.previewReport(this.page - 1);
      }
    },

    nextPage() {
      if (this.page < this.totalPages) {
        this.previewReport(this.page + 1);
      }
    },

    clearFilters() {
      this.filters = {
        from_date: "",
        to_date: "",
        product_id: "",
        payment_status: "",
        
      };

      // Reset preview to initial state
      this.records = [];
      this.total = 0;
      this.page = 1;
      this.totalPages = 0;
      this.hasPreview = false;
      this.error = "";
    },

    formatDate(value) {
      if (!value) {
        return "-";
      }
      return new Date(value).toLocaleDateString("en-IN");
    },

    formatAmount(value) {
      if (value === null || value === undefined || value === "") {
        return "0.00";
      }

      return Number(value).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    },

    filterChanged() {
      this.page = 1;
      const { from_date, to_date, product_id, payment_status } = this.filters;

      // If all filters are empty,
      // return to initial state
      if (!this.hasActiveFilters) {
        this.records = [];
        this.total = 0;
        this.totalPages = 0;
        this.hasPreview = false;
        this.error = "";

        return;
      }

      // If one date is selected,
      // wait until both dates are selected
      if ((from_date && !to_date) || (!from_date && to_date)) {
        return;
      }

      // Validate date range
      if (from_date && to_date && from_date > to_date) {
        this.error = "From date cannot be greater than To date.";

        return;
      }

      this.error = "";

      this.previewReport(1);
    },

    formatExpenses(expenses) {
      if (!expenses || typeof expenses !== "object") {
        return "0.00";
      }

      const total = Object.values(expenses).reduce(
        (sum, amount) => sum + Number(amount || 0),
        0,
      );

      return total.toFixed(2);
    },

    openEditModal(item) {
      this.editBill = {
        ...item,
      };

      this.editForm = {
        remark: item.remark || "Unpaid",
        expense: this.getExpenseAmount(),
      };

      this.editError = "";
      this.editing = false;
      this.editModalOpen = true;
    },

    
    async saveSellBill() {
        // Validate the bill number used by the Update Sell Bill Payment modal.
        if (!this.editBill?.bill_no) {
            this.editError = "Bill number is missing.";
            return;
        }

        this.editError = "";

        // Validate the raw input before converting it to a number.
        const rawExpense = this.editForm.expense;

        if (
            rawExpense === "" ||
            rawExpense === null ||
            rawExpense === undefined
        ) {
            this.editError = "Please enter the expense amount.";
            return;
        }

        const expense = Number(rawExpense);

        if (!Number.isFinite(expense) || expense <= 0) {
            this.editError = "Expense must be a valid number greater than 0.";
            return;
        }

        if (this.saving) {
            return;
        }

        this.saving = true;

        try {
            const payload = {
                bill_no: this.editBill.bill_no,
                remark: this.editForm.remark,
                expense: expense,
            };

            const response = await fetch("/api/update-sell-bill", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify(payload),
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const detail = data.detail;

                const message = Array.isArray(detail)
                    ? detail.map((item) => item.msg).join(", ")
                    : detail || "Failed to update sell bill.";

                throw new Error(message);
            }

            // Refresh the report after a successful update.
            this.editing = false;
            this.editModalOpen = false;
            this.billModalOpen = false;

            await this.previewReport(this.page);

        } catch (error) {
            console.error("Save sell bill error:", error);
            this.editError = error.message;
        } finally {
            this.saving = false;
        }
    },

    closeEditModal() {
      if (this.saving) {
        return;
      }

      this.editModalOpen = false;
      this.editing = false;
      this.editError = "";

      this.editBill = {};

      this.editForm = {
        remark: "",
        expense: 0,
      };
    },

    openBillModal(item) {
      this.selectedBill = item;

      this.editBill = {
          ...item,
          remark: item.remark,
          expense: Number(item.expenses || 0),
      };

      this.editForm = {
          remark: item.remark,
          expense: Number(item.expenses || 0),
      };

      this.editing = false;
      this.editError = "";
      this.billModalOpen = true;
    },
    closeBillModal() {
      if (this.saving) {
        return;
      }

      this.billModalOpen = false;
      this.selectedBill = {};
    },

    getGrossAmount() {
      return Number(this.selectedBill.gross_amount || 0);
    },

    getExpenseAmount() {
      return (this.selectedBill.expenses || 0);
    },

    getNetAmount() {
      return (this.selectedBill.net_amount || 0);
    },

    startEditing() {
      this.editForm = {
          remark: this.selectedBill.remark || "",
          expense: Number(this.selectedBill.expenses || 0),
      };

      this.editError = "";
      this.editing = true;
    },

    cancelEditing() {
        this.editForm = {
            remark: this.selectedBill.remark || "",
            expense: Number(this.selectedBill.expenses || 0),
        };

        this.editError = "";
        this.editing = false;
    },

    
    init() {
      const params = new URLSearchParams(window.location.search);
      const paymentStatus = params.get("payment_status");

      if (paymentStatus) {
        this.filters.payment_status = paymentStatus.trim();

        // Wait for Alpine to update the filter before loading records.
        this.$nextTick(() => {
          this.previewReport(1);
        });
      }
    },

  };
}
