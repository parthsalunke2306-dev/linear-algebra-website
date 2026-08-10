/**
 * Dynamic Matrix Grid & Interactive UI Engine
 * Renders raw textareas into interactive visual 2D HTML matrix input tables
 */

// 1. Light/Dark Theme Switcher
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
});

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeBtnLabel = document.getElementById('themeToggleLabel');
    const themeBtnLabelMobile = document.getElementById('themeToggleLabelMobile');
    const content = theme === 'light' 
        ? '<i class="bi bi-moon-stars-fill me-2 text-info"></i> Dark Mode' 
        : '<i class="bi bi-sun-fill me-2 text-warning"></i> Light Mode';

    if (themeBtnLabel) {
        themeBtnLabel.innerHTML = content;
    }
    if (themeBtnLabelMobile) {
        themeBtnLabelMobile.innerHTML = content;
    }
}

// 2. Clipboard Copy with Toast Feedback
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const toast = document.getElementById('copyToast');
        if (toast) {
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 2500);
        }
    }).catch(err => {
        console.error('Copy failed: ', err);
    });
}

// 3. Tabular Matrix Grid Renderer
function initMatrixGrid(textareaId, gridContainerId, isAugmented = false) {
    const textarea = document.getElementById(textareaId);
    const container = document.getElementById(gridContainerId);
    if (!textarea || !container) return;

    // Hide raw textarea (keep form submission synced)
    textarea.style.display = 'none';

    // Store settings on container dataset
    container.dataset.textareaId = textareaId;
    container.dataset.isAugmented = isAugmented ? 'true' : 'false';

    // Initial render from textarea value
    renderMatrixTable(textareaId, gridContainerId, isAugmented);
}

function renderMatrixTable(textareaId, gridContainerId, isAugmented = false) {
    const textarea = document.getElementById(textareaId);
    const container = document.getElementById(gridContainerId);
    if (!textarea || !container) return;

    let textVal = textarea.value.trim();
    let lines = textVal.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length === 0) {
        lines = ["1 0 0", "0 1 0", "0 0 1"];
        textarea.value = lines.join('\n');
    }

    let matrix = lines.map(line => line.split(/\s+/));
    let rows = matrix.length;
    let cols = matrix[0].length;

    let html = `<div class="table-responsive text-center mb-2">
        <table class="matrix-input-table mx-auto">
            <tbody>`;
    for (let r = 0; r < rows; r++) {
        html += `<tr>`;
        for (let c = 0; c < cols; c++) {
            let isAugCol = isAugmented && (c === cols - 1);
            let cellVal = (matrix[r] && matrix[r][c] !== undefined) ? matrix[r][c] : '0';
            html += `<td class="${isAugCol ? 'augmented-col-cell' : ''}">
                <input type="text" 
                       class="matrix-cell-input form-control font-monospace text-center" 
                       data-row="${r}" 
                       data-col="${c}" 
                       value="${cellVal}" 
                       oninput="syncGridToTextarea('${textareaId}', '${gridContainerId}')">
            </td>`;
        }
        html += `</tr>`;
    }
    html += `</tbody>
        </table>
    </div>`;

    container.innerHTML = html;
}

function syncGridToTextarea(textareaId, gridContainerId) {
    const container = document.getElementById(gridContainerId);
    const textarea = document.getElementById(textareaId);
    if (!container || !textarea) return;

    const rows = container.querySelectorAll('tbody tr');
    let matrixLines = [];
    rows.forEach(tr => {
        let rowVals = [];
        const inputs = tr.querySelectorAll('input.matrix-cell-input');
        inputs.forEach(inp => {
            let val = inp.value.trim();
            rowVals.push(val === '' ? '0' : val);
        });
        matrixLines.push(rowVals.join(' '));
    });

    textarea.value = matrixLines.join('\n');
}

