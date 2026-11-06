function transportManager() {
  return {
    trucks: [],

    truckNumberFilter: "",

    page: 1,

    pageSize: 8,

    totalRecords: 0,

    totalPages: 0,

    loading: false,

    error: null,
    showTruckModal: false,

    isEditMode: false,

    selectedTruckId: null,

    saving: false,

    formError: null,

    truckForm: {
      truck_number: "",
      owner_name: "",
      owner_mobile: "",
      driver_name: "",
      driver_mobile: "",
    },

    async loadTrucks(pageNumber = 1) {
      this.loading = true;

      this.error = null;

      try {
        const token = localStorage.getItem("access_token");

        const params = new URLSearchParams();

        params.append("page", pageNumber);

        params.append("page_size", this.pageSize);

        if (this.truckNumberFilter.trim()) {
          params.append("truck_number", this.truckNumberFilter.trim());
        }

        const response = await fetch(
          `/api/get-all-truck-info?${params.toString()}`,
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

          throw new Error(errorData.detail || "Unable to load trucks.");
        }

        const result = await response.json();

        this.trucks = result.data || [];

        this.page = result.page;

        this.pageSize = result.page_size;

        this.totalRecords = result.total_records;

        this.totalPages = result.total_pages;
      } catch (error) {
        console.error("Truck API error:", error);

        this.error = error.message;

        this.trucks = [];
      } finally {
        this.loading = false;
      }
    },

    previousPage() {
      if (this.page > 1 && !this.loading) {
        this.loadTrucks(this.page - 1);
      }
    },

    nextPage() {
      if (this.page < this.totalPages && !this.loading) {
        this.loadTrucks(this.page + 1);
      }
    },

    clearTruckFilter() {
      this.truckNumberFilter = "";

      this.loadTrucks(1);
    },

    /*
      Add create/update/delete
      modal methods here.
    */

    resetTruckForm() {
      this.truckForm = {
        truck_number: "",
        owner_name: "",
        owner_mobile: "",
        driver_name: "",
        driver_mobile: "",
      };

      this.selectedTruckId = null;

      this.formError = null;
    },

    openCreateModal() {
      this.resetTruckForm();

      this.isEditMode = false;

      this.showTruckModal = true;
    },

    openUpdateModal(truck) {
      this.resetTruckForm();

      this.isEditMode = true;

      this.selectedTruckId = truck.id;

      this.truckForm = {
        truck_number: truck.truck_number || "",
        owner_name: truck.owner_name || "",
        owner_mobile: truck.owner_mobile || "",
        driver_name: truck.driver_name || "",
        driver_mobile: truck.driver_mobile || "",
      };

      this.showTruckModal = true;
    },

    closeTruckModal() {
      if (this.saving) {
        return;
      }

      this.showTruckModal = false;

      this.resetTruckForm();
    },

    async saveTruck() {
      this.saving = true;

      this.formError = null;

      try {
        const token = localStorage.getItem("access_token");

        const requestData = {
          truck_number: this.truckForm.truck_number.trim().toUpperCase(),

          owner_name: this.truckForm.owner_name.trim(),

          owner_mobile: this.truckForm.owner_mobile.trim(),

          driver_name: this.truckForm.driver_name.trim(),

          driver_mobile: this.truckForm.driver_mobile.trim(),
        };

        // Create or update URL

        let url;

        let method;

        if (this.isEditMode) {
          url = `/api/update-truck-info?truck_id=${this.selectedTruckId}`;

          method = "PUT";
        } else {
          url = "/api/create-truck-info";

          method = "POST";
        }

        const response = await fetch(url, {
          method: method,

          headers: {
            "Content-Type": "application/json",

            ...(token
              ? {
                  Authorization: `Bearer ${token}`,
                }
              : {}),
          },

          body: JSON.stringify(requestData),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || "Unable to save truck information.");
        }

        // Close modal

        this.showTruckModal = false;

        // Reset form

        this.resetTruckForm();

        // Reload current page

        await this.loadTrucks(this.page);
      } catch (error) {
        console.error("Truck save error:", error);

        this.formError = error.message;
      } finally {
        this.saving = false;
      }
    },

    openDeleteModal(truck) {
      console.log("Delete truck:", truck);
    },
  };
}
