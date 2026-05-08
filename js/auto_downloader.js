/**
 * ComfyUI Auto-Downloader Frontend v2.7
 * Developer: Marbycore
 * Ultra-Aggressive: Sends full workflow data for recursive scanning on the server.
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

        console.log(`[AutoDownloader] Change detected. Sending full workflow for analysis...`);

        // Send the FULL workflow object. Python will scan it recursively.
        const response = await fetch('/auto_downloader/check', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(workflow)
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
        console.log("[AutoDownloader] v2.7 loaded — Developer: Marbycore");
        
        const originalOnConfigure = app.graph.onConfigure;
        app.graph.onConfigure = function() {
            if (originalOnConfigure) originalOnConfigure.apply(this, arguments);
            scheduleCheck();
        };

        scheduleCheck();
    },
    async loadedGraphNode() {
        scheduleCheck();
    }
});
