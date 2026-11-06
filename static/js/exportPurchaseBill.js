function purchaseExport() {
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
      paid_amount: 0,
      unpaid_amount: 0,
    },
    billModalOpen: false,
    editing: false,
    selectedBill: {},
    editOriginal: {},

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
          `/api/purchase-report?${params.toString()}`,
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
        console.error("Purchase report error:", error);

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
          `/api/purchase-report/export?${params.toString()}`,
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

        link.download = "Purchase_Report.xlsx";

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

    openBillModal(item) {
      this.selectedBill = { ...item };

      this.editOriginal = { ...item };

      this.editForm = {
        paid_amount: item.paid_amount ?? 0,
        unpaid_amount: Number(item.unpaid_amount ?? 0),
      };

      this.editing = false;
      this.saving = false;
      this.editError = "";

      this.billModalOpen = true;
    },

    calculateUnpaidAmount() {
      const paidValue = this.editForm.paid_amount;

      if (paidValue === "" || paidValue === null || paidValue === undefined) {
        return;
      }

      const totalAmount = Number(
        this.selectedBill.total_amount ??
        this.selectedBill.gross_amount ??
        0
      );
      const paidAmount = Number(paidValue);

      if (!Number.isFinite(paidAmount)) {
        return;
      }

      // Clamp only — never touch editForm.unpaid_amount
      if (paidAmount < 0) {
        this.editForm.paid_amount = 0;
        return;
      }

      if (paidAmount > totalAmount) {
        this.editForm.paid_amount = totalAmount;
        return;
      }

      // unpaid_amount is intentionally left untouched — it stays fixed
    },

    async savePurchaseBill() {
      this.editError = "";

      const billNo = this.selectedBill?.bill_no;
      const rawPaid = this.editForm.paid_amount;

      if (!billNo) {
        this.editError = "Purchase bill number is missing.";
        return;
      }

      if (
        rawPaid === "" ||
        rawPaid === null ||
        rawPaid === undefined
      ) {
        this.editError = "Please enter the paid amount.";
        return;
      }

      const paidAmount = Number(rawPaid);

      if (!Number.isFinite(paidAmount) || paidAmount < 0) {
        this.editError = "Please enter a valid paid amount.";
        return;
      }

      const totalAmount = Number(
        this.selectedBill.total_amount ??
        this.selectedBill.gross_amount ??
        0
      );

      if (paidAmount > totalAmount) {
        this.editError = "Paid amount cannot exceed the total bill amount.";
        return;
      }

      this.saving = true;

      try {
        const response = await fetch(
          `/api/update-purchase-bill?bill_no=${encodeURIComponent(billNo)}`,
          {
            method: "PUT",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              paid_amount: paidAmount,
            }),
          }
        );

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            result.detail || "Unable to update purchase bill."
          );
        }

        // Update the currently selected bill if the API returns these fields.
        if (result.paid_amount !== undefined) {
          this.selectedBill.paid_amount = Number(result.paid_amount);
        } else {
          this.selectedBill.paid_amount = paidAmount;
        }

        if (result.unpaid_amount !== undefined) {
          this.selectedBill.unpaid_amount = Number(result.unpaid_amount);
        }

        if (result.remarks !== undefined) {
          this.selectedBill.remarks = result.remarks;
        } else if (result.remark !== undefined) {
          this.selectedBill.remarks = result.remark;
        }

        this.editing = false;
        this.billModalOpen = false;
        this.editError = "";

        this.selectedBill = {};
        this.editOriginal = {};

        // Reload the report with the existing filters and page.
        await this.previewReport(this.page);

      } catch (error) {
        console.error("Purchase bill update error:", error);
        this.editError = error.message || "Unable to update purchase bill.";
      } finally {
        this.saving = false;
      }
    },

    closeEditModal() {
      if (this.saving) {
        return;
      }

      this.editModalOpen = false;

      this.editError = "";

      this.editBill = {};

      this.editForm = {
        paid_amount: 0,
        unpaid_amount: 0,
      };
    },

    startEditing() {
      // The report uses "remarks", so use it consistently.
      if (this.selectedBill.remarks !== "Unpaid") {
        return;
      }

      this.editOriginal = { ...this.selectedBill };

      this.editForm = {
        paid_amount: this.selectedBill.paid_amount ?? 0,
        unpaid_amount: Number(this.selectedBill.unpaid_amount ?? 0),
      };

      this.editError = "";
      this.editing = true;
    },

    cancelEditing() {
      if (this.saving) {
        return;
      }

      this.selectedBill = { ...this.editOriginal };

      this.editForm = {
        paid_amount: this.editOriginal.paid_amount ?? 0,
        unpaid_amount: Number(this.editOriginal.unpaid_amount ?? 0),
      };

      this.editError = "";
      this.editing = false;
    },

    closeBillModal() {
      if (this.saving) {
        return;
      }

      this.billModalOpen = false;
      this.editing = false;
      this.editError = "";

      this.selectedBill = {};
      this.editOriginal = {};

      this.editForm = {
        paid_amount: 0,
        unpaid_amount: 0,
      };
    },
    
    init() {
      const params = new URLSearchParams(window.location.search);
      const paymentStatus = params.get("payment_status");

      if (paymentStatus) {
        this.filters.payment_status = paymentStatus.trim();

        this.$nextTick(() => {
          this.previewReport(1);
        });
      }
    },

  };
}
