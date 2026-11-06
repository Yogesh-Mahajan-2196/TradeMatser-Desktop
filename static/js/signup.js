
function signupForm() {
  return {
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    confirm_password: "",
    mobile_no: "",

    loading: false,
    serverError: "",
    successMessage: "",

    errors: {
      first_name: "",
      last_name: "",
      email: "",
      password: "",
      confirm_password: "",
      mobile_no: ""
    },

    validateForm() {
      this.errors = {
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        confirm_password: "",
        mobile_no: ""
      };

      this.serverError = "";
      this.successMessage = "";

      let valid = true;

      if (!this.first_name.trim()) {
        this.errors.first_name = "First name is required.";
        valid = false;
      } else if (/<[^>]*>/.test(this.first_name)) {
        this.errors.first_name = "HTML is not allowed.";
        valid = false;
      }

      if (!this.last_name.trim()) {
        this.errors.last_name = "Last name is required.";
        valid = false;
      } else if (/<[^>]*>/.test(this.last_name)) {
        this.errors.last_name = "HTML is not allowed.";
        valid = false;
      }

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!this.email.trim()) {
        this.errors.email = "Email is required.";
        valid = false;
      } else if (!emailPattern.test(this.email.trim())) {
        this.errors.email = "Enter a valid email address.";
        valid = false;
      }

      const mobilePattern = /^[6-9]\d{9}$/;

      if (!this.mobile_no.trim()) {
        this.errors.mobile_no = "Mobile number is required.";
        valid = false;
      } else if (!mobilePattern.test(this.mobile_no.trim())) {
        this.errors.mobile_no =
          "Enter a valid 10-digit mobile number.";
        valid = false;
      }

      if (!this.password) {
        this.errors.password = "Password is required.";
        valid = false;
      } else if (
        this.password.length < 8 ||
        this.password.length > 20
      ) {
        this.errors.password =
          "Password must contain 8–20 characters.";
        valid = false;
      } else if (/\s/.test(this.password)) {
        this.errors.password = "Password must not contain spaces.";
        valid = false;
      } else if (!/[A-Z]/.test(this.password)) {
        this.errors.password =
          "Include at least one uppercase letter.";
        valid = false;
      } else if (!/[a-z]/.test(this.password)) {
        this.errors.password =
          "Include at least one lowercase letter.";
        valid = false;
      } else if (!/\d/.test(this.password)) {
        this.errors.password = "Include at least one number.";
        valid = false;
      } else if (!/[!@#$%^&*()_\-+=\[\]{};:'",.<>/?\\|`~]/.test(this.password)) {
        this.errors.password =
          "Include at least one special character.";
        valid = false;
      }

      if (!this.confirm_password) {
        this.errors.confirm_password =
          "Please confirm your password.";
        valid = false;
      } else if (this.password !== this.confirm_password) {
        this.errors.confirm_password =
          "Passwords do not match.";
        valid = false;
      }

      return valid;
    },

    async signup() {
      if (this.loading) return;

      if (!this.validateForm()) return;

      this.loading = true;
      this.serverError = "";
      this.successMessage = "";

      try {
        // Change this URL if your router has a prefix.
        const API_URL = "/api/register";

        // This endpoint requires an authenticated user.
        // Use the same token storage key as your login.js.
        // const token = localStorage.getItem("access_token");

        // if (!token) {
        //   this.serverError =
        //     "Please log in with an authorized account before creating a user.";
        //   return;
        // }

        const response = await fetch(API_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({
            first_name: this.first_name.trim(),
            last_name: this.last_name.trim(),
            email: this.email.trim(),
            password: this.password,
            confirm_password: this.confirm_password,
            mobile_no: this.mobile_no.trim()
          })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
          if (response.status === 409) {
            this.serverError =
              data.detail || "A user with this email already exists.";
          } else if (response.status === 422 && Array.isArray(data.detail)) {
            this.serverError = data.detail
              .map(error => {
                const field = error.loc?.at(-1);
                return `${field ? field + ": " : ""}${error.msg}`;
              })
              .join(" ");
          } else {
            this.serverError =
              typeof data.detail === "string"
                ? data.detail
                : "Unable to create the account. Please try again.";
          }

          return;
        }

        this.successMessage =
          data.result || "User created successfully.";

        this.first_name = "";
        this.last_name = "";
        this.email = "";
        this.password = "";
        this.confirm_password = "";
        this.mobile_no = "";

        // Return to login after a short delay.
        setTimeout(() => {
          window.location.href = "/login";
        }, 1200);

      } catch (error) {
        console.error("Signup error:", error);
        this.serverError =
          "Unable to connect to the server. Please try again.";
      } finally {
        this.loading = false;
      }
    }
  };
}
