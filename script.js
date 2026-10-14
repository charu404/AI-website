// Small UI enhancement: focus the URL box and guard against blank submissions.
document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector("#url");
  const form = document.querySelector(".scanner");
  if (input && !input.value) input.focus({ preventScroll: true });
  if (form && input) {
    form.addEventListener("submit", (event) => {
      if (!input.value.trim()) {
        event.preventDefault();
        input.focus();
      }
    });
  }
});
