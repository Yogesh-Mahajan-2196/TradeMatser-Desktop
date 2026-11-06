function purchaseBill(initialBillNo) {
  return {

    billNo: initialBillNo,
    billDate: "",
    supplierName: "",
    buyerName: "",
    buyerMobile: "",

    transportName: "",

    products: [],
    selectedProduct: "",
    selectedProductData: null,

    weightQuintal: 0,
    weightKg: 0,
    totalWeight: 0,
    rate: 0,
    totalAmount: 0,

    applyExpenses: false,
    appliedExpenseTotal: 0,
    expenses: {},

    paidAmount: 0,
    netAmount: 0,
    unpaidAmount: 0,

    amountInWords: "शून्य रुपये फक्त.",
    saving: false,

    async init() {
      this.generateBillDate();
      this.loadExpensesFromContext();
      await this.loadProducts();
      this.calculateBill();
    },

    generateBillDate() {
      const today = new Date();

      const day = String(today.getDate()).padStart(2, "0");
      const month = String(today.getMonth() + 1).padStart(2, "0");
      const year = today.getFullYear();
      this.billDate = `${day} / ${month} / ${year}`;

      return `${day} / ${month} / ${year}`;
    },

    async loadProducts() {
      try {
        const response = await fetch("/api/get-products", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Unable to load products");
        }

        const data = await response.json();

        this.products = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Product loading failed:", error);

        this.products = [];
      }
    },

    selectProduct() {
      this.selectedProductData =
        this.products.find(
          (product) => String(product.id) === String(this.selectedProduct),
        ) || null;

      this.calculateBill();
    },

    calculateBill() {
      const quintal = Number(this.weightQuintal) || 0;
      const kg = Number(this.weightKg) || 0;
      const rate = Number(this.rate) || 0;
      const paid = Number(this.paidAmount) || 0;

      // 1 quintal = 100 kg
      this.totalWeight = quintal + kg / 100;

      // Total amount
      this.totalAmount = this.totalWeight * rate;

      // Expenses
      this.appliedExpenseTotal = this.applyExpenses
        ? Object.values(this.expenses || {}).reduce(
            (total, value) => total + (Number(value) || 0),
            0
          )
        : 0;

      // Remaining amount after expenses
      const balance = this.totalAmount - this.appliedExpenseTotal;

      // Unpaid amount after paid amount
      this.netAmount = Math.max(balance - paid, 0);

      this.unpaidAmount = this.netAmount;

      // Amount in words
      this.amountInWords = this.marathiNumberToWords(
        Math.round(this.netAmount)
      );
    },

    formatMoney(value) {
      const number = Number(value) || 0;

      return new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 2,
      }).format(number);
    },

    async saveBill() {
      if (this.saving) {
        return;
      }

      // -----------------------------------------
      // BASIC VALIDATION
      // -----------------------------------------

      if (!this.supplierName.trim()) {
        alert("कृपया खरेदीदाराचे नाव भरा.");

        return;
      }

      if (!this.transportName.trim()) {
        alert("कृपया वाहन क्रमांक भरा.");

        return;
      }

      if (!this.selectedProduct) {
        alert("कृपया माल निवडा.");

        return;
      }

      if (Number(this.totalWeight) <= 0) {
        alert("कृपया वजन भरा.");

        return;
      }

      if (Number(this.rate) <= 0) {
        alert("कृपया दर भरा.");

        return;
      }

      // Make sure latest calculations exist
      this.calculateBill();

      // -----------------------------------------
      // PAID VALIDATION
      // -----------------------------------------

      if (Number(this.paidAmount) > Number(this.netAmount)) {
        alert("भरलेली रक्कम एकूण रकमेपेक्षा जास्त असू शकत नाही.");

        return;
      }

      this.saving = true;

      try {
        // -----------------------------------------
        // EXPENSE PAYLOAD
        // -----------------------------------------

        const expensesPayload = this.applyExpenses ? { ...this.expenses } : {};

        // -----------------------------------------
        // REQUEST BODY
        // -----------------------------------------

        const payload = {
          bill_header: {
            bill_no: Number(this.billNo),

            supplier_name: this.supplierName.trim(),

            vehicle_no: this.transportName.trim().toUpperCase(),

            remark:
              Number(this.paidAmount) >= Number(this.netAmount)
                ? "Paid"
                : "Unpaid",
          },

          bill_details: {
            product_id: Number(this.selectedProduct),

            weight: Number(this.totalWeight),

            rate: Number(this.rate),

            expenses: expensesPayload,

            paid_amount: Number(this.paidAmount) || 0,
          },
        };

        console.log("Purchase Bill Payload:", payload);

        // -----------------------------------------
        // API
        // -----------------------------------------

        const response = await fetch("/api/create-purchase-bill", {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          credentials: "include",

          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Purchase bill save failed.");
        }

        console.log("Purchase bill saved:", data);

        alert("Purchase bill saved successfully.");
        window.location.reload();
      } catch (error) {
        console.error("Purchase bill save error:", error);

        alert(error.message);
      } finally {
        this.saving = false;
      }
    },


    loadExpensesFromContext() {
      this.expenses = {};
      const expenseElements = document.querySelectorAll(".expense-value");

      expenseElements.forEach((element) => {
        const name = element.dataset.expenseKey;
        const amount = Number(element.dataset.expenseAmount) || 0;

        if (name) {
          this.expenses[name] = amount;
        }
        this.calculateBill();
      });
    },

    clearBill() {
      this.billNo = initialBillNo;
      this.billDate = this.generateBillDate();

      // Header
      this.supplierName = "";
      this.buyerName = "";
      this.buyerMobile = "";

      // Transport
      this.transportName = "";

      // Product
      this.selectedProduct = "";
      this.selectedProductData = null;

      // Weight & Rate
      this.weightQuintal = 0;
      this.weightKg = 0;
      this.totalWeight = 0;
      this.rate = 0;

      // Expenses
      this.applyExpenses = false;
      this.expenses = {};
      this.appliedExpenseTotal = 0;

      // Payment
      this.paidAmount = 0;

      // Amounts
      this.totalAmount = 0;
      this.netAmount = 0;
      this.unpaidAmount = 0;

      // Amount in words
      this.amountInWords = "शून्य रुपये फक्त.";

      this.saving = false;
    },

    marathiNumberToWords(number) {
      number = Number(number) || 0;

      if (number === 0) {
        return "शून्य रुपये फक्त.";
      }

      const ones = [
        "",

        "एक",

        "दोन",

        "तीन",

        "चार",

        "पाच",

        "सहा",

        "सात",

        "आठ",

        "नऊ",

        "दहा",

        "अकरा",

        "बारा",

        "तेरा",

        "चौदा",

        "पंधरा",

        "सोळा",

        "सतरा",

        "अठरा",

        "एकोणीस",
      ];

      const tens = [
        "",

        "",

        "वीस",

        "तीस",

        "चाळीस",

        "पन्नास",

        "साठ",

        "सत्तर",

        "ऐंशी",

        "नव्वद",
      ];

      const convertBelowHundred = (num) => {
        if (num < 20) {
          return ones[num];
        }

        const ten = Math.floor(num / 10);

        const one = num % 10;

        if (one === 0) {
          return tens[ten];
        }

        return `${tens[ten]} ${ones[one]}`;
      };

      const convert = (num) => {
        if (num < 100) {
          return convertBelowHundred(num);
        }

        if (num < 1000) {
          const hundred = Math.floor(num / 100);

          const remainder = num % 100;

          return (
            `${ones[hundred]}शे ` + `${remainder ? convert(remainder) : ""}`
          ).trim();
        }

        if (num < 100000) {
          const thousand = Math.floor(num / 1000);

          const remainder = num % 1000;

          return (
            `${convert(thousand)} हजार ` +
            `${remainder ? convert(remainder) : ""}`
          ).trim();
        }

        if (num < 10000000) {
          const lakh = Math.floor(num / 100000);

          const remainder = num % 100000;

          return (
            `${convert(lakh)} लाख ` + `${remainder ? convert(remainder) : ""}`
          ).trim();
        }

        const crore = Math.floor(num / 10000000);

        const remainder = num % 10000000;

        return (
          `${convert(crore)} कोटी ` + `${remainder ? convert(remainder) : ""}`
        ).trim();
      };

      return `${convert(number)} रुपये फक्त.`;
    },

    translateTransport(event) {},
  };
}
