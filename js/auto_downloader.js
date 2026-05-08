/**
 * ComfyUI Auto-Downloader Frontend v2.3
 * Developer: Marbycore
 * Detects workflow changes reliably on every load, including subsequent loads.
 */

import { app } from "../../scripts/app.js";

const CHECK_DELAY = 2000;   // ms after last node load before triggering
const POLL_INTERVAL = 1000; // ms between graph hash checks

let checkTimeout   = null;
let lastGraphHash  = null;
let pollInterval   = null;

// ── Helpers ──────────────────────────────────────────────────────────────────

function graphHash(workflow) {
    // A lightweight fingerprint: node count + sorted node types joined
    if (!workflow || !workflow.nodes) return "";
    const sig = workflow.nodes.map(n => `${n.id}:${n.type}`).sort().join("|");
    return `${workflow.nodes.length}::${sig}`;
}

async function checkModels() {
    try {
        const graph = app.graph;
        if (!graph) return;

        const workflow = graph.serialize();
        if (!workflow || !workflow.nodes || workflow.nodes.length === 0) return;

        // Build prompt in the format the backend expects
        const prompt = {};
        for (const node of workflow.nodes) {
            if (!node.type || node.type === "Note" || node.type === "MarkdownNote") continue;
            const inputs = {};
            if (node.widgets_values) {
                node.widgets_values.forEach((val, i) => { inputs[`widget_${i}`] = val; });
            }
            prompt[String(node.id)] = { class_type: node.type, inputs };
        }

        console.log(`[AutoDownloader] Checking ${Object.keys(prompt).length} nodes...`);

        const response = await fetch('/auto_downloader/check', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ prompt })
        });

        if (!response.ok) return;
        const result = await response.json();

        if (result.status === 'missing') {
            console.log(`[AutoDownloader] ${result.count} missing models — console opened`);
            showToast(`Auto-Downloader: ${result.count} missing model(s). Check the console window.`, 'warning');
        }
    } catch (err) {
        console.error('[AutoDownloader] Error:', err);
    }
}

function scheduleCheck() {
    if (checkTimeout) clearTimeout(checkTimeout);
    checkTimeout = setTimeout(checkModels, CHECK_DELAY);
}

// ── Graph change polling ──────────────────────────────────────────────────────
// Runs every second and triggers a check whenever the graph fingerprint changes.
// This is the most reliable way to detect any workflow switch.

function startPolling() {
    if (pollInterval) return;
    pollInterval = setInterval(() => {
        try {
            const graph = app.graph;
            if (!graph) return;
            const workflow = graph.serialize();
            const hash = graphHash(workflow);
            if (hash && hash !== lastGraphHash) {
                lastGraphHash = hash;
                scheduleCheck();
            }
        } catch (_) {}
    }, POLL_INTERVAL);
}

// ── Toast notification ────────────────────────────────────────────────────────

function showToast(message, type = 'info') {
    const el = document.createElement('div');
    el.style.cssText = `
        position:fixed; bottom:20px; right:20px; z-index:10000;
        background:${type === 'warning' ? '#f59e0b' : '#3b82f6'};
        color:#fff; padding:12px 20px; border-radius:8px; max-width:420px;
        font-family:sans-serif; font-size:14px;
        box-shadow:0 4px 12px rgba(0,0,0,.3); transition:opacity .3s;
    `;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 7000);
}

// ── Extension registration ────────────────────────────────────────────────────

app.registerExtension({
    name: "ComfyUI.AutoDownloader.Marbycore",

    async setup() {
        console.log("[AutoDownloader] v2.3 loaded — Developer: Marbycore");
        startPolling();   // polling covers ALL workflow changes, even edge cases
    },

    // Belt-and-suspenders: also keep the event-based hooks as backup
    async loadedGraphNode() {
        scheduleCheck();
    },
    async beforeConfigureGraph() {
        scheduleCheck();
    }
});
