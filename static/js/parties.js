function partyManager() {
  return {
    customers: [],

    nameFilter: "",

    mobileFilter: "",

    partyTypeFilter: "",

    page: 1,

    pageSize: 8,

    totalRecords: 0,

    totalPages: 0,

    loading: false,

    error: null,

    async loadCustomers(pageNumber = 1) {
      this.loading = true;

      this.error = null;

      try {
        const token = localStorage.getItem("access_token");

        const params = new URLSearchParams();

        params.append("page", pageNumber);

        params.append("page_size", this.pageSize);

        if (this.nameFilter.trim()) {
          params.append("name", this.nameFilter.trim());
        }

        if (this.mobileFilter.trim()) {
          params.append("mob_no", this.mobileFilter.trim());
        }

        if (this.partyTypeFilter) {
          params.append("party_type", this.partyTypeFilter);
        }

        const response = await fetch(
          `/api/get-customer?${params.toString()}`,
          {
            method: "GET",

            headers: {
              ...(token
                ? {
                    Authorization: `Bearer ${token}`,
                  }
                : {}),
            },
          },
        );

        if (!response.ok) {
          const errorData = await response.json();

          throw new Error(errorData.detail || "Failed to load parties.");
        }

        const result = await response.json();

        this.customers = result.data || [];

        this.page = result.page;

        this.pageSize = result.page_size;

        this.totalRecords = result.total_records;

        this.totalPages = result.total_pages;
      } catch (error) {
        console.error("Party API error:", error);

        this.error = error.message;

        this.customers = [];
      } finally {
        this.loading = false;
      }
    },

    searchMobile() {
        this.mobileFilter =
            this.mobileFilter.replace(
            /[^0-9]/g,
            ""
            );
        this.loadCustomers(1);
    },

    previousPage() {
      if (this.page > 1 && !this.loading) {
        this.loadCustomers(this.page - 1);
      }
    },

    nextPage() {
      if (this.page < this.totalPages && !this.loading) {
        this.loadCustomers(this.page + 1);
      }
    },

    clearFilters() {
      this.nameFilter = "";

      this.mobileFilter = "";

      this.partyTypeFilter = "";

      this.loadCustomers(1);
    },
  };
}
