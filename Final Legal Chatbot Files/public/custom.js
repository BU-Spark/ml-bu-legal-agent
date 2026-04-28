(function () {
  const MODE_KEY = "star_mode";
  const MODES = ["general", "tenant", "landlord"];
  const DEFAULT_LANDING_QUESTIONS = [
    "What rights do tenants have?",
    "Can my landlord increase rent?",
    "What should I do if repairs are ignored?",
  ];
  const SCALE_ICON =
    '<svg class="scale-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<path d="M12 3v14" />' +
      '<path d="M7 7h10" />' +
      '<path d="M4.5 9.5h5L7 14.5z" />' +
      '<path d="M14.5 9.5h5L17 14.5z" />' +
      '<path d="M9.5 20h5" />' +
    "</svg>";

  function titleCase(v) {
    return String(v || "").charAt(0).toUpperCase() + String(v || "").slice(1).toLowerCase();
  }

  function getActiveComposerInput() {
    const candidates = Array.from(
      document.querySelectorAll("textarea, input[type='text'], [role='textbox']")
    ).filter((el) => el instanceof HTMLElement && el.offsetParent !== null);

    if (candidates.length === 0) return null;

    // Chainlit composer is usually the lowest visible textbox on screen.
    candidates.sort((a, b) => {
      const ra = a.getBoundingClientRect();
      const rb = b.getBoundingClientRect();
      if (Math.abs(rb.bottom - ra.bottom) > 2) return rb.bottom - ra.bottom;
      return rb.width - ra.width;
    });

    return candidates[0];
  }

  function setComposerValue(input, text) {
    const tag = (input.tagName || "").toLowerCase();
    const isEditableDiv =
      input instanceof HTMLElement &&
      input.getAttribute("contenteditable") === "true";

    if (tag === "textarea" || tag === "input") {
      const proto = Object.getPrototypeOf(input);
      const nativeSetter =
        Object.getOwnPropertyDescriptor(proto, "value")?.set ||
        Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value")?.set ||
        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
      if (nativeSetter) nativeSetter.call(input, text);
      else input.value = text;
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    }

    if (isEditableDiv) {
      input.textContent = text;
      input.dispatchEvent(new InputEvent("input", { bubbles: true, data: text, inputType: "insertText" }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    }

    return false;
  }

  function submitComposer(input) {
    const form = input.closest("form");
    if (form instanceof HTMLFormElement) {
      const submitBtn = Array.from(form.querySelectorAll("button")).find((b) => {
        const aria = (b.getAttribute("aria-label") || "").toLowerCase();
        const txt = (b.textContent || "").toLowerCase().trim();
        const type = (b.getAttribute("type") || "").toLowerCase();
        return !b.disabled && (aria.includes("send") || txt === "send" || type === "submit");
      });
      if (submitBtn) {
        submitBtn.click();
        return true;
      }

      if (typeof form.requestSubmit === "function") {
        form.requestSubmit();
        return true;
      }
      const submitEvent = new Event("submit", { bubbles: true, cancelable: true });
      form.dispatchEvent(submitEvent);
      return true;
    }

    const scope = input.parentElement || document;
    const submitInScope = Array.from(scope.querySelectorAll("button")).find((b) => {
      const aria = (b.getAttribute("aria-label") || "").toLowerCase();
      const txt = (b.textContent || "").toLowerCase();
      const type = (b.getAttribute("type") || "").toLowerCase();
      return !b.disabled && (aria.includes("send") || txt === "send" || type === "submit");
    });
    if (submitInScope) {
      submitInScope.click();
      return true;
    }
    return false;
  }

  function sendAsChatInput(text) {
    const input = getActiveComposerInput();
    if (!input) return false;

    input.focus();
    setComposerValue(input, text);
    if (submitComposer(input)) return true;

    const directSendBtn = Array.from(document.querySelectorAll("button")).find((b) => {
      const aria = (b.getAttribute("aria-label") || "").toLowerCase();
      const txt = (b.textContent || "").toLowerCase();
      const type = (b.getAttribute("type") || "").toLowerCase();
      const visible = b instanceof HTMLElement && b.offsetParent !== null;
      return visible && (aria.includes("send") || txt === "send" || type === "submit");
    });
    if (directSendBtn) {
      directSendBtn.click();
      return true;
    }

    // Fallback: find the right-most button near the input/composer region.
    const inputRect = input.getBoundingClientRect();
    const nearbyButtons = Array.from(document.querySelectorAll("button"))
      .filter((b) => {
        if (!(b instanceof HTMLElement)) return false;
        const r = b.getBoundingClientRect();
        const sameBand = Math.abs(r.top - inputRect.top) < 140 || Math.abs(r.bottom - inputRect.bottom) < 140;
        const nearHorizontally = r.left > inputRect.left - 40 && r.left < inputRect.right + 220;
        const clickable = b.offsetParent !== null && !b.disabled;
        return sameBand && nearHorizontally && clickable;
      })
      .sort((a, b) => b.getBoundingClientRect().left - a.getBoundingClientRect().left);

    if (nearbyButtons.length > 0) {
      nearbyButtons[0].click();
      return true;
    }

    // Last fallback: synthesize Enter key sequence.
    ["keydown", "keypress", "keyup"].forEach((evt) => {
      input.dispatchEvent(
        new KeyboardEvent(evt, {
          bubbles: true,
          cancelable: true,
          key: "Enter",
          code: "Enter",
          keyCode: 13,
          which: 13,
        })
      );
    });
    return true;
  }

  function sendAsChatInputWithRetry(text, attempts = 6, delayMs = 120) {
    let n = 0;
    const tick = () => {
      n += 1;
      const ok = sendAsChatInput(text);
      if (!ok && n < attempts) setTimeout(tick, delayMs);
    };
    tick();
  }

  function getSavedMode() {
    const v = (localStorage.getItem(MODE_KEY) || "general").toLowerCase();
    return MODES.includes(v) ? v : "general";
  }

  function setMode(mode) {
    const next = MODES.includes(mode) ? mode : "general";
    localStorage.setItem(MODE_KEY, next);
    sendAsChatInput("/role " + next);
    updateModePanelState();
    updateModeFabLabel();
  }

  function updateModeFabLabel() {
    const fab = document.getElementById("star-mode-fab");
    if (!fab) return;
    fab.textContent = "Mode: " + titleCase(getSavedMode()) + " ▾";
  }

  function updateModePanelState() {
    const active = getSavedMode();
    document.querySelectorAll("#star-mode-panel button[data-mode]").forEach((btn) => {
      if (btn.getAttribute("data-mode") === active) btn.classList.add("star-active");
      else btn.classList.remove("star-active");
    });
  }

  function mountModeToggle() {
    let fab = document.getElementById("star-mode-fab");
    if (!fab) {
      fab = document.createElement("button");
      fab.id = "star-mode-fab";
      fab.type = "button";
      fab.title = "Select Mode";
      fab.setAttribute("aria-label", "Select Mode");
      document.body.appendChild(fab);
    }

    let panel = document.getElementById("star-mode-panel");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "star-mode-panel";
      panel.hidden = true;
      panel.innerHTML =
        '<div class="star-mode-title">Select mode</div>' +
        '<button data-mode="general" type="button">General</button>' +
        '<button data-mode="tenant" type="button">Tenant</button>' +
        '<button data-mode="landlord" type="button">Landlord</button>';
      document.body.appendChild(panel);

      panel.querySelectorAll("button[data-mode]").forEach((btn) => {
        btn.addEventListener("click", function () {
          setMode((btn.getAttribute("data-mode") || "general").toLowerCase());
          panel.hidden = true;
        });
      });

      document.addEventListener("click", function (e) {
        const t = e.target;
        if (!(t instanceof Node)) return;
        if (!panel.contains(t) && t !== fab) panel.hidden = true;
      });
    }

    fab.onclick = function () {
      panel.hidden = !panel.hidden;
      updateModePanelState();
      updateModeFabLabel();
    };

    updateModePanelState();
    updateModeFabLabel();
  }

  function mountFooterDisclaimer() {
    let el = document.getElementById("legal-disclaimer-footer");
    if (!el) {
      el = document.createElement("div");
      el.id = "legal-disclaimer-footer";
      el.innerHTML =
        '<div class="star-brand"><span class="brand-star">' + SCALE_ICON + '</span> Star Legal Law Chatbot</div>' +
        '<div class="star-disclaimer">IMPORTANT DISCLAIMER: General legal information only. This is NOT legal advice.</div>';
      document.body.appendChild(el);
    }
  }

  function mountLandingHero() {
    let hero = document.getElementById("star-landing-hero");
    if (!hero) {
      hero = document.createElement("div");
      hero.id = "star-landing-hero";
      hero.innerHTML =
        '<div class="hero-card">' +
          '<div class="hero-title"><span class="hero-star">' + SCALE_ICON + '</span> Star Legal Law Chatbot</div>' +
          '<div class="hero-subtitle">Ask any doubts related to Massachusetts housing.</div>' +
          '<div class="hero-disclaimer">IMPORTANT DISCLAIMER: This chatbot provides general legal information only. It is NOT legal advice.</div>' +
          '<div class="hero-native-suggestions" id="hero-native-suggestions"></div>' +
        "</div>";
      document.body.appendChild(hero);
    }

    // Hide hero after real chat messages appear.
    const hasChatMessages =
      document.querySelectorAll("[data-step-type], [data-testid*='message']").length > 0;
    hero.style.display = hasChatMessages ? "none" : "block";
  }

  function normalizeStarterText(text) {
    return String(text || "")
      .replace(/^💬\s*/u, "")
      .trim();
  }

  function getNativeFollowupButtons(limit = 3) {
    const allButtons = Array.from(document.querySelectorAll("button"));
    const seen = new Set();
    const picks = [];

    allButtons.forEach((btn) => {
      if (picks.length >= limit) return;
      if (btn.closest("#star-landing-hero")) return;

      const raw = (btn.textContent || "").trim();
      if (!raw.startsWith("💬")) return;

      const clean = normalizeStarterText(raw);
      if (!clean || seen.has(clean)) return;

      seen.add(clean);
      picks.push({ text: clean });
    });

    return picks;
  }

  function renderHeroStarterProxies() {
    const slot = document.getElementById("hero-native-suggestions");
    if (!(slot instanceof HTMLElement)) return;

    const nativeStarters = getNativeFollowupButtons(3);
    slot.innerHTML = "";

    const items = nativeStarters.length
      ? nativeStarters
      : DEFAULT_LANDING_QUESTIONS.map((text) => ({ text }));

    items.forEach(({ text }) => {
      const proxy = document.createElement("button");
      proxy.type = "button";
      proxy.className = "hero-native-btn";
      proxy.textContent = "💬 " + text;
      proxy.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        sendAsChatInputWithRetry(text, 10, 180);
      });
      slot.appendChild(proxy);
    });
  }

  function removeChainlitBranding() {
    const isChainlitText = (s) => String(s || "").toLowerCase().includes("chainlit");
    const isChainlitLink = (s) => {
      const v = String(s || "").toLowerCase();
      return v.includes("chainlit") || v.includes("chainlit.io") || v.includes("github.com/chainlit");
    };

    // Remove only explicit Chainlit links/logos (do not remove generic div/span containers).
    Array.from(document.querySelectorAll("a, img")).forEach((el) => {
      if (!(el instanceof HTMLElement)) return;

      const text = (el.textContent || "").trim();
      const href = el.getAttribute("href") || "";
      const src = el.getAttribute("src") || "";
      const alt = el.getAttribute("alt") || "";
      const aria = el.getAttribute("aria-label") || "";

      if (
        isChainlitText(text) ||
        isChainlitLink(href) ||
        isChainlitText(src) ||
        isChainlitText(alt) ||
        isChainlitText(aria)
      ) {
        const footerLike = el.closest("footer");
        if (footerLike) footerLike.remove();
        else if (el.tagName.toLowerCase() === "img" || el.tagName.toLowerCase() === "a") el.remove();
      }
    });

    // Remove footer only if it explicitly contains Chainlit branding.
    Array.from(document.querySelectorAll("footer")).forEach((f) => {
      if (!(f instanceof HTMLElement)) return;
      const txt = (f.textContent || "").trim().toLowerCase();
      if (txt.includes("chainlit")) {
        const hasInputs = f.querySelector("input, textarea, button");
        if (!hasInputs) f.remove();
      }
    });
  }

  function styleSuggestionButtonsAndSources() {
    Array.from(document.querySelectorAll("button")).forEach((btn) => {
      const t = (btn.textContent || "").trim();
      if (t.startsWith("💬")) btn.classList.add("star-suggested-btn");
    });
  }

  function keepFooterPermanentAndClearComposer() {
    const footer = document.getElementById("legal-disclaimer-footer");
    if (!(footer instanceof HTMLElement)) return;

    if (footer.parentElement !== document.body) document.body.appendChild(footer);
    footer.style.display = "block";
    const footerHeight = Math.ceil(footer.getBoundingClientRect().height) || 44;
    const clearance = footerHeight + 18;

    document.body.style.paddingBottom = clearance + "px";
    document.documentElement.style.setProperty("--legal-footer-offset", clearance + "px");

    const input = getActiveComposerInput();
    if (!(input instanceof HTMLElement)) return;

    const form = input.closest("form");
    if (form instanceof HTMLElement) {
      form.style.marginBottom = Math.max(8, footerHeight + 6) + "px";
    }
  }

  function syncModeFromAssistantText() {
    const lines = Array.from(document.querySelectorAll("div, p, span"))
      .map((n) => (n.textContent || "").trim())
      .filter(Boolean)
      .slice(-160);

    for (const line of lines) {
      const m = line.match(/current mode:\s*`?(general|tenant|landlord)`?/i);
      if (m && m[1]) localStorage.setItem(MODE_KEY, m[1].toLowerCase());
    }
    updateModePanelState();
    updateModeFabLabel();
  }

  function boot() {
    removeChainlitBranding();
    mountModeToggle();
    mountLandingHero();
    renderHeroStarterProxies();
    mountFooterDisclaimer();
    styleSuggestionButtonsAndSources();
    keepFooterPermanentAndClearComposer();
    syncModeFromAssistantText();
  }

  boot();
  setInterval(boot, 1200);
  window.addEventListener("resize", keepFooterPermanentAndClearComposer, { passive: true });

  // In case Chainlit re-renders branding after initial mount, remove again.
  const observer = new MutationObserver(() => {
    removeChainlitBranding();
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
