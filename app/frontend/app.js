const form = document.querySelector("#task-form");
const uploadForm = document.querySelector("#upload-form");
const homePage = document.querySelector("#home-page");
const taskPage = document.querySelector("#task-page");
const douyinTab = document.querySelector("#tab-douyin");
const uploadTab = document.querySelector("#tab-upload");
const textarea = document.querySelector("#share-text");
const audioFile = document.querySelector("#audio-file");
const pasteButton = document.querySelector("#paste-button");
const pasteHint = document.querySelector("#paste-hint");
const submitButton = document.querySelector("#submit-button");
const uploadButton = document.querySelector("#upload-button");
const result = document.querySelector("#result");
const appVersion = document.querySelector("#app-version");
const homeButton = document.querySelector("#home-button");
const LAST_TASK_KEY = "accompaniment:lastTaskId";
const RETENTION_DAYS = 7;

let pollTimer = null;
let pitchPollTimer = null;
let currentTaskData = null;
let currentVariantKey = "original";
let pitchBusy = false;
let resultTab = "play";

homeButton.addEventListener("click", resetToHome);
douyinTab.addEventListener("click", () => setHomeTab("douyin"));
uploadTab.addEventListener("click", () => setHomeTab("upload"));

pasteButton.addEventListener("click", async () => {
  if (!navigator.clipboard || typeof navigator.clipboard.readText !== "function") {
    focusForManualPaste();
    return;
  }

  try {
    const text = await navigator.clipboard.readText();
    if (!text.trim()) {
      focusForManualPaste("剪贴板里没有内容，请先在抖音复制链接。");
      return;
    }
    textarea.value = text;
    textarea.focus();
    pasteHint.textContent = "已粘贴，可以点“开始处理”。";
  } catch (error) {
    focusForManualPaste();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearTimeout(pitchPollTimer);
  currentTaskData = null;
  currentVariantKey = "original";
  pitchBusy = false;
  resultTab = "play";
  const shareText = textarea.value.trim();
  if (!shareText) {
    showError("请先粘贴抖音分享文本");
    return;
  }

  setBusy(true);
  showNotice("正在提交", "已经收到分享文本，正在开始处理。");

  try {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        share_text: shareText,
      }),
    });
    const data = await response.json();

    if (!response.ok) {
      setBusy(false);
      showError(data.message || "这次没有提交成功，请稍后再试");
      return;
    }

    rememberTask(data.task_id);
    showProcessing(data.task_id, data.message || "正在处理，请稍等");
    pollTask(data.task_id);
  } catch (error) {
    setBusy(false);
    showError("无法连接服务，请稍后再试");
  }
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearTimeout(pollTimer);
  clearTimeout(pitchPollTimer);
  currentTaskData = null;
  currentVariantKey = "original";
  pitchBusy = false;
  resultTab = "play";

  const file = audioFile.files && audioFile.files[0];
  if (!file) {
    showError("请先选择一个音频文件");
    return;
  }

  setBusy(true);
  showNotice("正在上传", "正在把音频上传到处理中心。");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/uploads", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok) {
      setBusy(false);
      showError(data.message || "这次没有上传成功，请换一个音频试试");
      return;
    }

    setBusy(false);
    rememberTask(data.task_id);
    showSuccess(data);
  } catch (error) {
    setBusy(false);
    showError("无法连接服务，请稍后再试");
  }
});

loadVersion();
restoreLastTask();

async function loadVersion() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    if (response.ok && data.version) {
      appVersion.textContent = `版本 ${data.version}`;
    }
  } catch (error) {
    appVersion.textContent = "版本未知";
  }
}

function restoreLastTask() {
  const taskId = taskIdFromUrl() || localStorage.getItem(LAST_TASK_KEY);
  if (!taskId) {
    return;
  }
  rememberTask(taskId);
  setBusy(true);
  showProcessing(taskId, "正在恢复上次任务，请稍等");
  fetchTask(taskId);
}

function taskIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const taskId = params.get("task");
  return taskId && /^[A-Z0-9]{8,10}$/.test(taskId) ? taskId : "";
}

function rememberTask(taskId) {
  if (!taskId) {
    return;
  }
  localStorage.setItem(LAST_TASK_KEY, taskId);
  const url = new URL(window.location.href);
  url.searchParams.set("task", taskId);
  window.history.replaceState({}, "", url);
}

