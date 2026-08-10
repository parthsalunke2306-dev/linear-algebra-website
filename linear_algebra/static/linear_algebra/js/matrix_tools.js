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

    // Populate Question Statement Box inside solution element
    let questionBox = solutionElement.querySelector('.pdf-question-box');
    if (!questionBox) {
        questionBox = document.createElement('div');
        questionBox.className = 'pdf-question-box';
        solutionElement.insertBefore(questionBox, solutionElement.firstChild);
    }

    const questionTextarea = document.querySelector('textarea[name*="matrix"], textarea[name*="question"], textarea[name*="vectors"]');
    const questionVal = questionTextarea ? questionTextarea.value.trim() : '';
    
    if (questionVal) {
        const valEscaped = questionVal.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        questionBox.innerHTML = `
            <strong style="color: #0f172a; display: block; margin-bottom: 6px; font-size: 13px; text-transform: uppercase;">1. QUESTION / INPUT PROBLEM STATEMENT:</strong>
            <pre style="margin: 0; font-family: monospace; font-size: 14px; color: #1e293b; white-space: pre-wrap; background: #ffffff; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 4px;">${valEscaped}</pre>
        `;
    } else {
        questionBox.innerHTML = `
            <strong style="color: #0f172a; display: block; margin-bottom: 6px; font-size: 13px; text-transform: uppercase;">1. QUESTION / INPUT PROBLEM STATEMENT:</strong>
            <p style="margin: 0; font-style: italic; font-size: 13px; color: #475569;">Problem parameters specified in linear algebra solver input.</p>
        `;
    }

    // Expand all accordion steps for complete derivation export
    const accordions = solutionElement.querySelectorAll('.accordion-collapse');
    accordions.forEach(acc => acc.classList.add('show'));

    // Temporarily activate clean white academic paper mode on-screen for capture
    document.body.classList.add('pdf-export-active');

    // Strip inline dark background styles during capture to guarantee uniform color scheme
    const styledElements = solutionElement.querySelectorAll('*');
    const inlineStyleMap = new Map();
    styledElements.forEach(el => {
        if (el.style.background || el.style.backgroundColor) {
            inlineStyleMap.set(el, {
                bg: el.style.background,
                bgColor: el.style.backgroundColor,
                color: el.style.color
            });
            el.style.background = '#f8fafc';
            el.style.backgroundColor = '#f8fafc';
            el.style.color = '#0f172a';
        }
    });

    const cleanName = (filenamePrefix || topicTitle || 'Solution').replace(/[^a-zA-Z0-9_-]/g, '_');
    const filename = `Solution_${cleanName}_${new Date().toISOString().slice(0,10)}.pdf`;

    const opt = {
        margin:       [10, 10, 10, 10],
        filename:     filename,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff' },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
    };

    const cleanup = () => {
        document.body.classList.remove('pdf-export-active');
        inlineStyleMap.forEach((styleObj, el) => {
            el.style.background = styleObj.bg;
            el.style.backgroundColor = styleObj.bgColor;
            el.style.color = styleObj.color;
        });
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-lg me-1 text-success"></i> PDF Downloaded';
            setTimeout(() => { btn.innerHTML = originalBtnText; }, 3000);
        }
    };


    const runExport = () => {
        if (typeof html2pdf !== 'undefined') {
            html2pdf().set(opt).from(solutionElement).save().then(cleanup).catch(err => {
                console.error("html2pdf failed, falling back to print dialog:", err);
                cleanup();
                window.print();
            });
        } else {
            cleanup();
            window.print();
        }
    };

    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([solutionElement]).then(() => {
            setTimeout(runExport, 200);
        }).catch(runExport);
    } else {
        setTimeout(runExport, 200);
    }
}




