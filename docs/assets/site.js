// SPDX-License-Identifier: AGPL-3.0-or-later
// CVfacile site: template viewer, scroll reveals and analytics events.
// The page works without this file: every template, caption and PDF link is in the HTML.

(function () {
  // Analytics (assets/analytics.js). Does nothing when PostHog is not configured.
  const track = (event, properties) => { if (window.cvfTrack) window.cvfTrack(event, properties); };
  const where = (el) => {
    const zone = el.closest("nav, footer, section, header, dialog");
    return zone ? (zone.tagName === "NAV" ? "nav" : zone.id || zone.tagName.toLowerCase()) : "page";
  };

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
        track("template_previewed", { template: fig.dataset.name });
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
      track("template_prompt_copied", { template: btn.closest(".tpl").dataset.name });
      btn.textContent = btn.dataset.done;
      btn.classList.add("done");
      setTimeout(() => { btn.textContent = btn.dataset.label; btn.classList.remove("done"); }, 1600);
    });
  });

  // Link clicks worth measuring: the main CTA, GitHub, PDFs, language switch, docs.
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[href]");
    if (!a) return;
    const href = a.getAttribute("href");
    if (href === "#start") {
      track("get_started_clicked", { location: where(a) });
    } else if (a.id === "viewer-pdf" || a.classList.contains("pdf")) {
      const tpl = a.closest(".tpl");
      track("template_pdf_opened", {
        template: tpl ? tpl.dataset.name : document.getElementById("viewer-name").textContent,
        from: tpl ? "card" : "viewer",
      });
    } else if (a.hasAttribute("hreflang")) {
      track("language_switched", { to: a.getAttribute("hreflang"), location: where(a) });
    } else if (/github\.com\/nem95\/CVFacile\/?(#readme)?$/.test(href)) {
      track("github_clicked", { location: where(a), target: href.endsWith("#readme") ? "readme" : "repo" });
    } else if (/github\.com\/nem95\/CVFacile\/blob\//.test(href)) {
      track("repo_doc_opened", { doc: href.split("/").pop(), location: where(a) });
    }
  });

  // FAQ: which questions people open.
  document.querySelectorAll(".faq details").forEach((d) => {
    d.addEventListener("toggle", () => {
      if (d.open) track("faq_question_opened", { question: d.querySelector("summary").textContent.trim() });
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
