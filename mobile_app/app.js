(function () {
  const app = document.getElementById("app");

  if (!app) {
    return;
  }

  const config = window.__MOBILE_CONFIG__ || {};

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function renderLinks(text, links) {
    if (Array.isArray(links) && links.length > 0) {
      return links
        .map(
          (link) =>
            `<a class="source-pill" href="${escapeHtml(link.url)}" target="_blank" rel="noreferrer">${escapeHtml(link.label)}</a>`
        )
        .join("");
    }
    return escapeHtml(text);
  }

  function renderItem(item) {
    const className =
      item.label === "一句话判断"
        ? "row verdict"
        : item.label === "来源"
          ? "row sources"
          : "row";
    const content =
      item.label === "来源"
        ? renderLinks(item.text, item.links)
        : escapeHtml(item.text).replaceAll("；", "；<br>");
    return `
      <div class="${className}">
        <div class="row-label">${escapeHtml(item.label)}</div>
        <div class="row-content">${content}</div>
      </div>
    `;
  }

  function renderStory(story) {
    const notes = (story.notes || [])
      .map((note) => `<div class="note">${escapeHtml(note)}</div>`)
      .join("");
    const items = (story.items || []).map(renderItem).join("");
    return `
      <article class="story">
        <h3>${escapeHtml(story.title)}</h3>
        ${notes}
        ${items}
      </article>
    `;
  }

  function renderSection(section, index) {
    const notes = (section.notes || [])
      .map((note) => `<div class="note">${escapeHtml(note)}</div>`)
      .join("");
    const stories = (section.stories || []).map(renderStory).join("");
    return `
      <section class="section">
        <div class="section-title">
          <div>
            <p class="section-kicker">Section ${String(index + 1).padStart(2, "0")}</p>
            <h2>${escapeHtml(section.title)}</h2>
          </div>
          <span class="section-index">${String(index + 1).padStart(2, "0")}</span>
        </div>
        ${notes}
        <div class="story-list">${stories}</div>
      </section>
    `;
  }

  function renderApp(digest, sourceLabel) {
    const top3 = (digest.top3 || [])
      .map(
        (item, index) => `
          <li class="top-item">
            <div class="top-rank">${index + 1}</div>
            <div>${escapeHtml(item)}</div>
          </li>
        `
      )
      .join("");

    const sections = (digest.sections || [])
      .filter((section) => !["今日总览", "今日 Top 3", "收尾总结"].includes(section.title))
      .map(renderSection)
      .join("");

    app.innerHTML = `
      <main class="shell">
        <section class="hero">
          <p class="eyebrow">News Assistant Mobile</p>
          <h1>${escapeHtml(digest.title)}</h1>
          <p class="greeting">${escapeHtml(digest.greeting || "")}</p>
          <div class="hero-grid">
            <div class="chip">安卓 / 鸿蒙 4 适配的移动阅读版</div>
            <div class="chip">更强调分析层次，弱化源报道立场口吻</div>
            <div class="chip">当前数据源：${escapeHtml(sourceLabel)}</div>
          </div>
        </section>

        <section class="overview">
          <div class="section-title">
            <div>
              <p class="section-kicker">Overview</p>
              <h2>今日总览</h2>
            </div>
          </div>
          <p>${escapeHtml(digest.overview || "")}</p>
        </section>

        <section class="top3">
          <div class="section-title">
            <div>
              <p class="section-kicker">Priority</p>
              <h2>今日 Top 3</h2>
            </div>
          </div>
          <ol class="top-list">${top3}</ol>
        </section>

        ${sections}

        <section class="closing">
          <div class="section-title">
            <div>
              <p class="section-kicker">Closing</p>
              <h2>收尾总结</h2>
            </div>
          </div>
          <p>${escapeHtml(digest.closing || "")}</p>
        </section>

        <div class="footer-space"></div>
      </main>
    `;
  }

  async function fetchRemoteDigest() {
    const url = String(config.remoteDigestJsonUrl || "").trim();
    if (!url) {
      return null;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000);
    try {
      const response = await fetch(`${url}${url.includes("?") ? "&" : "?"}t=${Date.now()}`, {
        cache: "no-store",
        signal: controller.signal
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } finally {
      clearTimeout(timer);
    }
  }

  async function init() {
    let digest = null;
    let sourceLabel = "内置离线内容";
    try {
      digest = await fetchRemoteDigest();
      if (digest) {
        sourceLabel = "远程同步内容";
      }
    } catch (_error) {
    }
    if (!digest) {
      digest = window.__DIGEST__;
    }
    if (!digest) {
      app.innerHTML = `<main class="shell"><section class="hero"><p class="eyebrow">News Assistant Mobile</p><h1>暂无可用内容</h1><p class="greeting">请先生成一份日报或配置远程同步地址。</p></section></main>`;
      return;
    }
    renderApp(digest, sourceLabel);
  }

  init();

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("./service-worker.js").catch(() => {});
    });
  }
})();
