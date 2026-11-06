window.loginForm = function () {
  return {
    username: "",
    password: "",

    emailError: "",
    passwordError: "",
    serverError: "",

    loading: false,

    async login() {
      // Clear previous errors

      this.emailError = "";
      this.passwordError = "";
      this.serverError = "";

      // Validate email

      if (this.username.trim() === "") {
        this.emailError = "Email is required.";
      }

      // Validate password

      if (this.password.trim() === "") {
        this.passwordError = "Password is required.";
      }

      // Stop if validation fails

      if (
        this.emailError ||
        this.passwordError
      ) {
        return;
      }

      this.loading = true;

      try {
        const formData = new URLSearchParams();

        formData.append(
          "username",
          this.username
        );

        formData.append(
          "password",
          this.password
        );

        const response = await fetch(
          "/api/login",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/x-www-form-urlencoded",
            },
            credentials: "include",
            body: formData,
          }
        );

        const data =
          await response.json();

        if (response.ok) {
          localStorage.setItem(
            "access_token",
            data.access_token
          );

            if (data.role_id === "USER") {
                window.location.href = "/sell-bill";
            } else {
                window.location.href = "/dashboard";
            }

          return;
        }

        this.serverError =
          data.detail ||
          "Invalid email or password.";

      } catch (error) {
        console.error(
          "Login error:",
          error
        );

        this.serverError =
          "Unable to connect to the server.";

      } finally {
        this.loading = false;
      }
    },
  };
};

async function logout() {
            try {
                const response = await fetch(
                    '/logout',
                    {
                        method: 'POST',
                        credentials: 'include'
                    }
                )

                if (!response.ok) {
                    throw new Error(
                        'Logout failed'
                    )
                }

                // Redirect after cookie is deleted
                localStorage.removeItem("access_token")
                window.location.href = '/login'
            } catch (error) {
                console.error(
                    'Logout error:',
                    error
                )

                alert(
                    'Unable to logout. Please try again.'
                )
            }
        }