/**
 * ComfyUI Auto-Downloader Frontend v2.5
 * Developer: Marbycore
 * Optimized: Uses native graph events to detect changes with zero resource impact.
 */

import { app } from "../../scripts/app.js";

const CHECK_DELAY = 1000;
let checkTimeout = null;

async function checkModels() {
    try {
        const graph = app.graph;
        if (!graph) return;

        const workflow = graph.serialize();
        if (!workflow || !workflow.nodes || workflow.nodes.length === 0) return;

        const prompt = {};
        for (const node of workflow.nodes) {
            if (!node.type || node.type === "Note" || node.type === "MarkdownNote") continue;
            const inputs = {};
            if (node.widgets_values) {
                node.widgets_values.forEach((val, i) => { inputs[`widget_${i}`] = val; });
            }
            prompt[String(node.id)] = { class_type: node.type, inputs };
        }

        console.log(`[AutoDownloader] Change detected. Checking ${Object.keys(prompt).length} nodes...`);

        const response = await fetch('/auto_downloader/check', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ prompt })
        });

        if (!response.ok) return;
        const result = await response.json();

        if (result.status === 'missing') {
            console.log(`[AutoDownloader] Missing models found! Opening Marbycore Console...`);
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

app.registerExtension({
    name: "ComfyUI.AutoDownloader.Marbycore",
    async setup() {
        console.log("[AutoDownloader] v2.5 loaded — Developer: Marbycore");
        
        // Hook directly into the graph's configuration event
        // This fires every time a workflow is loaded or changed significantly.
        const originalOnConfigure = app.graph.onConfigure;
        app.graph.onConfigure = function() {
            if (originalOnConfigure) originalOnConfigure.apply(this, arguments);
            console.log("[AutoDownloader] Graph configure event detected");
            scheduleCheck();
        };

        // Initial check
        scheduleCheck();
    },
    async loadedGraphNode() {
        // Backup hook for node-by-node loads
        scheduleCheck();
    }
});
