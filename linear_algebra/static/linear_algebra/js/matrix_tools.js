/**
 * Matrix Tools & Interactive UI Scripts
 * Handles Light/Dark Theme Switching, Representation of Matrix Grid, Presets & LaTeX Copying
 */

// 1. Light/Dark Theme Switcher & Matrix Grid Initialization
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Initialize Representation of Matrix Grid for all matrix input textareas
    initMatrixGrids();
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

// 3. REPRESENTATION OF MATRIX GRID & DYNAMIC RESIZER
function initMatrixGrids() {
    const textareas = document.querySelectorAll('textarea#id_matrix_text, textarea#id_vectors_text');
    textareas.forEach(textarea => {
        if (!textarea.id) return;
        
        // Hide original raw textarea (keep synced for form post)
        textarea.style.display = 'none';
        
        let wrapper = document.getElementById(`grid_wrapper_${textarea.id}`);
        if (!wrapper) {
            wrapper = document.createElement('div');
            wrapper.id = `grid_wrapper_${textarea.id}`;
            wrapper.className = 'matrix-grid-wrapper';
            textarea.parentNode.insertBefore(wrapper, textarea);
        }
        
        renderMatrixGrid(textarea.id);
    });
}

function renderMatrixGrid(textareaId) {
    const textarea = document.getElementById(textareaId);
    const wrapper = document.getElementById(`grid_wrapper_${textareaId}`);
    if (!textarea || !wrapper) return;

    let val = textarea.value.trim();
    if (!val) {
        val = "1 2 -1 8\n-3 -1 2 -11\n2 1 2 -3";
        textarea.value = val;
    }

    let lines = val.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    let matrix = lines.map(line => line.split(/\s+/));
    let numRows = matrix.length;
    let numCols = matrix[0] ? matrix[0].length : 1;

    let html = `
        <div class="matrix-grid-header-label">
            <span><i class="bi bi-grid-3x3-gap-fill text-purple me-2"></i>Representation of Matrix Grid</span>
            <span class="text-muted font-monospace" style="font-size: 0.75rem;">
                <i class="bi bi-arrow-right text-cyan me-1"></i>Columns: ${numCols} | <i class="bi bi-arrow-down text-purple me-1"></i>Rows: ${numRows}
            </span>
        </div>
        <table class="matrix-grid-table">
            <thead>
                <tr>
                    <th class="row-header-arrow"><span class="text-muted" style="font-size: 0.7rem;">Rows ↓ \\ Cols →</span></th>
    `;

    // Render Column Headers (0, 1, 2, 3...)
    for (let j = 0; j < numCols; j++) {
        html += `<th class="col-index-th">Col ${j}</th>`;
    }
    html += `</tr></thead><tbody>`;

    // Render Data Rows with Row Headers (Row 0, Row 1, Row 2...)
    for (let i = 0; i < numRows; i++) {
        html += `<tr><th class="row-index-th">Row ${i}</th>`;
        for (let j = 0; j < numCols; j++) {
            let cellValue = (matrix[i] && matrix[i][j] !== undefined) ? matrix[i][j] : '0';
            html += `
                <td>
                    <input type="text" class="matrix-grid-cell-input" 
                           data-target="${textareaId}" data-row="${i}" data-col="${j}" 
                           value="${cellValue}" 
                           oninput="onMatrixGridCellInput('${textareaId}')"
                           autocomplete="off">
                </td>
            `;
        }
        html += `</tr>`;
    }

    html += `</tbody></table>`;
    wrapper.innerHTML = html;
}

function onMatrixGridCellInput(textareaId) {
    const textarea = document.getElementById(textareaId);
    const wrapper = document.getElementById(`grid_wrapper_${textareaId}`);
    if (!textarea || !wrapper) return;

    const inputs = wrapper.querySelectorAll('.matrix-grid-cell-input');
    let matrixDict = {};
    let maxRow = 0;
    let maxCol = 0;

    inputs.forEach(input => {
        let r = parseInt(input.getAttribute('data-row'), 10);
        let c = parseInt(input.getAttribute('data-col'), 10);
        if (!matrixDict[r]) matrixDict[r] = {};
        matrixDict[r][c] = input.value.trim() === '' ? '0' : input.value.trim();
        if (r > maxRow) maxRow = r;
        if (c > maxCol) maxCol = c;
    });

    let lines = [];
    for (let i = 0; i <= maxRow; i++) {
        let rowVals = [];
        for (let j = 0; j <= maxCol; j++) {
            rowVals.push((matrixDict[i] && matrixDict[i][j] !== undefined) ? matrixDict[i][j] : '0');
        }
        lines.push(rowVals.join(' '));
    }

    textarea.value = lines.join('\n');
}

function modifyMatrixSize(textareaId, action) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;

    let lines = textarea.value.trim().split('\n').filter(l => l.trim().length > 0);
    if (lines.length === 0) {
        lines = ["0 0 0", "0 0 0", "0 0 0"];
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
    }

    textarea.value = matrix.map(row => row.join(' ')).join('\n');
    renderMatrixGrid(textareaId);
}

// Hook preset loaders to update the matrix grid representation
const originalLoadGaussianPreset = window.loadGaussianPreset;
window.updateGridAfterPreset = function(textareaId) {
    setTimeout(() => {
        renderMatrixGrid(textareaId);
    }, 50);
};
