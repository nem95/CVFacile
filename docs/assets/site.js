// SPDX-License-Identifier: AGPL-3.0-or-later
// CVfacile site: template viewer and scroll reveals.
// The page works without this file: every template, caption and PDF link is in the HTML.

(function () {
  // Template viewer: a click on a template opens it full size.
  const viewer = document.getElementById("viewer");
  if (viewer) {
    const name = document.getElementById("viewer-name");
    const img = document.getElementById("viewer-img");
    const pdf = document.getElementById("viewer-pdf");
    document.querySelectorAll(".tpl[data-full]").forEach((fig) => {
      fig.querySelector("button").addEventListener("click", () => {
        name.textContent = fig.dataset.name;
        img.src = fig.dataset.full;
        img.alt = fig.querySelector("img").alt;
        pdf.href = fig.dataset.pdf;
        viewer.showModal();
      });
    });
    document.getElementById("viewer-close").addEventListener("click", () => viewer.close());
    viewer.addEventListener("click", (e) => { if (e.target === viewer) viewer.close(); });
  }

  // Copy prompt: puts a ready-to-paste instruction for the AI agent in the clipboard.
  document.querySelectorAll(".tpl .copy").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const text = btn.dataset.prompt;
      try {
        await navigator.clipboard.writeText(text);
      } catch (_) {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch (__) { /* nothing more to try */ }
        ta.remove();
      }
      btn.textContent = btn.dataset.done;
      btn.classList.add("done");
      setTimeout(() => { btn.textContent = btn.dataset.label; btn.classList.remove("done"); }, 1600);
    });
  });

  // Reveal blocks as they enter the viewport, once. Only when the visitor accepts motion
  // (the "motion" class is set in <head>).
  if (document.documentElement.classList.contains("motion")) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
  }
})();
