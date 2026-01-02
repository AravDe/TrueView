const API_BASE = 'http://localhost:8000';

function handleFileSelect() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const fileNameSpan = document.getElementById('fileName');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const imgPreview = document.getElementById('imagePreview');
    const vidPreview = document.getElementById('videoPreview');

    if (file) {
        fileNameSpan.textContent = file.name;
        analyzeBtn.style.display = 'block';
        
        const url = URL.createObjectURL(file);
        
        if (file.type.startsWith('video/')) {
            vidPreview.src = url;
            vidPreview.style.display = 'block';
            imgPreview.style.display = 'none';
        } else {
            imgPreview.src = url;
            imgPreview.style.display = 'block';
            vidPreview.style.display = 'none';
        }
    }
}

async function handleAnalysis() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) return alert('Please select a file first.');

    const btn = document.getElementById('analyzeBtn');
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('resultsSection');
    const verdictCard = document.getElementById('verdictCard');
    const metricsGrid = document.getElementById('metricsGrid');
    const resultMediaContainer = document.getElementById('resultMediaContainer');
    const headerBtn = document.getElementById('headerNewAnalysisBtn');

    // Reset UI
    btn.disabled = true;
    btn.textContent = 'Uploading & Scanning...';
    metricsGrid.innerHTML = '';
    verdictCard.className = 'verdict-card verdict-loading'; 
    verdictCard.style.background = ''; 
    document.getElementById('verdictTitle').textContent = 'PROCESSING DATA...';
    document.getElementById('verdictOverview').textContent = '';

    try {
        // STEP 1: Upload & Initial Scan
        const formData = new FormData();
        formData.append('file', file);

        const uploadResp = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResp.ok) throw new Error('Upload failed');
        const initialData = await uploadResp.json();

        // Switch Views
        uploadSection.style.display = 'none';
        resultsSection.style.display = 'block';
        headerBtn.style.display = 'block';
        
        // Move preview to results
        resultMediaContainer.innerHTML = '';
        const imgPreview = document.getElementById('imagePreview');
        const vidPreview = document.getElementById('videoPreview');
        
        if (imgPreview.style.display !== 'none') {
            const clone = imgPreview.cloneNode(true);
            clone.style.display = 'block';
            clone.style.height = 'auto';
            clone.style.width = '100%';
            resultMediaContainer.appendChild(clone);
        } else if (vidPreview.style.display !== 'none') {
            const clone = vidPreview.cloneNode(true);
            clone.style.display = 'block';
            clone.style.height = 'auto';
            clone.style.width = '100%';
            resultMediaContainer.appendChild(clone);
        }

        // Render Verdict
        const aiResult = initialData.ai_scan_result;
        const isFake = aiResult.ai_detected || aiResult.deepfake_detected;
        const confidence = Math.max(aiResult.ai_confidence, aiResult.deepfake_confidence) * 100;

        verdictCard.className = `verdict-card ${isFake ? 'verdict-fake' : 'verdict-real'}`;
        document.getElementById('verdictTitle').textContent = isFake ? 'AI-GENERATED CONTENT DETECTED' : 'CONTENT APPEARS AUTHENTIC';
        document.getElementById('verdictConfidence').textContent = `Confidence: ${confidence.toFixed(1)}%`;
        document.getElementById('verdictOverview').textContent = initialData.brief_overview;

        // Render Metric Placeholders (Loading State)
        const metrics = initialData.analysis_result.metrics;
        Object.keys(metrics).forEach(key => {
            const card = document.createElement('div');
            card.id = `metric-${key}`;
            card.className = 'metric-card loading';
            card.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <div class="spinner"></div>
                    <h3>${key.replace(/_/g, ' ')}</h3>
                </div>
                <p style="font-size: 0.8rem; text-transform: uppercase;">Scanning...</p>
            `;
            metricsGrid.appendChild(card);
        });

        // STEP 2: Fetch Detailed Metrics (Parallel)
        fetchDetailedMetrics(initialData.analysis_result);

    } catch (error) {
        alert('Error: ' + error.message);
        btn.disabled = false;
        btn.textContent = 'Analyze Media';
    }
}

async function fetchDetailedMetrics(analysisResult) {
    try {
        const resp = await fetch(`${API_BASE}/analyze/metrics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ analysis_result: analysisResult })
        });

        if (!resp.ok) throw new Error('Metric analysis failed');
        const data = await resp.json();

        // Update Metric Cards
        data.metricExplanations.forEach(metric => {
            const card = document.getElementById(`metric-${metric.metric_name}`);
            if (card) {
                card.className = 'metric-card';
                const statusClass = `status-${metric.status}`;
                const statusLabel = metric.status === 'normal' ? 'NORMAL' : 'SUSPICIOUS';
                
                card.innerHTML = `
                    <h3>${metric.display_name}</h3>
                    <div class="metric-value">${metric.actual_value.toFixed(2)}</div>
                    <div style="margin-bottom: 1rem;">
                        <span class="metric-status ${statusClass}">${statusLabel}</span>
                        <span style="font-size: 0.8rem; margin-left: 10px; font-family: 'Courier New', monospace;">[${metric.expected_range}]</span>
                    </div>
                    <p style="font-size: 0.9rem; line-height: 1.5;">${metric.analysis}</p>
                `;
            }
        });

        // Show notification popup
        const popup = document.getElementById('notificationPopup');
        popup.classList.add('show');
        setTimeout(() => {
            popup.classList.remove('show');
        }, 5000);

    } catch (error) {
        console.error('Metric fetch error:', error);
    }
}

function scrollToMetrics() {
    document.getElementById('metricsSection').scrollIntoView({ behavior: 'smooth' });
}