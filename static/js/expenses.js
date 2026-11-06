function expenseManager() {
  return {
    // =========================
    // Expense table
    // =========================
    records: [],
    loading: false,
    error: "",

    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,

    filters: {
      from_date: "",
      to_date: "",
      category: "",
    },

    // =========================
    // Expense summary
    // =========================
    summary: {
      total_expense: 0,
      categories: [],
    },

    chart: null,

    // =========================
    // Create expense modal
    // =========================
    createModalOpen: false,
    createLoading: false,
    createError: "",

    createForm: {
      expense_name: "",
      category: "",
      amount: "",
    },

    // =========================
    // Edit expense modal
    // =========================
    editModalOpen: false,
    editLoading: false,
    editError: "",
    editExpense: {},
    editForm: {
      expense_name: "",
      category: "",
      amount: "",
    },

    // =========================
    // Delete confirmation modal
    // =========================
    deleteModalOpen: false,
    deleteLoading: false,
    deleteError: "",

    deleteExpenseData: {},

    // =========================
    // Selected category
    // =========================
    selectedCategory: "",

    // =========================
    // Initialize page
    // =========================
    async init() {
      await Promise.all([this.loadExpenses(1), this.loadSummary()]);
    },

    // =========================
    // Check active filters
    // =========================
    get hasActiveFilters() {
      return Object.values(this.filters).some(
        (value) => value !== "" && value !== null && value !== undefined,
      );
    },

    // =========================
    // Load expense records
    // =========================
    async loadExpenses(requestedPage = 1) {
      this.page = requestedPage;
      this.loading = true;
      this.error = "";

      try {
        const params = new URLSearchParams();

        params.append("page", this.page);
        params.append("page_size", this.pageSize);

        if (this.filters.from_date) {
          params.append("from_date", this.filters.from_date);
        }

        if (this.filters.to_date) {
          params.append("to_date", this.filters.to_date);
        }

        if (this.filters.category) {
          params.append("category", this.filters.category);
        }

        const response = await fetch(`/api/get-expenses?${params.toString()}`, {
          method: "GET",
          credentials: "include",
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.detail || "Unable to load expenses.");
        }

        this.records = data.items || [];

        this.total = Number(data.total || 0);

        this.page = Number(data.page || requestedPage);

        this.pageSize = Number(data.page_size || this.pageSize);

        this.totalPages = Number(data.total_pages || 0);
      } catch (error) {
        console.error("Expense load error:", error);

        this.error = error.message || "Unable to load expenses.";

        this.records = [];
      } finally {
        this.loading = false;
      }
    },

    // =========================
    // Load category summary
    // =========================
    async loadSummary() {
      try {
        const params = new URLSearchParams();

        if (this.filters.from_date) {
          params.append("from_date", this.filters.from_date);
        }

        if (this.filters.to_date) {
          params.append("to_date", this.filters.to_date);
        }

        if (this.filters.category) {
          params.append("category", this.filters.category);
        }

        const response = await fetch(
          `/api/expense-category-summary?${params.toString()}`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.detail || "Unable to load expense summary.");
        }

        this.summary = {
          total_expense: Number(data.total_expense || 0),

          categories: data.categories || [],
        };

        await this.$nextTick();

        this.renderChart();
      } catch (error) {
        console.error("Expense summary error:", error);

        this.summary = {
          total_expense: 0,
          categories: [],
        };

        this.destroyChart();
      }
    },

    // =========================
    // Filter changed
    // =========================
    async filterChanged() {
      const { from_date, to_date } = this.filters;

      if (from_date && to_date && from_date > to_date) {
        this.error = "From date cannot be greater than To date.";

        return;
      }

      this.error = "";

      await Promise.all([this.loadExpenses(1), this.loadSummary()]);
    },

    // =========================
    // Clear filters
    // =========================
    async clearFilters() {
      this.filters = {
        from_date: "",
        to_date: "",
        category: "",
      };

      this.selectedCategory = "";

      await this.filterChanged();
    },

    // =========================
    // Pagination
    // =========================
    async previousPage() {
      if (this.page > 1) {
        await this.loadExpenses(this.page - 1);
      }
    },

    async nextPage() {
      if (this.page < this.totalPages) {
        await this.loadExpenses(this.page + 1);
      }
    },

    // =========================
    // Format amount
    // =========================
    formatAmount(value) {
      return Number(value || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    },

    // =========================
    // Format date
    // =========================
    formatDate(value) {
      if (!value) {
        return "-";
      }

      return new Date(value).toLocaleDateString("en-IN");
    },

    // =========================
    // Category colors
    // =========================
    getCategoryColor(category) {
      const colors = {
        Food: "#cbdc39",

        Transportation: "#e56d5d",

        Fuel: "#5b88bd",

        Miscellaneous: "#5ea5b8",
      };

      return colors[category] || "#94a3b8";
    },

    // =========================
    // Render chart
    // =========================
    renderChart() {
      const canvas = document.getElementById("expensePieChart");

      if (!canvas) {
        return;
      }

      this.destroyChart();

      const labels = this.summary.categories.map((item) => item.category);

      const values = this.summary.categories.map((item) =>
        Number(item.amount || 0),
      );

      if (labels.length === 0) {
        return;
      }

      const colors = this.summary.categories.map((item) =>
        this.getCategoryColor(item.category),
      );

      this.chart = new Chart(canvas, {
        type: "doughnut",

        data: {
          labels,

          datasets: [
            {
              data: values,

              backgroundColor: colors,

              borderWidth: 0,

              hoverOffset: 6,
            },
          ],
        },

        options: {
          responsive: true,

          maintainAspectRatio: false,

          cutout: "48%",

          onClick: (event, elements) => {
            if (!elements.length) {
              return;
            }

            const index = elements[0].index;

            this.openCategoryModal(labels[index]);
          },

          plugins: {
            legend: {
              display: false,
            },
          },
        },
      });
    },

    // =========================
    // Destroy old chart
    // =========================
    destroyChart() {
      if (this.chart) {
        this.chart.destroy();

        this.chart = null;
      }
    },

    // =========================
    // Create modal
    // =========================
    openCreateModal() {
      this.createForm = {
        expense_name: "",
        category: "",
        amount: "",
      };

      this.createError = "";

      this.createModalOpen = true;
    },

    closeCreateModal() {
      this.createModalOpen = false;

      this.createError = "";

      this.createForm = {
        expense_name: "",
        category: "",
        amount: "",
      };
    },

    // =========================
    // Create expense
    // =========================
    async createExpense() {
      this.createError = "";

      const expenseName = this.createForm.expense_name.trim();

      if (!expenseName) {
        this.createError = "Please enter expense name.";

        return;
      }

      if (!this.createForm.category) {
        this.createError = "Please select a category.";

        return;
      }

      const amount = Number(this.createForm.amount);

      if (!amount || amount <= 0) {
        this.createError = "Please enter a valid amount.";

        return;
      }

      this.createLoading = true;

      try {
        const response = await fetch("/api/create-expense", {
          method: "POST",

          credentials: "include",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            expense_name: expenseName,

            category: this.createForm.category,

            amount,
          }),
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(result.detail || "Unable to create expense.");
        }

        // Important:
        // Set loading false
        // before closing.
        this.createLoading = false;

        this.closeCreateModal();

        await Promise.all([this.loadExpenses(1), this.loadSummary()]);
      } catch (error) {
        console.error("Create expense error:", error);

        this.createError = error.message || "Unable to create expense.";
      } finally {
        this.createLoading = false;
      }
    },

    // =========================
    // Category click
    // =========================
    async openCategoryModal(category) {
      this.selectedCategory = category;

      this.filters.category = category;

      await this.loadExpenses(1);

      document.getElementById("expenseTable")?.scrollIntoView({
        behavior: "smooth",

        block: "start",
      });
    },

    // =========================
    // Edit modal
    // =========================
    openEditModal(expense) {
      this.editExpense = {
        ...expense,
      };

      this.editForm = {
        expense_name: expense.expense_name || "",

        category: expense.category || "",

        amount: expense.amount || "",
      };

      this.editError = "";

      this.editModalOpen = true;
    },

    closeEditModal() {
      this.editModalOpen = false;

      this.editError = "";

      this.editExpense = {};

      this.editForm = {
        expense_name: "",
        category: "",
        amount: "",
      };
    },

    // =========================
    // Update expense
    // =========================
    async updateExpense() {
      this.editError = "";

      if (!this.editExpense.id) {
        this.editError = "Expense ID is missing.";

        return;
      }

      const expenseName = this.editForm.expense_name.trim();

      if (!expenseName) {
        this.editError = "Please enter expense name.";

        return;
      }

      if (!this.editForm.category) {
        this.editError = "Please select a category.";

        return;
      }

      const amount = Number(this.editForm.amount);

      if (!amount || amount <= 0) {
        this.editError = "Please enter a valid amount.";

        return;
      }

      this.editLoading = true;

      try {
        const response = await fetch(
          `/api/update-expense/${this.editExpense.id}`,
          {
            method: "PUT",

            credentials: "include",

            headers: {
              "Content-Type": "application/json",
            },

            body: JSON.stringify({
              expense_name: expenseName,

              category: this.editForm.category,

              amount,
            }),
          },
        );

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(result.detail || "Unable to update expense.");
        }

        // Important:
        // Stop loading first.
        this.editLoading = false;

        this.closeEditModal();

        await Promise.all([this.loadExpenses(this.page), this.loadSummary()]);
      } catch (error) {
        console.error("Update expense error:", error);

        this.editError = error.message || "Unable to update expense.";
      } finally {
        this.editLoading = false;
      }
    },

    // =========================
    // Delete modal
    // =========================
    openDeleteModal(expense) {
      this.deleteExpenseData = {
        ...expense,
      };

      this.deleteError = "";

      this.deleteModalOpen = true;
    },

    closeDeleteModal() {
      if (this.deleteLoading) {
        return;
      }

      this.deleteModalOpen = false;

      this.deleteError = "";

      this.deleteExpenseData = {};
    },

    // =========================
    // Confirm delete
    // =========================
    async confirmDeleteExpense() {
      const expenseId = this.deleteExpenseData.id;

      if (!expenseId) {
        this.deleteError = "Expense ID is missing.";

        return;
      }

      this.deleteLoading = true;

      this.deleteError = "";

      try {
        const response = await fetch(`/api/delete-expense/${expenseId}`, {
          method: "DELETE",

          credentials: "include",
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(result.detail || "Unable to delete expense.");
        }

        const nextPage =
          this.records.length === 1 && this.page > 1
            ? this.page - 1
            : this.page;

        // Stop loading first.
        this.deleteLoading = false;

        this.closeDeleteModal();

        await Promise.all([this.loadExpenses(nextPage), this.loadSummary()]);
      } catch (error) {
        console.error("Delete expense error:", error);

        this.deleteError = error.message || "Unable to delete expense.";
      } finally {
        this.deleteLoading = false;
      }
    },

    // =========================
    // Date label
    // =========================
    get selectedDateLabel() {
      const { from_date, to_date } = this.filters;

      if (from_date && to_date) {
        return this.formatDate(from_date) + " - " + this.formatDate(to_date);
      }

      if (from_date) {
        return this.formatDate(from_date);
      }

      return "All time";
    },
  };
}
