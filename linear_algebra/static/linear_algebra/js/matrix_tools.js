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
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise();
    }
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

// 3. Tabular Matrix Grid Renderer & Interactive UI Engine
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

    let html = `<div class="matrix-grid-wrapper table-responsive text-center my-3">
        <div class="matrix-bracket-container d-inline-flex align-items-center justify-content-center">
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
                       autocomplete="off"
                       spellcheck="false"
                       oninput="syncGridToTextarea('${textareaId}', '${gridContainerId}')"
                       onkeydown="handleMatrixKeyNav(event, this, '${gridContainerId}')"
                       onpaste="handleMatrixPaste(event, this, '${textareaId}', '${gridContainerId}')">
            </td>`;
        }
        html += `</tr>`;
    }
    html += `</tbody>
            </table>
        </div>
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

// Keyboard Arrow Navigation (Up, Down, Left, Right, Enter)
function handleMatrixKeyNav(e, input, gridContainerId) {
    const row = parseInt(input.dataset.row, 10);
    const col = parseInt(input.dataset.col, 10);
    const container = document.getElementById(gridContainerId);
    if (!container) return;

    let targetRow = row;
    let targetCol = col;

    if (e.key === 'ArrowUp') {
        targetRow = row - 1;
        e.preventDefault();
    } else if (e.key === 'ArrowDown' || e.key === 'Enter') {
        targetRow = row + 1;
        e.preventDefault();
    } else if (e.key === 'ArrowLeft' && input.selectionStart === 0 && input.selectionEnd === 0) {
        targetCol = col - 1;
        e.preventDefault();
    } else if (e.key === 'ArrowRight' && input.selectionStart === input.value.length) {
        targetCol = col + 1;
        e.preventDefault();
    } else {
        return;
    }

    const nextInput = container.querySelector(`input.matrix-cell-input[data-row="${targetRow}"][data-col="${targetCol}"]`);
    if (nextInput) {
        nextInput.focus();
        nextInput.select();
    }
}

// Matrix Paste Support (Paste tab/space separated rows into matrix cells)
function handleMatrixPaste(e, startInput, textareaId, gridContainerId) {
    const pasteData = (e.clipboardData || window.clipboardData).getData('text');
    if (!pasteData || (!pasteData.includes('\n') && !pasteData.includes('\t') && !pasteData.includes(' '))) {
        return; // normal single-value paste
    }

    e.preventDefault();
    const rows = pasteData.trim().split('\n').map(r => r.trim().split(/[\t\s,]+/));
    if (rows.length === 0) return;

    const textarea = document.getElementById(textareaId);
    if (!textarea) return;

    // Build current matrix
    let currentMatrix = textarea.value.trim().split('\n').map(l => l.trim().split(/\s+/));
    const startRow = parseInt(startInput.dataset.row, 10) || 0;
    const startCol = parseInt(startInput.dataset.col, 10) || 0;

    // Expand matrix size if paste exceeds current bounds
    while (currentMatrix.length < startRow + rows.length) {
        let cols = currentMatrix[0] ? currentMatrix[0].length : rows[0].length;
        currentMatrix.push(new Array(cols).fill('0'));
    }

    for (let r = 0; r < rows.length; r++) {
        let curR = startRow + r;
        while (currentMatrix[curR].length < startCol + rows[r].length) {
            currentMatrix[curR].push('0');
        }
        for (let c = 0; c < rows[r].length; c++) {
            let curC = startCol + c;
            currentMatrix[curR][curC] = rows[r][c];
        }
    }

    textarea.value = currentMatrix.map(row => row.join(' ')).join('\n');
    const container = document.getElementById(gridContainerId);
    let isAug = container && container.dataset.isAugmented === 'true';
    renderMatrixTable(textareaId, gridContainerId, isAug);
}

// 4. Dynamic Matrix Resizer with Grid Auto-Sync
function modifyMatrixSize(textareaId, action, gridContainerId = null) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;

    let lines = textarea.value.trim().split('\n').filter(l => l.trim().length > 0);
    if (lines.length === 0) {
        lines = ["1 0 0", "0 1 0", "0 0 1"];
    }

    let matrix = lines.map(line => line.trim().split(/\s+/));
    let rows = matrix.length;
    let cols = matrix[0] ? matrix[0].length : 1;

    if (action === 'add_row') {
        let newRow = new Array(cols).fill('0');
        matrix.push(newRow);
    } else if (action === 'remove_row' && rows > 1) {
        matrix.pop();
    } else if (action === 'add_col') {
        matrix.forEach(row => row.push('0'));
    } else if (action === 'remove_col' && cols > 1) {
        matrix.forEach(row => row.pop());
    } else if (action === 'add_size') {
        let newRow = new Array(cols + 1).fill('0');
        matrix.forEach(row => row.push('0'));
        matrix.push(newRow);
    } else if (action === 'remove_size' && rows > 1 && cols > 1) {
        matrix.pop();
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

// 6. Universal Export to Microsoft Word (.doc / .docx compatible) with Math & Question Support
function latexToWordHTML(latex) {
    if (!latex) return '';
    let str = String(latex).trim();

    // Clean outer dollar signs or math delimiters
    str = str.replace(/^\$\$+|\$\$+$/g, '').trim();

    // Helper: Convert LaTeX Matrix / Array to HTML Table
    function convertMatrix(match, align, body) {
        const rows = body.trim().split(/\\\\|\n/).map(r => r.trim()).filter(r => r.length > 0);
        if (rows.length === 0) return '';

        const hasBar = align && align.includes('|');
        const barIndex = hasBar ? align.indexOf('|') - 1 : -1;

        let tableRows = '';
        rows.forEach(rowStr => {
            const cells = rowStr.split('&').map(c => c.trim());
            let rowHtml = '<tr>';
            cells.forEach((cell, idx) => {
                const isAug = hasBar && (idx > barIndex);
                const borderLeft = isAug ? 'border-left: 1.5pt dashed #64748b;' : '';
                rowHtml += `<td style="padding: 4pt 10pt; text-align: center; border: none; font-size: 11pt; font-weight: 500; ${borderLeft}">${cleanMathSymbols(cell)}</td>`;
            });
            rowHtml += '</tr>';
            tableRows += rowHtml;
        });

        return `<table style="display: inline-table; vertical-align: middle; border-left: 2.5pt solid #0f172a; border-right: 2.5pt solid #0f172a; border-collapse: collapse; margin: 6pt 12pt; background-color: #f8fafc;"><tbody>${tableRows}</tbody></table>`;
    }

    // Helper: Clean math symbols to Unicode
    function cleanMathSymbols(text) {
        if (!text) return '';
        let s = String(text);
        s = s.replace(/\\mathbf\{([^}]+)\}/g, '<b>$1</b>');
        s = s.replace(/\\boldsymbol\{([^}]+)\}/g, '<b>$1</b>');
        s = s.replace(/\\text\{([^}]+)\}/g, '$1');
        s = s.replace(/\\operatorname\{([^}]+)\}/g, '$1');
        s = s.replace(/\\pmod\{([^}]+)\}/g, ' (mod $1)');
        s = s.replace(/\\sqrt\{([^}]+)\}/g, '√($1)');
        s = s.replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '($1)/($2)');
        s = s.replace(/\\cdot/g, ' · ');
        s = s.replace(/\\times/g, ' × ');
        s = s.replace(/\\oplus/g, ' ⊕ ');
        s = s.replace(/\\odot/g, ' ⊙ ');
        s = s.replace(/\\theta/g, 'θ');
        s = s.replace(/\\lambda/g, 'λ');
        s = s.replace(/\\delta/g, 'δ');
        s = s.replace(/\\Delta/g, 'Δ');
        s = s.replace(/\\det/g, 'det');
        s = s.replace(/\\approx/g, ' ≈ ');
        s = s.replace(/\\equiv/g, ' ≡ ');
        s = s.replace(/\\implies/g, ' ⟹ ');
        s = s.replace(/\\iff/g, ' ⟺ ');
        s = s.replace(/\\in/g, ' ∈ ');
        s = s.replace(/\\forall/g, ' ∀ ');
        s = s.replace(/\\exists/g, ' ∃ ');
        s = s.replace(/\\perp/g, ' ⊥ ');
        s = s.replace(/\\le/g, ' ≤ ');
        s = s.replace(/\\ge/g, ' ≥ ');
        s = s.replace(/\\neq/g, ' ≠ ');
        s = s.replace(/\\left\[/g, '[').replace(/\\right\]/g, ']');
        s = s.replace(/\\left\(/g, '(').replace(/\\right\)/g, ')');
        s = s.replace(/\\left|\\right/g, '');
        s = s.replace(/\\;/g, ' ').replace(/\\,/g, ' ').replace(/\\!/g, '');
        s = s.replace(/\\hat\{([^}]+)\}/g, '$1̂');
        return s;
    }

    // Convert matrix environments
    str = str.replace(/\\left\s*\[\s*\\begin\{(?:array|bmatrix|vmatrix|matrix|pmatrix)\}(?:\{([^}]+)\})?(.*?)\\end\{(?:array|bmatrix|vmatrix|matrix|pmatrix)\}\s*\\right\s*\]/gs, convertMatrix);
    str = str.replace(/\\begin\{(?:array|bmatrix|vmatrix|matrix|pmatrix)\}(?:\{([^}]+)\})?(.*?)\\end\{(?:array|bmatrix|vmatrix|matrix|pmatrix)\}/gs, convertMatrix);

    return cleanMathSymbols(str);
}

function extractInputSectionHTML() {
    let inputHTML = '';
    const matrixTextarea = document.getElementById('id_matrix_text');
    const vectorsTextarea = document.getElementById('id_vectors_text');
    const v1x = document.getElementById('id_v1_x');

    if (matrixTextarea && matrixTextarea.value.trim()) {
        const isAugmented = document.getElementById('gaussianGrid') !== null;
        const lines = matrixTextarea.value.trim().split('\n').map(l => l.trim()).filter(l => l.length > 0);
        let tableRows = '';
        lines.forEach(line => {
            const cells = line.split(/\s+/);
            tableRows += '<tr>';
            cells.forEach((cell, idx) => {
                const isAugCol = isAugmented && (idx === cells.length - 1);
                const borderLeft = isAugCol ? 'border-left: 1.5pt dashed #64748b;' : '';
                tableRows += `<td style="padding: 4pt 10pt; text-align: center; border: none; font-size: 11pt; font-weight: 500; ${borderLeft}">${cell}</td>`;
            });
            tableRows += '</tr>';
        });

        const label = isAugmented ? 'Input Augmented Matrix [A | b]:' : 'Input Coefficient Matrix A:';
        inputHTML = `
        <div style="background-color: #f1f5f9; border: 1pt solid #cbd5e1; border-radius: 6pt; padding: 12pt; margin-bottom: 16pt;">
            <h5 style="margin: 0 0 6pt 0; color: #1d4ed8;">${label}</h5>
            <div style="text-align: center;">
                <table style="display: inline-table; vertical-align: middle; border-left: 2.5pt solid #0f172a; border-right: 2.5pt solid #0f172a; border-collapse: collapse; margin: 4pt auto; background-color: #ffffff;">
                    <tbody>${tableRows}</tbody>
                </table>
            </div>
        </div>`;
    } else if (vectorsTextarea && vectorsTextarea.value.trim()) {
        const lines = vectorsTextarea.value.trim().split('\n').map(l => l.trim()).filter(l => l.length > 0);
        let vectorList = lines.map((l, i) => `<b>v</b><sub>${i+1}</sub> = [${l.split(/\s+/).join(', ')}]`).join('<br>');
        inputHTML = `
        <div style="background-color: #f1f5f9; border: 1pt solid #cbd5e1; border-radius: 6pt; padding: 12pt; margin-bottom: 16pt;">
            <h5 style="margin: 0 0 6pt 0; color: #1d4ed8;">Input Vector Set:</h5>
            <p style="margin: 0; font-family: Calibri, sans-serif; font-size: 11pt;">${vectorList}</p>
        </div>`;
    } else if (v1x) {
        const u = `[${document.getElementById('id_v1_x').value}, ${document.getElementById('id_v1_y').value}, ${document.getElementById('id_v1_z').value}]`;
        const v = `[${document.getElementById('id_v2_x').value}, ${document.getElementById('id_v2_y').value}, ${document.getElementById('id_v2_z').value}]`;
        inputHTML = `
        <div style="background-color: #f1f5f9; border: 1pt solid #cbd5e1; border-radius: 6pt; padding: 12pt; margin-bottom: 16pt;">
            <h5 style="margin: 0 0 6pt 0; color: #1d4ed8;">Input 3D Vectors:</h5>
            <p style="margin: 0; font-size: 11pt;">Vector <b>u</b> = ${u} &nbsp;&nbsp;|&nbsp;&nbsp; Vector <b>v</b> = ${v}</p>
        </div>`;
    }

    return inputHTML;
}

// Helper: Extract original TeX from MathJax container
function extractMathJaxTeX(mjxEl) {
    if (!mjxEl) return '';
    // 1. Check <annotation encoding="application/x-tex"> inside assistive-mml
    const annot = mjxEl.querySelector('annotation[encoding="application/x-tex"]') || mjxEl.querySelector('annotation');
    if (annot && annot.textContent && annot.textContent.trim()) {
        return annot.textContent.trim();
    }
    // 2. Check aria-label
    const ariaLabel = mjxEl.getAttribute('aria-label');
    if (ariaLabel && ariaLabel.trim()) {
        return ariaLabel.trim();
    }
    // 3. Check alt or title
    const alt = mjxEl.getAttribute('alt') || mjxEl.getAttribute('title');
    if (alt && alt.trim()) {
        return alt.trim();
    }
    // 4. Check data-latex
    if (mjxEl.dataset && mjxEl.dataset.latex) {
        return mjxEl.dataset.latex.trim();
    }
    return mjxEl.innerText || mjxEl.textContent || '';
}

// Helper: Format inline equations and formulas for Word
function formatEquationForWord(latex) {
    if (!latex) return '';
    let s = String(latex).trim();
    s = s.replace(/^\$\$+|\$\$+$|^[\$]|[\$]$/g, '').trim();

    // Check if it's a matrix environment
    if (s.includes('\\begin{array}') || s.includes('\\begin{bmatrix}') || s.includes('\\begin{matrix}') || s.includes('\\begin{vmatrix}') || s.includes('\\begin{pmatrix}')) {
        return latexToWordHTML(s);
    }

    // Replace fractions
    s = s.replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, '($1/$2)');
    s = s.replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, '($1/$2)');

    // Replace bold vectors and hats
    s = s.replace(/\\mathbf\{([^{}]+)\}/g, '<b>$1</b>');
    s = s.replace(/\\boldsymbol\{([^{}]+)\}/g, '<b>$1</b>');
    s = s.replace(/\\hat\{([^{}]+)\}/g, '<b>$1</b>̂');
    s = s.replace(/\\vec\{([^{}]+)\}/g, '<b>$1</b>');

    // Replace text / operators
    s = s.replace(/\\text\{([^{}]+)\}/g, '$1');
    s = s.replace(/\\operatorname\{([^{}]+)\}/g, '$1');
    s = s.replace(/\\cos/g, 'cos');
    s = s.replace(/\\sin/g, 'sin');
    s = s.replace(/\\tan/g, 'tan');
    s = s.replace(/\\arccos/g, 'arccos');
    s = s.replace(/\\det/g, 'det');
    s = s.replace(/\\pmod\{([^{}]+)\}/g, ' (mod $1)');
    s = s.replace(/\\sqrt\{([^{}]+)\}/g, '√($1)');

    // Replace arrows & relations
    s = s.replace(/\\leftarrow|\\gets/g, ' ← ');
    s = s.replace(/\\rightarrow|\\to/g, ' → ');
    s = s.replace(/\\implies|\\Longrightarrow/g, ' ⟹ ');
    s = s.replace(/\\iff|\\Longleftrightarrow/g, ' ⟺ ');
    s = s.replace(/\\approx/g, ' ≈ ');
    s = s.replace(/\\equiv/g, ' ≡ ');
    s = s.replace(/\\neq/g, ' ≠ ');
    s = s.replace(/\\le/g, ' ≤ ');
    s = s.replace(/\\ge/g, ' ≥ ');
    s = s.replace(/\\cdot/g, ' · ');
    s = s.replace(/\\times/g, ' × ');
    s = s.replace(/\\oplus/g, ' ⊕ ');
    s = s.replace(/\\odot/g, ' ⊙ ');
    s = s.replace(/\\perp/g, ' ⊥ ');
    s = s.replace(/\\parallel/g, ' ∥ ');

    // Replace Greek letters
    s = s.replace(/\\theta/g, 'θ');
    s = s.replace(/\\lambda/g, 'λ');
    s = s.replace(/\\delta/g, 'δ');
    s = s.replace(/\\Delta/g, 'Δ');
    s = s.replace(/\\alpha/g, 'α');
    s = s.replace(/\\beta/g, 'β');
    s = s.replace(/\\gamma/g, 'γ');
    s = s.replace(/\\pi/g, 'π');
    s = s.replace(/\\in/g, ' ∈ ');
    s = s.replace(/\\forall/g, ' ∀ ');
    s = s.replace(/\\exists/g, ' ∃ ');
    s = s.replace(/\\setminus/g, ' \\ ');
    s = s.replace(/\\gcd/g, 'gcd');

    // Replace subscripts & superscripts
    s = s.replace(/_\{([^{}]+)\}/g, '<sub>$1</sub>');
    s = s.replace(/_([0-9a-zA-Z])/g, '<sub>$1</sub>');
    s = s.replace(/\^\{([^{}]+)\}/g, '<sup>$1</sup>');
    s = s.replace(/\^([0-9a-zA-Z])/g, '<sup>$1</sup>');

    // Replace norms and delimiters
    s = s.replace(/\\\|/g, '||');
    s = s.replace(/\\left\[/g, '[').replace(/\\right\]/g, ']');
    s = s.replace(/\\left\(/g, '(').replace(/\\right\)/g, ')');
    s = s.replace(/\\left\\\{/g, '{').replace(/\\right\\\}/g, '}');
    s = s.replace(/\\\{/g, '{').replace(/\\\}/g, '}');
    s = s.replace(/\\left|\\right/g, '');
    s = s.replace(/\\langle/g, '⟨').replace(/\\rangle/g, '⟩');
    s = s.replace(/\\;/g, ' ').replace(/\\,/g, ' ').replace(/\\!/g, '').replace(/\\quad/g, '   ');

    return `<span style="font-family: 'Cambria Math', 'Segoe UI', Calibri, serif; color: #0f172a; font-weight: 600;">${s}</span>`;
}

function exportPageToWord(filename, elementId = null) {
    const defaultName = filename || document.title.replace(/[^a-zA-Z0-9_-]/g, '_') || 'linear_algebra_document';
    const target = elementId 
        ? document.getElementById(elementId) 
        : (document.getElementById('solutionSection') || document.querySelector('.main-content-wrapper') || document.body);

    if (!target) {
        window.print();
        return;
    }

    // Extract Page Title / Question header
    const pageHeadingEl = document.querySelector('h1') || document.querySelector('h2');
    const pageTitle = pageHeadingEl ? pageHeadingEl.innerText.trim() : document.title;
    const unitBadgeEl = document.querySelector('.badge-unit') || document.querySelector('.badge-topic');
    const unitText = unitBadgeEl ? unitBadgeEl.innerText.trim() : 'Linear Algebra Solver';

    // Extract Input Matrix / Vector Parameters
    const inputSectionHTML = extractInputSectionHTML();

    // Clone solution content and process math
    const clone = target.cloneNode(true);
    clone.querySelectorAll('.no-print, button, form, .matrix-resizer-controls, .preset-container, nav, header, footer').forEach(el => el.remove());

    // 1. Replace all explicit LaTeX blocks (like matrix snapshots & solution formulas) FIRST
    clone.querySelectorAll('.latex-scroll-wrapper, [data-latex]').forEach(wrapper => {
        let latex = wrapper.getAttribute('data-latex');
        if (!latex) {
            const assistive = wrapper.querySelector('mjx-assistive-mml');
            latex = assistive ? assistive.innerText : wrapper.innerText;
        }

        if (latex) {
            const formattedMath = latexToWordHTML(latex);
            wrapper.innerHTML = `<div style="text-align: center; margin: 8pt 0; font-family: 'Cambria Math', 'Calibri', serif;">${formattedMath}</div>`;
            wrapper.style.backgroundColor = '#f8fafc';
            wrapper.style.border = '1pt solid #cbd5e1';
            wrapper.style.borderRadius = '4pt';
            wrapper.style.padding = '8pt';
            wrapper.style.margin = '8pt 0';
        }
    });

    // 2. Process ALL remaining MathJax containers (in titles, headings, and inline text)
    clone.querySelectorAll('mjx-container').forEach(mjx => {
        const tex = extractMathJaxTeX(mjx);
        if (tex) {
            const formatted = formatEquationForWord(tex);
            const span = document.createElement('span');
            span.innerHTML = formatted;
            mjx.replaceWith(span);
        } else {
            mjx.remove();
        }
    });

    // Remove empty assistive tags if any remain
    clone.querySelectorAll('mjx-assistive-mml').forEach(el => el.remove());

    const docTitle = document.title || 'Linear Algebra Derivation Report';
    const nowStr = new Date().toLocaleString();

    const wordHTML = `
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head>
<meta charset='utf-8'>
<title>${docTitle}</title>
<!--[if gte mso 9]>
<xml>
<w:WordDocument>
<w:View>Print</w:View>
<w:Zoom>100</w:Zoom>
<w:DoNotOptimizeForBrowser/>
</w:WordDocument>
</xml>
<![endif]-->
<style>
  @page {
    size: A4 portrait;
    margin: 20mm 15mm 20mm 15mm;
    mso-header-margin: 36pt;
    mso-footer-margin: 36pt;
  }
  body {
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #0f172a;
    background-color: #ffffff;
    padding: 0;
    margin: 0;
  }
  .doc-header {
    border-bottom: 2.5pt solid #1d4ed8;
    padding-bottom: 10pt;
    margin-bottom: 16pt;
  }
  .doc-title {
    font-size: 20pt;
    font-weight: bold;
    color: #0f172a;
    margin: 0 0 4pt 0;
  }
  .doc-subtitle {
    font-size: 10.5pt;
    color: #475569;
    margin: 0;
  }
  .question-box {
    background-color: #eff6ff;
    border-left: 3.5pt solid #2563eb;
    border-radius: 4pt;
    padding: 10pt 14pt;
    margin-bottom: 16pt;
  }
  h1, h2, h3, h4, h5, h6 {
    color: #0f172a;
    font-weight: bold;
    margin-top: 14pt;
    margin-bottom: 6pt;
  }
  h4 { font-size: 14pt; color: #138808; }
  h5 { font-size: 12pt; color: #1d4ed8; }
  p { margin: 0 0 8pt 0; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 10pt 0;
  }
  th, td {
    border: 1pt solid #cbd5e1;
    padding: 6pt 10pt;
    text-align: center;
    font-size: 10.5pt;
  }
  th {
    background-color: #f1f5f9;
    font-weight: bold;
    color: #0f172a;
  }
  .badge {
    display: inline-block;
    padding: 2pt 6pt;
    font-weight: bold;
    border-radius: 4pt;
    font-size: 9pt;
    background-color: #f1f5f9;
    color: #334155;
    border: 0.5pt solid #cbd5e1;
  }
  .badge-topic {
    background-color: #fee2e2 !important;
    color: #991b1b !important;
  }
  .bg-success {
    background-color: #dcfce7 !important;
    color: #166534 !important;
  }
  .single-step-section, .single-vector-step, .single-term-section, .single-section-block, .single-axiom-section {
    border-bottom: 1pt solid #e2e8f0;
    padding-bottom: 12pt;
    margin-bottom: 12pt;
  }
  .doc-footer {
    margin-top: 24pt;
    border-top: 1pt solid #cbd5e1;
    padding-top: 8pt;
    font-size: 9pt;
    color: #64748b;
    text-align: center;
  }
</style>
</head>
<body>
  <div class="doc-header">
    <div class="doc-title">Linear Algebra Explorer</div>
    <div class="doc-subtitle">${unitText} • ${pageTitle} • Generated on ${nowStr}</div>
  </div>

  <!-- Question & Problem Statement Box -->
  <div class="question-box">
    <div style="font-size: 12pt; font-weight: bold; color: #1e3a8a; margin-bottom: 4pt;">
      Problem Formulation &amp; Task Objective
    </div>
    <p style="margin: 0 0 6pt 0; color: #334155;">
      Evaluate step-by-step mathematical derivation for <strong>${pageTitle}</strong> using linear algebraic row operations and exact algorithms.
    </p>
  </div>

  <!-- Input Data Section -->
  ${inputSectionHTML}

  <!-- Computed Step-by-Step Derivations & Solutions -->
  <div class="doc-content">
    ${clone.innerHTML}
  </div>

  <div class="doc-footer">
    Report exported from <strong>Linear Algebra Explorer</strong> • Data Science Linear Algebra &amp; Python 3.14 / Django
  </div>
</body>
</html>`;

    const blob = new Blob(['\ufeff', wordHTML], {
        type: 'application/msword'
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${defaultName}.doc`;
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }, 200);
}

