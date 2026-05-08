/**
 * ComfyUI Auto-Downloader Frontend - Developer: Marbycore
 * Versión corregida con lógica ultra-compatible (como la original)
 */

import { app } from "../../scripts/app.js";

const CHECK_DELAY = 1500;
let checkTimeout = null;

async function checkModels() {
    try {
        const graph = app.graph;
        if (!graph) return;

        const workflow = graph.serialize();
        if (!workflow || !workflow.nodes || workflow.nodes.length === 0) return;

        // Formato simple que funcionaba en la versión original
        const prompt = {};
        for (const node of workflow.nodes) {
            if (!node.type || node.type === "Note" || node.type === "MarkdownNote") continue;
            
            const inputs = {};
            if (node.widgets_values && node.widgets_values.length > 0) {
                node.widgets_values.forEach((val, i) => {
                    inputs[`widget_${i}`] = val;
                });
            }
            
            prompt[String(node.id)] = {
                class_type: node.type,
                inputs: inputs
            };
        }

        const response = await fetch('/auto_downloader/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) return;
        const result = await response.json();

        if (result.status === 'missing' && result.count > 0) {
            console.log(`[AutoDownloader] Detectados ${result.count} modelos. Abriendo consola Marbycore...`);
        }
    } catch (err) {
        console.error('[AutoDownloader] Error:', err);
    }
}

app.registerExtension({
    name: "ComfyUI.AutoDownloader.Marbycore",
    async setup() {
        console.log("[AutoDownloader] Frontend initialized - Developer: Marbycore");
    },
    async loadedGraphNode() {
        if (checkTimeout) clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkModels, CHECK_DELAY);
    },
    async beforeConfigureGraph() {
        if (checkTimeout) clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkModels, CHECK_DELAY);
    }
});
