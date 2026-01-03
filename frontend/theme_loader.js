const ANIMATION_CSS = `
/* Futuristic Apple Emoji Background */
.apple-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: -1;
    overflow: hidden;
    opacity: 0.5;
}

.apple-bg span {
    position: absolute;
    display: block;
    font-size: 2rem;
    animation: floatUp 15s linear infinite;
    bottom: -50px;
}

@keyframes floatUp {
    0% { transform: translateY(0) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-110vh) rotate(360deg); opacity: 0; }
}

/* Loading Overlay */
.loading-overlay {
    display: none; /* Toggled via JS */
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    z-index: 1000;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    color: white;
    font-family: monospace;
}

.loader {
    width: 50px;
    height: 50px;
    border: 5px solid #fff;
    border-bottom-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}

.loading-text {
    font-size: 1.5rem;
    letter-spacing: 2px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;

document.addEventListener("DOMContentLoaded", () => {
    // 1. Inject CSS for animations directly
    const style = document.createElement("style");
    style.textContent = ANIMATION_CSS;
    document.head.appendChild(style);

    // 2. Inject Background with Apple Emojis
    const bgDiv = document.createElement("div");
    bgDiv.className = "apple-bg";
    
    // Create floating emojis with distributed positions
    const baseEmojis = ['👁️‍🗨️', '⚠️', '🤖'];
    const totalEmojis = 20;

    for (let i = 0; i < totalEmojis; i++) {
        const span = document.createElement("span");
        span.innerText = baseEmojis[i % baseEmojis.length];
        // Evenly spread horizontal position (0-100%)
        span.style.left = `${(i / totalEmojis) * 100}%`;
        // Random animation delay (0-20s) to stagger them
        span.style.animationDelay = `${Math.random() * 20}s`;
        // Random size variation
        span.style.fontSize = `${2 + Math.random()}rem`;
        bgDiv.appendChild(span);
    }
    
    document.body.prepend(bgDiv);

    // 3. Inject Loading Overlay HTML
    const loaderDiv = document.createElement("div");
    loaderDiv.id = "loading-overlay";
    loaderDiv.className = "loading-overlay";
    loaderDiv.innerHTML = `
        <div class="loader"></div>
        <div class="loading-text">PROCESSING MEDIA...</div>
    `;
    document.body.appendChild(loaderDiv);
});

// Expose global functions to toggle loader
window.showLoader = function() {
    const loader = document.getElementById('loading-overlay');
    if (loader) loader.style.display = 'flex';
};

window.hideLoader = function() {
    const loader = document.getElementById('loading-overlay');
    if (loader) loader.style.display = 'none';
};