function resetToHome() {
  clearTimeout(pollTimer);
  clearTimeout(pitchPollTimer);
  currentTaskData = null;
  currentVariantKey = "original";
  pitchBusy = false;
  localStorage.removeItem(LAST_TASK_KEY);
  const url = new URL(window.location.href);
  url.searchParams.delete("task");
  window.history.replaceState({}, "", url);
  textarea.value = "";
  audioFile.value = "";
  pasteHint.textContent = "从抖音复制后，回到这里点“粘贴链接”。如果按钮没反应，就长按输入框选择粘贴。";
  homeButton.hidden = true;
  homePage.hidden = false;
  taskPage.hidden = true;
  setHomeTab("douyin");
  setBusy(false);
  result.className = "result";
  result.innerHTML = "";
  textarea.focus();
}

function pollTask(taskId) {
  clearTimeout(pollTimer);
  pollTimer = setTimeout(async () => {
    fetchTask(taskId);
  }, 1800);
}

function pollPitch(taskId, pitchJobId) {
  clearTimeout(pitchPollTimer);
  pitchPollTimer = setTimeout(async () => {
    fetchPitchJob(taskId, pitchJobId);
  }, 1800);
}

async function fetchTask(taskId) {
  try {
    const response = await fetch(`/api/tasks/${encodeURIComponent(taskId)}`);
    const data = await response.json();
    if (!response.ok) {
      setBusy(false);
      showError(data.message || "没有找到这次任务", taskId);
      return;
    }

    if (data.status === "done") {
      setBusy(false);
      rememberTask(taskId);
      showSuccess(data);
      return;
    }
    if (data.status === "failed" || data.status === "expired") {
      setBusy(false);
      rememberTask(taskId);
      showError(data.message || "这次没有处理成功，请换一个视频试试", taskId);
      return;
    }

    setBusy(true);
    showProcessing(taskId, data.message || "正在处理，请稍等");
    pollTask(taskId);
  } catch (error) {
    setBusy(false);
    showError("查询任务失败，请稍后再试", taskId);
  }
}

function setBusy(isBusy) {
  submitButton.disabled = isBusy;
  pasteButton.disabled = isBusy;
  uploadButton.disabled = isBusy;
  audioFile.disabled = isBusy;
  textarea.readOnly = isBusy;
  submitButton.textContent = isBusy ? "处理中..." : "开始处理";
  uploadButton.textContent = isBusy ? "处理中..." : "上传音频";
}

function focusForManualPaste(message = "请长按输入框，然后选择粘贴。") {
  pasteHint.textContent = message;
  textarea.focus();
}

function showNotice(title, message) {
  showTaskPage();
  homeButton.hidden = false;
  result.className = "result notice";
  result.innerHTML = `
    <h2>${escapeHtml(title)}</h2>
    <p>${escapeHtml(message)}</p>
  `;
}

function showProcessing(taskId, message) {
  showTaskPage();
  homeButton.hidden = false;
  result.className = "result notice";
  result.innerHTML = `
    <h2>正在处理</h2>
    <p>${escapeHtml(message)}</p>
    <p class="task-id">任务号：${escapeHtml(taskId)}</p>
  `;
}

function showSuccess(data) {
  currentTaskData = normalizeTaskData(data);
  currentVariantKey = "original";
  pitchBusy = false;
  resultTab = "play";
  renderSuccess();
}