// 4. Dynamic Matrix Resizer with Grid Auto-Sync
function modifyMatrixSize(textareaId, action, gridContainerId = null) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;

    let lines = textarea.value.trim().split('\n').filter(l => l.trim().length > 0);
    if (lines.length === 0) return;

    let matrix = lines.map(line => line.trim().split(/\s+/));
    let rows = matrix.length;
    let cols = matrix[0].length;

    if (action === 'add_row') {
        let newRow = new Array(cols).fill('0');
        matrix.push(newRow);
    } else if (action === 'remove_row' && rows > 1) {
        matrix.pop();
    } else if (action === 'add_col') {
        matrix.forEach(row => row.push('0'));
    } else if (action === 'remove_col' && cols > 1) {
        matrix.forEach(row => row.pop());
    }

    textarea.value = matrix.map(row => row.join(' ')).join('\n');

    // Auto-re-render grid if container provided
    if (gridContainerId) {
        const container = document.getElementById(gridContainerId);
        let isAug = container && container.dataset.isAugmented === 'true';
        renderMatrixTable(textareaId, gridContainerId, isAug);
    }
}

// 5. Toggle All Steps Open / Closed
function toggleAllSteps(accordionId) {
    const accordion = document.getElementById(accordionId);
    if (!accordion) return;

    const collapseElements = accordion.querySelectorAll('.accordion-collapse');
    const buttons = accordion.querySelectorAll('.accordion-button');
    
    let anyExpanded = Array.from(collapseElements).some(el => el.classList.contains('show'));

    collapseElements.forEach(el => {
        if (anyExpanded) {
            el.classList.remove('show');
        } else {
            el.classList.add('show');
        }
    });

    buttons.forEach(btn => {
        if (anyExpanded) {
            btn.classList.add('collapsed');
        } else {
            btn.classList.remove('collapsed');
        }
    });
}

