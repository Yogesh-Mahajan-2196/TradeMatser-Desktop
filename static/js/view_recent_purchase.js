function purchaseBills() {
  return {
    purchases: [],

    page: 1,
    pageSize: 10,

    totalRecords: 0,
    totalPages: 0,

    loading: false,
    error: null,

    
    async loadPurchases(pageNumber = 1) {
        this.loading = true;
        this.error = null;
        
    console.log("recent_purchase.js loaded");
      try {
        const token = localStorage.getItem("access_token");

        const response = await fetch(
          `/api/recent-purchases?page=${pageNumber}&page_size=${this.pageSize}`,
          {
            method: "GET",

            headers: {
              "Content-Type": "application/json",

              ...(token
                ? {
                    Authorization: `Bearer ${token}`,
                  }
                : {}),
            },
          }
        );

        if (!response.ok) {
          let errorMessage = "Failed to load purchase bills.";

          try {
            const errorData = await response.json();

            errorMessage =
              errorData.detail || errorMessage;
          } catch {
            // Keep the default error message.
          }

          throw new Error(errorMessage);
        }

        const result = await response.json();

        this.purchases = result.data || [];

        this.page = result.page;

        this.pageSize = result.page_size;

        this.totalRecords = result.total_records;

        this.totalPages = result.total_pages;

      } catch (error) {
        console.error(
          "Purchase API error:",
          error
        );

        this.error = error.message;

        this.purchases = [];

      } finally {
        this.loading = false;
      }
    },

    previousPage() {
      if (
        this.page > 1 &&
        !this.loading
      ) {
        this.loadPurchases(
          this.page - 1
        );
      }
    },

    nextPage() {
      if (
        this.page < this.totalPages &&
        !this.loading
      ) {
        this.loadPurchases(
          this.page + 1
        );
      }
    },

    formatDate(dateValue) {
      if (!dateValue) {
        return "-";
      }

      return new Date(
        dateValue
      ).toLocaleDateString(
        "en-GB",
        {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
        }
      );
    },

    formatAmount(amount) {
      return Number(
        amount || 0
      ).toLocaleString(
        "en-IN",
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }
      );
    },
  };
}