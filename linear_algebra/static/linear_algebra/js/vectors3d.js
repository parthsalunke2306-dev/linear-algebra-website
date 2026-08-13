/**
 * 3D Vector Visualizer Canvas Component
 * Renders 3D Vectors v1, v2, Projection, and Cross Product on HTML5 Canvas
 */
function initVectorCanvas(canvasId, v1, v2, crossProd, projVec) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let width = 340;
    let height = 320;

    let angleX = 0.5;
    let angleY = 0.6;
    let isDragging = false;
    let lastMouseX = 0;
    let lastMouseY = 0;

    let zoomLevel = 1.0;

    function project(x, y, z) {
        const originX = width / 2;
        const originY = height / 2;
        const baseScale = Math.max(Math.min(width, height) / 12, 22);
        const scale = baseScale * zoomLevel;

        // Rotate around Y
        let radY = angleY;
        let x1 = x * Math.cos(radY) + z * Math.sin(radY);
        let z1 = -x * Math.sin(radY) + z * Math.cos(radY);

        // Rotate around X
        let radX = angleX;
        let y2 = y * Math.cos(radX) - z1 * Math.sin(radX);
        let z2 = y * Math.sin(radX) + z1 * Math.cos(radX);

        return {
            px: originX + x1 * scale,
            py: originY - y2 * scale
        };
    }

    // Expose Zoom & Reset Control Functions Globally
    window.zoomVectorCanvas = function(factor) {
        zoomLevel = Math.max(0.3, Math.min(4.0, zoomLevel * factor));
        render();
    };

    window.resetVectorCanvasView = function() {
        zoomLevel = 1.0;
        angleX = 0.5;
        angleY = 0.6;
        render();
    };

    function formatCoord(val) {
        if (typeof val === 'number') {
            return Number.isInteger(val) ? val.toString() : val.toFixed(2);
        }
        return val;
    }

    function formatLabel(name, coords) {
        if (!coords || coords.length < 3) return name;
        return `${name} (${formatCoord(coords[0])}, ${formatCoord(coords[1])}, ${formatCoord(coords[2])})`;
    }

    function drawArrow(ctx, fromX, fromY, toX, toY, color, label, strokeWidth = 3, pointRadius = 4) {
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = strokeWidth;
        ctx.moveTo(fromX, fromY);
        ctx.lineTo(toX, toY);
        ctx.stroke();

        // Arrow head
        const angle = Math.atan2(toY - fromY, toX - fromX);
        const headLen = 10;
        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6), toY - headLen * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6), toY - headLen * Math.sin(angle + Math.PI / 6));
        ctx.fill();

        // Plotted Point Coordinate Dot at Tip
        if (strokeWidth > 1.5) {
            ctx.beginPath();
            ctx.arc(toX, toY, pointRadius, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.lineWidth = 1.5;
            ctx.strokeStyle = '#FFFFFF';
            ctx.stroke();
        }

        // Label with Coordinates
        if (label) {
            ctx.font = 'bold 11px Inter, sans-serif';
            ctx.fillStyle = color;
            ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
            ctx.shadowBlur = 4;
            ctx.fillText(label, toX + 8, toY - 6);
            ctx.shadowBlur = 0;
        }
    }

    function render() {
        if (!width || !height) return;
        ctx.clearRect(0, 0, width, height);

        // Draw 3D Axes
        const o = project(0, 0, 0);
        const xAxis = project(6, 0, 0);
        const yAxis = project(0, 6, 0);
        const zAxis = project(0, 0, 6);

        drawArrow(ctx, o.px, o.py, xAxis.px, xAxis.py, '#94a3b8', 'X', 1.5);
        drawArrow(ctx, o.px, o.py, yAxis.px, yAxis.py, '#94a3b8', 'Y', 1.5);
        drawArrow(ctx, o.px, o.py, zAxis.px, zAxis.py, '#94a3b8', 'Z', 1.5);

        // Draw Vector v1 with Coordinates
        if (v1) {
            const p1 = project(v1[0], v1[1], v1[2]);
            drawArrow(ctx, o.px, o.py, p1.px, p1.py, '#06b6d4', formatLabel('v1', v1), 3.5);
        }

        // Draw Vector v2 with Coordinates
        if (v2) {
            const p2 = project(v2[0], v2[1], v2[2]);
            drawArrow(ctx, o.px, o.py, p2.px, p2.py, '#6366f1', formatLabel('v2', v2), 3.5);
        }

        // Draw Projection Vector with Coordinates
        if (projVec && v1) {
            const p1 = project(v1[0], v1[1], v1[2]);
            const pProj = project(projVec[0], projVec[1], projVec[2]);
            drawArrow(ctx, o.px, o.py, pProj.px, pProj.py, '#f59e0b', formatLabel('proj', projVec), 2.5);

            // Dotted line from v1 tip to proj tip
            ctx.beginPath();
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 1.5;
            ctx.moveTo(p1.px, p1.py);
            ctx.lineTo(pProj.px, pProj.py);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Draw Cross Product Vector with Coordinates
        if (crossProd && (crossProd[0] !== 0 || crossProd[1] !== 0 || crossProd[2] !== 0)) {
            const pCross = project(crossProd[0], crossProd[1], crossProd[2]);
            drawArrow(ctx, o.px, o.py, pCross.px, pCross.py, '#10b981', formatLabel('v1 × v2', crossProd), 3);
        }
    }

    function resizeCanvas() {
        if (!canvas.parentElement) return;
        const pWidth = canvas.parentElement.clientWidth;
        width = canvas.width = pWidth > 0 ? pWidth : (canvas.clientWidth || 340);
        height = canvas.height = 320;
        render();
    }

    function getEventPos(e) {
        if (e.touches && e.touches.length > 0) {
            return { x: e.touches[0].clientX, y: e.touches[0].clientY };
        }
        return { x: e.clientX, y: e.clientY };
    }

    function handleStart(e) {
        isDragging = true;
        const pos = getEventPos(e);
        lastMouseX = pos.x;
        lastMouseY = pos.y;
    }

    function handleMove(e) {
        if (!isDragging) return;
        if (e.touches && e.touches.length === 1) {
            e.preventDefault();
        }
        const pos = getEventPos(e);
        const deltaX = pos.x - lastMouseX;
        const deltaY = pos.y - lastMouseY;
        angleY += deltaX * 0.012;
        angleX += deltaY * 0.012;
        lastMouseX = pos.x;
        lastMouseY = pos.y;
        render();
    }

    function handleEnd() {
        isDragging = false;
    }

    // Mouse Event Listeners
    canvas.addEventListener('mousedown', handleStart);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleEnd);

    // Mouse Wheel Zooming
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.15 : 0.85;
        zoomLevel = Math.max(0.3, Math.min(4.0, zoomLevel * factor));
        render();
    }, { passive: false });

    // Touch Event Listeners for Mobile & Tablet 3D Orbiting
    canvas.addEventListener('touchstart', handleStart, { passive: false });
    window.addEventListener('touchmove', handleMove, { passive: false });
    window.addEventListener('touchend', handleEnd);
    window.addEventListener('touchcancel', handleEnd);

    // Window Resize Handling
    window.addEventListener('resize', resizeCanvas);

    // Initial resize and render
    resizeCanvas();
    setTimeout(resizeCanvas, 100);
}



