const alertBox = document.getElementById('warning-box');
const threatLevel = document.getElementById('threat-level');
const logList = document.getElementById('log-list');

function addLog(message, isWarning = false) {
    const li = document.createElement('li');
    const time = new Date().toLocaleTimeString();
    li.innerHTML = `<span class="time">[${time}]</span> <span style="color: ${isWarning ? '#ff003c' : '#ccc'}">${message}</span>`;
    logList.appendChild(li);
    // Keep max 50 logs
    if (logList.children.length > 50) {
        logList.removeChild(logList.firstChild);
    }
    // Auto scroll bottom
    logList.parentElement.scrollTop = logList.parentElement.scrollHeight;
}

let wasWarning = false;

// Poll the status every half second
setInterval(async () => {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        if (data.warning) {
            alertBox.classList.add('active');
            threatLevel.textContent = 'CRITICAL';
            threatLevel.className = 'value danger';

            if (!wasWarning) {
                wasWarning = true;
                addLog('CRITICAL: Drone breached restricted perimeter!', true);
            }
        } else {
            alertBox.classList.remove('active');
            threatLevel.textContent = 'NOMINAL';
            threatLevel.className = 'value success';

            if (wasWarning) {
                wasWarning = false;
                addLog('STATUS: Restricted perimeter secured. Drone exited area.', false);
            }
        }
    } catch (error) {
        console.error("Error fetching status", error);
    }
}, 500);
