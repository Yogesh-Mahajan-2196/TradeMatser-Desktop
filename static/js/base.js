// document.addEventListener("DOMContentLoaded", function () {
//   const sidebar = document.getElementById("sidebar");
//   const overlay = document.getElementById("sidebarOverlay");
//   const openButton = document.getElementById("openSidebar");
//   const closeButton = document.getElementById("closeSidebar");

//   // Open sidebar
//   function openSidebar() {
//     if (!sidebar || !overlay) return;

//     sidebar.classList.remove("-translate-x-full");
//     sidebar.classList.add("translate-x-0");

//     overlay.classList.remove("hidden");

//     document.body.classList.add("overflow-hidden");
//   }

//   // Close sidebar
//   function closeSidebar() {
//     if (!sidebar || !overlay) return;

//     sidebar.classList.remove("translate-x-0");
//     sidebar.classList.add("-translate-x-full");

//     overlay.classList.add("hidden");

//     document.body.classList.remove("overflow-hidden");
//   }

//   // Open button click
//   if (openButton) {
//     openButton.addEventListener("click", openSidebar);
//   }

//   // Close button click
//   if (closeButton) {
//     closeButton.addEventListener("click", closeSidebar);
//   }

//   // Click outside sidebar
//   if (overlay) {
//     overlay.addEventListener("click", closeSidebar);
//   }

//   // Close when user clicks sidebar route
//   const sidebarLinks = sidebar.querySelectorAll("a");

//   sidebarLinks.forEach(function (link) {
//     link.addEventListener("click", function () {
//       if (window.innerWidth < 1024) {
//         closeSidebar();
//       }
//     });
//   });

//   // Close using Escape key
//   document.addEventListener("keydown", function (event) {
//     if (event.key === "Escape") {
//       closeSidebar();
//     }
//   });

//   // Remove mobile sidebar state on desktop
//   window.addEventListener("resize", function () {
//     if (window.innerWidth >= 1024) {
//       sidebar.classList.remove(
//         "-translate-x-full",
//         "translate-x-0"
//       );

//       overlay.classList.add("hidden");

//       document.body.classList.remove("overflow-hidden");
//     } else {
//       sidebar.classList.remove("translate-x-0");
//       sidebar.classList.add("-translate-x-full");
//     }
//   });
// });

async function apiFetch(
  url,
  options = {},
) {
  const token =
    localStorage.getItem(
      "access_token",
    );

  const headers = {
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization =
      `Bearer ${token}`;
  }

  return fetch(
    url,
    {
      ...options,
      headers,
    },
  );
}