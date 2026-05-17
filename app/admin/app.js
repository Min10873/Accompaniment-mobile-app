const serviceStatus = document.querySelector("#service-status");
const storageStatus = document.querySelector("#storage-status");
const taskCounts = document.querySelector("#task-counts");
const tasksBody = document.querySelector("#tasks-body");
const updatedAt = document.querySelector("#updated-at");
const refreshButton = document.querySelector("#refresh-button");
const appVersion = document.querySelector("#app-version");

refreshButton.addEventListener("click", loadAdmin);
loadAdmin();

async function loadAdmin() {
  refreshButton.disabled = true;
  try {
    const response = await fetch("/api/admin/status");
    const data = await response.json();
    renderStatus(data);
    updatedAt.textContent = `刷新时间：${new Date().toLocaleString()}`;
  } catch (error) {
    updatedAt.textContent = "刷新失败";
  } finally {
    refreshButton.disabled = false;
  }
}

function renderStatus(data) {
  appVersion.textContent = `版本 ${data.backend.version || "未知"}`;
  serviceStatus.innerHTML = renderDefinitionList([
    ["backend", data.backend.status],
    ["version", data.backend.version || "未知"],
    ["processing", data.backend.processing_mode],
    ["sidecar", data.sidecar.status],
  ]);

  storageStatus.innerHTML = renderDefinitionList([
    ["data", "仅显示容量和文件数量"],
    ["free", formatBytes(data.storage.data_free_bytes)],
    ["audio", `${data.storage.audio_count} 个文件`],
    ["tasks", `${data.storage.tasks_count} 个文件`],
    ["videos", `${data.storage.videos_count} 个文件`],
  ]);

  taskCounts.innerHTML = Object.entries(data.tasks.counts)
    .map(([status, count]) => `<span class="chip">${escapeHtml(status)}: ${count}</span>`)
    .join("") || '<span class="muted">暂无任务</span>';

  tasksBody.innerHTML = data.tasks.recent.map(renderTaskRow).join("") ||
    '<tr><td colspan="7" class="empty">暂无任务</td></tr>';
}

function renderTaskRow(task) {
  const audio = task.audio_url
    ? `<a href="${escapeAttribute(task.audio_url)}" target="_blank" rel="noreferrer">打开</a>`
    : "";
  return `
    <tr>
      <td><code>${escapeHtml(task.task_id)}</code></td>
      <td><span class="status ${escapeAttribute(task.status)}">${escapeHtml(task.status)}</span></td>
      <td>${escapeHtml(task.created_at)}</td>
      <td>${escapeHtml(task.updated_at)}</td>
      <td>${escapeHtml(task.error_code || "")}</td>
      <td>${escapeHtml(task.share_text_preview || "")}</td>
      <td>${audio}</td>
    </tr>
  `;
}

function renderDefinitionList(rows) {
  return rows.map(([key, value]) => `
    <dt>${escapeHtml(key)}</dt>
    <dd>${escapeHtml(value)}</dd>
  `).join("");
}

function formatBytes(value) {
  if (value > 1024 * 1024 * 1024) {
    return `${(value / 1024 / 1024 / 1024).toFixed(1)} GB`;
  }
  if (value > 1024 * 1024) {
    return `${(value / 1024 / 1024).toFixed(1)} MB`;
  }
  return `${Math.round(value / 1024)} KB`;
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
