// This is a standalone, embeddable animation of the MCO progressive revelation workflow
// You can embed this in any HTML page or iframe

const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCO Progressive Revelation</title>
    <style>
        .mco-animation-container {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .mco-animation-title {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }
        
        .mco-animation-stage {
            position: relative;
            height: 450px;
            border: 1px solid #ddd;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .mco-agent {
            position: absolute;
            width: 70px;
            height: 70px;
            background-color: #3498db;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: bold;
            font-size: 16px;
            z-index: 10;
            transition: left 1.5s ease-in-out, top 1.5s ease-in-out;
            left: 50px;
            top: 190px;
        }
        
        .mco-step {
            position: absolute;
            width: 100px;
            height: 50px;
            background-color: #2ecc71;
            border-radius: 25px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: bold;
            z-index: 5;
            font-size: 14px;
        }
        
        .mco-step-1 { left: 150px; top: 200px; }
        .mco-step-2 { left: 280px; top: 200px; }
        .mco-step-3 { left: 410px; top: 200px; }
        .mco-step-4 { left: 540px; top: 200px; }
        .mco-step-5 { left: 670px; top: 200px; }
        
        .mco-context-container {
            position: absolute;
            width: 100%;
            height: 160px;
            top: 20px;
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .mco-context-box {
            width: 160px;
            height: 140px;
            border-radius: 8px;
            padding: 12px;
            box-sizing: border-box;
            color: white;
            font-size: 13px;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }
        
        .mco-core { background-color: #e74c3c; }
        .mco-sc { background-color: #9b59b6; }
        .mco-features { background-color: #f39c12; }
        .mco-styles { background-color: #16a085; }
        
        .mco-injection-container {
            position: absolute;
            width: 100%;
            height: 160px;
            bottom: 20px;
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .mco-injection {
            width: 160px;
            height: 140px;
            border-radius: 8px;
            padding: 12px;
            box-sizing: border-box;
            color: white;
            font-size: 13px;
            opacity: 0;
            transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
            transform: translateY(50px);
        }
        
        .mco-injection.active {
            opacity: 1;
            transform: translateY(0);
        }
        
        .mco-arrow {
            position: absolute;
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-bottom: 16px solid #f39c12;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }
        
        .mco-arrow-features {
            left: 50%;
            bottom: 180px;
            transform: translateX(-90px);
        }
        
        .mco-arrow-styles {
            left: 50%;
            bottom: 180px;
            transform: translateX(60px);
            border-bottom-color: #16a085;
        }
        
        .mco-controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        
        .mco-button {
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        
        .mco-button:hover {
            background-color: #2980b9;
        }
        
        .mco-status {
            text-align: center;
            margin-top: 15px;
            font-size: 16px;
            color: #555;
            height: 20px;
        }
        
        .mco-legend {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
        }
        
        .mco-legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
        }
        
        .mco-legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="mco-animation-container">
        <h2 class="mco-animation-title">MCO Progressive Revelation</h2>
        
        <div class="mco-animation-stage">
            <div class="mco-context-container">
                <div class="mco-context-box mco-core" id="mco-core-box">
                    <strong>mco.core</strong><br>
                    Workflow definition<br>
                    Data variables<br>
                    Agent steps<br>
                    <small>Always in persistent memory</small>
                </div>
                <div class="mco-context-box mco-sc" id="mco-sc-box">
                    <strong>mco.sc</strong><br>
                    Goal<br>
                    Success criteria<br>
                    Target audience<br>
                    <small>Always in persistent memory</small>
                </div>
                <div class="mco-context-box mco-features" id="mco-features-box">
                    <strong>mco.features</strong><br>
                    Implementation details<br>
                    Additional functionality<br>
                    <small>Injected during implementation steps</small>
                </div>
                <div class="mco-context-box mco-styles" id="mco-styles-box">
                    <strong>mco.styles</strong><br>
                    Formatting preferences<br>
                    Presentation guidelines<br>
                    <small>Injected during formatting steps</small>
                </div>
            </div>
            
            <div class="mco-step mco-step-1">Research</div>
            <div class="mco-step mco-step-2">Analyze</div>
            <div class="mco-step mco-step-3">Implement</div>
            <div class="mco-step mco-step-4">Format</div>
            <div class="mco-step mco-step-5">Finalize</div>
            
            <div class="mco-agent" id="mco-agent">Agent</div>
            
            <div class="mco-injection-container">
                <div class="mco-injection mco-features" id="mco-features-injection">
                    <strong>Features Injection</strong><br>
                    - Data visualizations<br>
                    - Executive summary<br>
                    - Comparative analysis<br>
                    <small>Injected at step 3</small>
                </div>
                <div class="mco-injection mco-styles" id="mco-styles-injection">
                    <strong>Styles Injection</strong><br>
                    - Professional tone<br>
                    - Clear headings<br>
                    - Consistent formatting<br>
                    <small>Injected at step 4</small>
                </div>
            </div>
            
            <div class="mco-arrow mco-arrow-features" id="mco-arrow-features"></div>
            <div class="mco-arrow mco-arrow-styles" id="mco-arrow-styles"></div>
        </div>
        
        <div class="mco-legend">
            <div class="mco-legend-item">
                <div class="mco-legend-color" style="background-color: #e74c3c;"></div>
                <span>mco.core</span>
            </div>
            <div class="mco-legend-item">
                <div class="mco-legend-color" style="background-color: #9b59b6;"></div>
                <span>mco.sc</span>
            </div>
            <div class="mco-legend-item">
                <div class="mco-legend-color" style="background-color: #f39c12;"></div>
                <span>mco.features</span>
            </div>
            <div class="mco-legend-item">
                <div class="mco-legend-color" style="background-color: #16a085;"></div>
                <span>mco.styles</span>
            </div>
        </div>
        
        <div class="mco-status" id="mco-status">Workflow starting...</div>
        
        <div class="mco-controls">
            <button class="mco-button" id="mco-play-btn">Play Animation</button>
            <button class="mco-button" id="mco-reset-btn">Reset</button>
        </div>
    </div>

    <script>
        // Self-executing function to avoid global namespace pollution
        (function() {
            // Wait for DOM to be fully loaded
            document.addEventListener('DOMContentLoaded', function() {
                initMCOAnimation();
            });
            
            // Initialize animation if DOM is already loaded
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                initMCOAnimation();
            }
            
            function initMCOAnimation() {
                const agent = document.getElementById('mco-agent');
                const coreBox = document.getElementById('mco-core-box');
                const scBox = document.getElementById('mco-sc-box');
                const featuresBox = document.getElementById('mco-features-box');
                const stylesBox = document.getElementById('mco-styles-box');
                const featuresInjection = document.getElementById('mco-features-injection');
                const stylesInjection = document.getElementById('mco-styles-injection');
                const arrowFeatures = document.getElementById('mco-arrow-features');
                const arrowStyles = document.getElementById('mco-arrow-styles');
                const statusText = document.getElementById('mco-status');
                const playBtn = document.getElementById('mco-play-btn');
                const resetBtn = document.getElementById('mco-reset-btn');
                
                if (!agent || !playBtn) {
                    console.error('MCO Animation: Required elements not found');
                    return;
                }
                
                let animationRunning = false;
                let animationTimeouts = [];
                
                // Step positions
                const steps = [
                    { left: 150, top: 190 },  // Research
                    { left: 280, top: 190 },  // Analyze
                    { left: 410, top: 190 },  // Implement
                    { left: 540, top: 190 },  // Format
                    { left: 670, top: 190 }   // Finalize
                ];
                
                // Status messages
                const statusMessages = [
                    "Starting workflow with persistent context...",
                    "Step 1: Researching with core and sc in context",
                    "Step 2: Analyzing findings with persistent context",
                    "Step 3: Implementing with features injected",
                    "Step 4: Formatting with styles injected",
                    "Step 5: Finalizing with complete context"
                ];
                
                function resetAnimation() {
                    // Clear all timeouts
                    animationTimeouts.forEach(timeout => clearTimeout(timeout));
                    animationTimeouts = [];
                    animationRunning = false;
                    
                    // Reset agent position
                    agent.style.left = '50px';
                    agent.style.top = '190px';
                    
                    // Reset context boxes
                    coreBox.style.opacity = '0';
                    scBox.style.opacity = '0';
                    featuresBox.style.opacity = '0';
                    stylesBox.style.opacity = '0';
                    
                    // Reset injections
                    featuresInjection.classList.remove('active');
                    stylesInjection.classList.remove('active');
                    
                    // Reset arrows
                    arrowFeatures.style.opacity = '0';
                    arrowStyles.style.opacity = '0';
                    
                    // Reset status
                    statusText.textContent = "Workflow starting...";
                    
                    // Reset button
                    playBtn.textContent = "Play Animation";
                }
                
                function runAnimation() {
                    if (animationRunning) {
                        resetAnimation();
                        return;
                    }
                    
                    animationRunning = true;
                    playBtn.textContent = "Stop Animation";
                    
                    // Start animation sequence
                    
                    // Show persistent context
                    animationTimeouts.push(setTimeout(() => {
                        coreBox.style.opacity = '1';
                        scBox.style.opacity = '1';
                        statusText.textContent = statusMessages[0];
                    }, 500));
                    
                    // Step 1: Research
                    animationTimeouts.push(setTimeout(() => {
                        agent.style.left = steps[0].left + 'px';
                        statusText.textContent = statusMessages[1];
                    }, 2000));
                    
                    // Step 2: Analyze
                    animationTimeouts.push(setTimeout(() => {
                        agent.style.left = steps[1].left + 'px';
                        statusText.textContent = statusMessages[2];
                    }, 4000));
                    
                    // Step 3: Implement with features injection
                    animationTimeouts.push(setTimeout(() => {
                        agent.style.left = steps[2].left + 'px';
                        featuresBox.style.opacity = '1';
                        arrowFeatures.style.opacity = '1';
                        featuresInjection.classList.add('active');
                        statusText.textContent = statusMessages[3];
                    }, 6000));
                    
                    // Step 4: Format with styles injection
                    animationTimeouts.push(setTimeout(() => {
                        agent.style.left = steps[3].left + 'px';
                        stylesBox.style.opacity = '1';
                        arrowStyles.style.opacity = '1';
                        stylesInjection.classList.add('active');
                        statusText.textContent = statusMessages[4];
                    }, 8000));
                    
                    // Step 5: Finalize
                    animationTimeouts.push(setTimeout(() => {
                        agent.style.left = steps[4].left + 'px';
                        statusText.textContent = statusMessages[5];
                    }, 10000));
                    
                    // Reset after complete animation
                    animationTimeouts.push(setTimeout(() => {
                        resetAnimation();
                    }, 12000));
                }
                
                // Event listeners
                playBtn.addEventListener('click', runAnimation);
                resetBtn.addEventListener('click', resetAnimation);
                
                // Initial reset
                resetAnimation();
            }
        })();
    </script>
</body>
</html>
`;

// Export the HTML string for easy embedding
if (typeof module !== 'undefined' && module.exports) {
    module.exports = html;
}