// 6. Professional White-Paper Academic PDF Export Engine
function downloadSolutionPDF(topicTitle, filenamePrefix) {
    const solutionElement = document.getElementById('solutionExportContainer') || 
                            document.querySelector('.glass-card:has(.accordion)') ||
                            document.querySelector('.glass-card:has(.latex-scroll-wrapper)');
    
    if (!solutionElement) {
        alert("No solution content available to export. Please compute a question first.");
        return;
    }

    const btn = (event && event.currentTarget) ? event.currentTarget : document.getElementById('pdfDownloadBtn');
    const originalBtnText = btn ? btn.innerHTML : '';
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-arrow-repeat spin me-1"></i> Generating PDF...';
    }

    // Extract Question / Input Problem Statement
    let questionHTML = "";
    const questionTextarea = document.querySelector('textarea[name*="matrix"], textarea[name*="question"], textarea[name*="vectors"]');
    if (questionTextarea && questionTextarea.value.trim()) {
        const valEscaped = questionTextarea.value.trim().replace(/</g, "&lt;").replace(/>/g, "&gt;");
        questionHTML = `
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; padding: 12px 16px; border-radius: 6px; margin-bottom: 15px;">
                <strong style="color: #0f172a; display: block; margin-bottom: 6px; font-size: 13px;">Input Problem / Given Matrix:</strong>
                <pre style="margin: 0; font-family: monospace; font-size: 14px; color: #1e293b; white-space: pre-wrap;">${valEscaped}</pre>
            </div>`;
    }

    // Create Clean Off-Screen White Academic Document Container
    const pdfDoc = document.createElement('div');
    pdfDoc.id = 'academicPDFDocument';
    pdfDoc.style.cssText = 'position: absolute; left: -9999px; top: 0; width: 750px; background: #ffffff; color: #0f172a; padding: 35px 30px; font-family: "Inter", -apple-system, sans-serif; line-height: 1.5;';

    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    const cleanTopic = topicTitle || 'Linear Algebra Solution';
    
    pdfDoc.innerHTML = `
        <div style="border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <h2 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 20px; letter-spacing: -0.5px;">LINEAR ALGEBRA EXPLORER</h2>
                <h4 style="margin: 4px 0 0 0; color: #475569; font-size: 13px; font-weight: 600;">${cleanTopic} — Official Solution Sheet</h4>
            </div>
            <div style="text-align: right; font-size: 11px; color: #64748b; font-family: monospace;">
                <div><strong>Date:</strong> ${dateStr}</div>
                <div>Academic Solution Document</div>
            </div>
        </div>

        <div style="margin-bottom: 20px;">
            <h3 style="font-size: 14px; color: #0f172a; font-weight: 700; border-left: 4px solid #4f46e5; padding-left: 8px; margin-bottom: 10px; text-transform: uppercase;">1. QUESTION / PROBLEM STATEMENT</h3>
            ${questionHTML || '<p style="color: #64748b; font-style: italic; font-size: 12px;">Problem statement as rendered on solver dashboard.</p>'}
        </div>

        <div>
            <h3 style="font-size: 14px; color: #0f172a; font-weight: 700; border-left: 4px solid #4f46e5; padding-left: 8px; margin-bottom: 15px; text-transform: uppercase;">2. COMPLETE STEP-BY-STEP SOLUTION</h3>
            <div id="pdfSolutionContent"></div>
        </div>

        <div style="margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; font-size: 10px; color: #94a3b8; text-align: center; font-family: monospace;">
            Linear Algebra & Data Science Explorer • Generated Academic Document
        </div>
    `;

    // Clone solution content and clean up UI clutter
    const contentClone = solutionElement.cloneNode(true);
    
    // Remove buttons and UI headers from PDF clone
    contentClone.querySelectorAll('.no-print, button, .pdf-only-header, .matrix-resizer-controls').forEach(el => el.remove());
    
    // Expand all accordion steps
    contentClone.querySelectorAll('.accordion-collapse').forEach(el => {
        el.classList.add('show');
        el.style.display = 'block';
        el.style.visibility = 'visible';
    });

    // Apply crisp white-paper styles to all cloned elements
    contentClone.querySelectorAll('*').forEach(el => {
        el.style.backgroundColor = 'transparent';
        el.style.color = '#0f172a';
        el.style.boxShadow = 'none';

        if (el.classList.contains('glass-card') || el.classList.contains('accordion-item')) {
            el.style.border = '1px solid #cbd5e1';
            el.style.marginBottom = '12px';
            el.style.borderRadius = '6px';
            el.style.padding = '12px 16px';
            el.style.background = '#ffffff';
        }
        if (el.classList.contains('bg-dark') || el.classList.contains('table-dark') || el.classList.contains('accordion-body')) {
            el.style.background = '#f8fafc';
            el.style.border = '1px solid #e2e8f0';
            el.style.borderRadius = '4px';
        }
        if (el.classList.contains('latex-scroll-wrapper')) {
            el.style.overflow = 'visible';
            el.style.whiteSpace = 'normal';
            el.style.fontSize = '14px';
        }
    });

    pdfDoc.querySelector('#pdfSolutionContent').appendChild(contentClone);
    document.body.appendChild(pdfDoc);

    const cleanName = (filenamePrefix || topicTitle || 'Solution').replace(/[^a-zA-Z0-9_-]/g, '_');
    const filename = `Solution_${cleanName}_${new Date().toISOString().slice(0,10)}.pdf`;

    const opt = {
        margin:       [10, 10, 10, 10],
        filename:     filename,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
    };

    const runPDFExport = () => {
        if (typeof html2pdf !== 'undefined') {
            html2pdf().set(opt).from(pdfDoc).save().then(() => {
                if (pdfDoc.parentNode) pdfDoc.parentNode.removeChild(pdfDoc);
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="bi bi-check-lg me-1 text-success"></i> PDF Downloaded';
                    setTimeout(() => { btn.innerHTML = originalBtnText; }, 3000);
                }
            }).catch(err => {
                console.error("PDF generation failed:", err);
                if (pdfDoc.parentNode) pdfDoc.parentNode.removeChild(pdfDoc);
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = originalBtnText;
                }
                alert("Opening print dialog for PDF export...");
                window.print();
            });
        } else {
            if (pdfDoc.parentNode) pdfDoc.parentNode.removeChild(pdfDoc);
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalBtnText;
            }
            alert("Opening print dialog for PDF export...");
            window.print();
        }
    };

    // Ensure MathJax renders formulas cleanly in temporary document before taking vector snapshot
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([pdfDoc]).then(runPDFExport).catch(runPDFExport);
    } else {
        runPDFExport();
    }
}