function renderSuccess(pitchMessage = "", isPitchBusy = pitchBusy) {
  showTaskPage();
  homeButton.hidden = false;
  pitchBusy = isPitchBusy;
  const currentVariant = currentTaskData.audio_variants[currentVariantKey];
  const audioUrl = currentVariant.audio_url;
  const fullUrl = new URL(audioUrl, window.location.href).href;
  const validUntil = formatValidUntil(currentVariant.expires_at || currentTaskData.expires_at, currentVariant.created_at);
  const variants = Object.entries(currentTaskData.audio_variants);
  const variantButtons = variants.length > 1
    ? `<div class="variant-bar" aria-label="音频版本">
        ${variants
          .map(([key, variant]) => {
            const isActive = key === currentVariantKey;
            return `<button class="variant-button${isActive ? " active" : ""}" type="button" data-variant-key="${escapeAttribute(key)}" ${isActive ? "disabled" : ""}>${escapeHtml(variant.label || labelForVariant(key, variant))}</button>`;
          })
          .join("")}
      </div>`
    : "";
  const playPanelHidden = resultTab === "play" ? "" : " hidden";
  const pitchPanelHidden = resultTab === "pitch" ? "" : " hidden";
  result.className = "result notice success";
  result.innerHTML = `
    <h2>处理好了</h2>
    <div class="tab-bar result-tabs" role="tablist" aria-label="结果功能">
      <button id="result-tab-play" class="tab-button${resultTab === "play" ? " active" : ""}" type="button" role="tab" aria-selected="${resultTab === "play"}" aria-controls="play-panel">播放保存</button>
      <button id="result-tab-pitch" class="tab-button${resultTab === "pitch" ? " active" : ""}" type="button" role="tab" aria-selected="${resultTab === "pitch"}" aria-controls="pitch-panel">变调处理</button>
    </div>

    <section id="play-panel" class="result-panel"${playPanelHidden} role="tabpanel" aria-labelledby="result-tab-play">
      <section class="current-version">
        <div>
          <p class="section-label">当前版本</p>
          <p class="current-version-name">${escapeHtml(currentVariant.label || labelForVariant(currentVariantKey, currentVariant))}</p>
        </div>
        ${variantButtons}
      </section>
      <div class="player">
        <audio controls src="${escapeAttribute(audioUrl)}"></audio>
      </div>
      <div class="result-actions">
        <a class="button-link primary" href="${escapeAttribute(audioUrl)}" download>下载音频</a>
        <button class="secondary" type="button" id="copy-link">复制链接</button>
      </div>
      <p class="small-note">当前音频链接有效到 ${escapeHtml(validUntil)}。</p>
    </section>

    <form id="pitch-panel" class="pitch-panel result-panel"${pitchPanelHidden} role="tabpanel" aria-labelledby="result-tab-pitch">
      <h3>变调处理</h3>
      <p class="small-note">当前基准：${escapeHtml(currentVariant.label || labelForVariant(currentVariantKey, currentVariant))}</p>
      <div class="pitch-row" role="group" aria-label="升降调">
        <label class="choice"><input type="radio" name="pitch-direction" value="up" checked />升高</label>
        <label class="choice"><input type="radio" name="pitch-direction" value="down" />降低</label>
      </div>
      <div class="pitch-select-heading">
        <label class="pitch-select-label" for="pitch-semitones">半音</label>
        <span>1 = 半音，2 = 全音</span>
      </div>
      <select id="pitch-semitones" name="pitch-semitones">
        ${Array.from({ length: 5 }, (_, index) => {
          const value = index + 1;
          return `<option value="${value}">${value}</option>`;
        }).join("")}
      </select>
      <button class="primary" type="submit" ${isPitchBusy ? "disabled" : ""}>生成这个版本</button>
      <button class="secondary" type="button" id="use-original" ${currentVariantKey === "original" ? "disabled" : ""}>切回原调</button>
      ${pitchMessage ? `<p class="pitch-status">${escapeHtml(pitchMessage)}</p>` : ""}
    </form>
    <p class="task-id">任务号：${escapeHtml(currentTaskData.task_id)}</p>
  `;

  document.querySelector("#result-tab-play").addEventListener("click", () => {
    resultTab = "play";
    renderSuccess(pitchMessage, pitchBusy);
  });
  document.querySelector("#result-tab-pitch").addEventListener("click", () => {
    resultTab = "pitch";
    renderSuccess(pitchMessage, pitchBusy);
  });

  document.querySelectorAll("[data-variant-key]").forEach((button) => {
    button.addEventListener("click", () => {
      currentVariantKey = button.dataset.variantKey;
      renderSuccess();
    });
  });

  document.querySelector("#use-original").addEventListener("click", () => {
    currentVariantKey = "original";
    renderSuccess();
  });

  document.querySelector("#pitch-panel").addEventListener("submit", submitPitch);

  const copyButton = document.querySelector("#copy-link");
  if (copyButton) {
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(fullUrl);
        copyButton.textContent = "已复制";
      } catch (error) {
        copyButton.textContent = "复制失败";
      }
    });
  }
}

