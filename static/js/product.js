function productManager() {
  return {
    products: [],

    loading: false,

    saving: false,

    error: null,

    formError: null,

    showModal: false,

    isEditMode: false,

    form: {
    id: null,

    product_name: "",

    unit: "",
    },

    async loadProducts() {  
        this.loading = true;
        this.error = null;

        try {
            const token = localStorage.getItem("access_token");

            const response = await fetch("/api/get-products", {
            method: "GET",

            headers: {
                ...(token
                ? {
                    Authorization: `Bearer ${token}`,
                    }
                : {}),
            },
            });

            if (!response.ok) {
            const errorData = await response.json();

            throw new Error(errorData.detail || "Failed to load products.");
            }

            this.products = await response.json();
        } catch (error) {
            console.error("Product loading error:", error);

            this.error = error.message;
        } finally {
            this.loading = false;
        }
    },

    openCreateModal() {
        this.isEditMode = false;

        this.formError = null;

        this.form = {
            id: null,

            product_name: "",

            unit: "",
        };

        this.showModal = true;
    },

    openUpdateModal(product) {
        this.isEditMode = true;

        this.formError = null;

        this.form = {
            id: product.produc_id,

            product_name: product.product_name,

            unit: product.unit,
        };

        this.showModal = true;
    },

    closeModal() {
        if (this.saving) {
            return;
        }
        this.showModal = false;

        this.formError = null;

        this.form = {
            id: null,
            product_name: "",
            unit: "",
        };

        this.isEditMode = false;
    },

    async saveProduct() {
        this.saving = true;
        this.formError = null;

        try {
            const token = localStorage.getItem("access_token");
            const url = this.isEditMode ? "/api/update-product" : "/api/create-product";
            const method = this.isEditMode ? "PUT" : "POST";

            let requestData;
            if (this.isEditMode) {
                requestData = { id: this.form.id, product_name: this.form.product_name, unit: this.form.unit };
            } else {
                requestData = { product_name: this.form.product_name, unit: this.form.unit };
            }

            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                body: JSON.stringify(requestData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Unable to save product.");
            }

            this.saving = false;   // reset BEFORE closeModal so the guard doesn't block it
            this.closeModal();
            await this.loadProducts();
        } catch (error) {
            console.error("Product save error:", error);
            this.formError = error.message;
        } finally {
            this.saving = false;  // still safe to keep here for the error path
        }
    },
  };
}
