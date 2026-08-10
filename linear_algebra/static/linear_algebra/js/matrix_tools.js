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