async function submitPitch(event) {
  event.preventDefault();
  if (!currentTaskData) {
    return;
  }

  const formData = new FormData(event.currentTarget);
  const direction = formData.get("pitch-direction");
  const semitones = Number(formData.get("pitch-semitones"));
  pitchBusy = true;
  resultTab = "pitch";
  renderSuccess("正在提交变调请求", true);

  try {
    const response = await fetch(`/api/tasks/${encodeURIComponent(currentTaskData.task_id)}/pitch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ direction, semitones }),
    });
    const data = await response.json();
    if (data.cached && data.audio_url && data.variant_key) {
      addVariantFromPitch(data, direction, semitones);
      currentVariantKey = data.variant_key;
      pitchBusy = false;
      resultTab = "play";
      renderSuccess(data.message || "这个版本已经生成过，可以直接播放");
      return;
    }
    if (response.status === 202 && data.pitch_job_id) {
      resultTab = "pitch";
      renderSuccess(data.message || "正在调整音高", true);
      pollPitch(currentTaskData.task_id, data.pitch_job_id);
      return;
    }
    pitchBusy = false;
    renderSuccess(data.message || "这次变调没有成功，原调还可以继续播放");
  } catch (error) {
    pitchBusy = false;
    renderSuccess("无法连接服务，原调还可以继续播放");
  }
}

async function fetchPitchJob(taskId, pitchJobId) {
  try {
    const response = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/pitch/${encodeURIComponent(pitchJobId)}`);
    const data = await response.json();
    if (!response.ok) {
      pitchBusy = false;
      renderSuccess(data.message || "这次变调没有成功，原调还可以继续播放");
      return;
    }
    if (data.status === "done" && data.audio_url && data.variant_key) {
      addVariantFromPitch(data);
      currentVariantKey = data.variant_key;
      pitchBusy = false;
      resultTab = "play";
      renderSuccess(data.message || "变调好了，可以播放");
      return;
    }
    if (data.status === "failed") {
      pitchBusy = false;
      renderSuccess(data.message || "这次变调没有成功，原调还可以继续播放");
      return;
    }
    renderSuccess(data.message || "正在调整音高", true);
    pollPitch(taskId, pitchJobId);
  } catch (error) {
    pitchBusy = false;
    renderSuccess("查询变调任务失败，原调还可以继续播放");
  }
}

function normalizeTaskData(data) {
  const variants = { ...(data.audio_variants || {}) };
  if (!variants.original) {
    variants.original = {
      kind: "original",
      audio_url: data.audio_url,
      expires_at: data.expires_at,
      label: "原调",
    };
  }
  return {
    ...data,
    audio_variants: variants,
  };
}

function addVariantFromPitch(data, direction = null, semitones = null) {
  if (!currentTaskData || !data.variant_key || !data.audio_url) {
    return;
  }
  currentTaskData.audio_variants[data.variant_key] = {
    kind: "pitch",
    audio_url: data.audio_url,
    direction,
    semitones,
    expires_at: data.expires_at || currentTaskData.expires_at,
    label: labelForVariant(data.variant_key, { direction, semitones }),
  };
}

function labelForVariant(key, variant = {}) {
  if (key === "original") {
    return "原调";
  }
  const [directionFromKey, semitonesFromKey] = key.split("_");
  const direction = variant.direction || directionFromKey;
  const semitones = variant.semitones || semitonesFromKey;
  const directionLabel = direction === "down" ? "降低" : "升高";
  return `${directionLabel} ${semitones}`;
}

function showError(message, taskId = "") {
  showTaskPage();
  homeButton.hidden = false;
  result.className = "result notice danger";
  result.innerHTML = `
    <h2>没有处理成功</h2>
    <p>${escapeHtml(message)}</p>
    ${taskId ? `<p class="task-id">任务号：${escapeHtml(taskId)}</p>` : ""}
  `;
}

function showTaskPage() {
  homePage.hidden = true;
  taskPage.hidden = false;
}

function setHomeTab(tabName) {
  const isUpload = tabName === "upload";
  uploadTab.classList.toggle("active", isUpload);
  uploadTab.setAttribute("aria-selected", String(isUpload));
  douyinTab.classList.toggle("active", !isUpload);
  douyinTab.setAttribute("aria-selected", String(!isUpload));
  uploadForm.hidden = !isUpload;
  form.hidden = isUpload;
  if (isUpload) {
    audioFile.focus();
  } else {
    textarea.focus();
  }
}

function formatValidUntil(expiresAt, createdAt) {
  const explicitDate = expiresAt ? new Date(expiresAt) : null;
  if (explicitDate && !Number.isNaN(explicitDate.getTime())) {
    return formatDate(explicitDate);
  }

  const date = createdAt ? new Date(createdAt) : new Date();
  if (Number.isNaN(date.getTime())) {
    return "生成后 7 天";
  }
  date.setDate(date.getDate() + RETENTION_DAYS);
  return formatDate(date);
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}.${month}.${day}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}
