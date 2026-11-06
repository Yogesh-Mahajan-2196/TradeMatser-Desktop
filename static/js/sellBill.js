function sellBill(initialBillNo) {
  return {
    // =====================================================
    // STATE
    // =====================================================

    saving: false,

    products: [],
    billDate: "",
    grossAmount: 0,
    totalExpenses: 0,
    netAmount: 0,

    amountInWords: "Zero Rupees Only.",

    // =====================================================
    // DEFAULT FORM
    // =====================================================

    getInitialForm() {
      return {
        bill_no: initialBillNo,
        bill_date: this.getTodayDate(),
        company_name: "",
        address: "",
        broker_name: "",
        truck_no: "",
        po_no: "",
        bags: 0,
        remarks: "Unpaid",
      };
    },

    getInitialDetails() {
      return {
        product_id: 0,
        weight: 0,
        rate: 0,
        expenses: 0,
      };
    },

    // =====================================================
    // FORM STATE
    // =====================================================

    form: {
      bill_no: initialBillNo,
      bill_date: "",
      company_name: "",
      address: "",
      broker_name: "",
      truck_no: "",
      po_no: "",
      bags: 0,
      remarks: "Unpaid",
    },

    details: {
      product_id: 0,
      weight: 0,
      rate: 0,
      expenses: 0,
    },

    // =====================================================
    // INIT
    // =====================================================

    async init() {
      this.form = this.getInitialForm();

      await this.loadProducts();

      this.calculateTotals();
    },

    // =====================================================
    // DATE
    // =====================================================

    getTodayDate() {
      const today = new Date();

      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, "0");
      const day = String(today.getDate()).padStart(2, "0");

      const date = `${year}-${month}-${day}`;
      this.billDate = date;
      return date;
    },

    // =====================================================
    // LOAD PRODUCTS
    // =====================================================

    async loadProducts() {
      try {
        const response = await fetch("/api/get-products", {
          credentials: "include",
          headers: {
            Accept: "application/json",
          },
        });

        if (!response.ok) {
          throw new Error("Unable to load products.");
        }

        const data = await response.json();

        const productList = Array.isArray(data)
          ? data
          : (data.data ?? data.products ?? data.records ?? []);

        this.products = productList.map((item) => ({
          id: Number(item.product_id ?? item.produc_id ?? item.id ?? 0),
          product_name: item.product_name ?? "",
          unit: item.unit ?? "",
        }));
      } catch (error) {
        console.error("Product loading failed:", error);
        this.products = [];
      }
    },

    // =====================================================
    // PRODUCT CHANGE
    // =====================================================

    productChanged() {
      this.calculateTotals();
    },

    // =====================================================
    // CALCULATE TOTALS
    // =====================================================

    calculateTotals() {
      const weight = Number(this.details.weight) || 0;
      const rate = Number(this.details.rate) || 0;
      const expenses = Number(this.details.expenses) || 0;

      this.grossAmount = weight * rate;

      this.totalExpenses = expenses;

      this.netAmount = Math.max(this.grossAmount - this.totalExpenses, 0);

      this.amountInWords = this.numberToWords(this.netAmount);
    },

    // =====================================================
    // FORMAT AMOUNT
    // =====================================================

    formatAmount(value) {
      return (Number(value) || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    },

    // =====================================================
    // VALIDATION
    // =====================================================

    validateBill() {
      const validations = [
        [this.form.bill_no, "Bill number is required."],
        [this.form.bill_date, "Bill date is required."],
        [this.form.company_name.trim(), "Company name is required."],
        [this.form.broker_name.trim(), "Broker name is required."],
        [this.details.product_id, "Please select a product."],
        [Number(this.details.weight) > 0, "Weight must be greater than 0."],
        [Number(this.details.rate) > 0, "Rate must be greater than 0."],
        [this.form.truck_no.trim(), "Truck number is required."],
        [Number(this.form.bags) > 0, "Bags must be greater than 0."],
      ];

      for (const [condition, message] of validations) {
        if (!condition) {
          alert(message);
          return false;
        }
      }

      return true;
    },

    // =====================================================
    // SAVE BILL
    // =====================================================

    async saveBill() {
      if (this.saving) {
        return;
      }

      if (!this.validateBill()) {
        return;
      }

      this.calculateTotals();

      const payload = {
        bill_header: {
          bill_no: Number(this.form.bill_no),

          bill_date: this.form.bill_date,

          company_name: this.form.company_name.trim(),

          address: this.form.address.trim(),

          broker_name: this.form.broker_name.trim(),

          truck_no: this.form.truck_no.trim(),

          po_no: this.form.po_no.trim() || null,

          bags: Number(this.form.bags),

          remarks: this.form.remarks || "Unpaid",
        },

        bill_details: {
          product_id: Number(this.details.product_id),

          weight: Number(this.details.weight),

          rate: Number(this.details.rate),

          expenses: Number(this.details.expenses) || 0,
        },
      };

      this.saving = true;

      try {
        const response = await fetch("/api/create-sell-bill", {
          method: "POST",

          credentials: "include",

          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },

          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(this.getApiError(data));
        }

        alert("Sell bill saved successfully.");

        window.location.reload();
      } catch (error) {
        console.error("Create sell bill error:", error);

        alert(error.message || "Something went wrong.");
      } finally {
        this.saving = false;
      }
    },

    // =====================================================
    // API ERROR
    // =====================================================

    getApiError(data) {
      if (typeof data?.detail === "string") {
        return data.detail;
      }

      if (Array.isArray(data?.detail)) {
        return data.detail.map((item) => item.msg).join(", ");
      }

      return "Unable to create sell bill.";
    },

    // =====================================================
    // CLEAR BILL
    // =====================================================

    clearBill() {
      this.form = this.getInitialForm();

      this.details = this.getInitialDetails();

      this.grossAmount = 0;
      this.totalExpenses = 0;
      this.netAmount = 0;

      this.amountInWords = "Zero Rupees Only.";
    },

    // =====================================================
    // NUMBER TO WORDS
    // =====================================================

    numberToWords(amount) {
      amount = Math.round(Number(amount) || 0);

      if (amount === 0) {
        return "Zero Rupees Only.";
      }

      const ones = [
        "",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
      ];

      const tens = [
        "",
        "",
        "Twenty",
        "Thirty",
        "Forty",
        "Fifty",
        "Sixty",
        "Seventy",
        "Eighty",
        "Ninety",
      ];

      const convertBelowThousand = (number) => {
        let result = "";

        if (number >= 100) {
          result += `${ones[Math.floor(number / 100)]} Hundred `;

          number %= 100;
        }

        if (number >= 20) {
          result += `${tens[Math.floor(number / 10)]} `;

          number %= 10;
        }

        if (number > 0) {
          result += `${ones[number]} `;
        }

        return result.trim();
      };

      const crore = Math.floor(amount / 10000000);
      amount %= 10000000;

      const lakh = Math.floor(amount / 100000);
      amount %= 100000;

      const thousand = Math.floor(amount / 1000);
      amount %= 1000;

      const parts = [];

      if (crore > 0) {
        parts.push(`${convertBelowThousand(crore)} Crore`);
      }

      if (lakh > 0) {
        parts.push(`${convertBelowThousand(lakh)} Lakh`);
      }

      if (thousand > 0) {
        parts.push(`${convertBelowThousand(thousand)} Thousand`);
      }

      if (amount > 0) {
        parts.push(convertBelowThousand(amount));
      }

      return `${parts.join(" ")} Rupees Only.`;
    },
  };
}
