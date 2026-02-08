const TASK_POOL = {
    "Reading": [
        {"desc": "Solve 10 passages", "time": 40},
        {"desc": "Read 2 academic articles", "time": 30},
        {"desc": "Complete 1 full mock test section", "time": 60},
        {"desc": "Speed read 5 pages", "time": 15},
    ],
    "Writing": [
        {"desc": "Write Task 1 (150 words)", "time": 20},
        {"desc": "Write Task 2 (250 words)", "time": 40},
        {"desc": "Review grammar rules", "time": 15},
        {"desc": "Paraphrase 5 sentences", "time": 10},
    ],
    "Listening": [
        {"desc": "Practice audio quiz", "time": 30},
        {"desc": "Listen to a TED Talk", "time": 15},
        {"desc": "Transcribe 2 mins of audio", "time": 20},
        {"desc": "Full Listening Mock Test", "time": 40},
    ],
    "Speaking": [
        {"desc": "Record 2 minute speech", "time": 10},
        {"desc": "Practice Part 1 questions", "time": 15},
        {"desc": "Describe a picture", "time": 5},
        {"desc": "Shadowing exercise", "time": 20},
    ]
};

let appState = {
    profile: null,
    tasks: [],
    momentum: 0,
    streak: 0,
    completedTasksCount: 0,
    skillStats: {
        Reading: 0,
        Writing: 0,
        Listening: 0,
        Speaking: 0
    },
    lastCompletedDate: null,
    isDemoDataAdded: false
};

let skillChart = null;

const onboardingSection = document.getElementById('onboarding');
const dashboardSection = document.getElementById('dashboard');
const setupForm = document.getElementById('setupForm');
const taskList = document.getElementById('taskList');
const momentumDisplay = document.getElementById('momentumDisplay');
const momentumBar = document.getElementById('momentumBar');
const streakDisplay = document.getElementById('streakDisplay');
const completedDisplay = document.getElementById('completedDisplay');
const daysLeftDisplay = document.getElementById('daysLeftDisplay');
const resetBtn = document.getElementById('resetBtn');
const generateTasksBtn = document.getElementById('generateTasksBtn');
const completionMessage = document.getElementById('completionMessage');

document.addEventListener('DOMContentLoaded', () => {
    loadState();
    if (appState.profile) {
        showDashboard();
    } else {
        showOnboarding();
    }
});

setupForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const profile = {
        targetScore: document.getElementById('targetScore').value,
        examDate: document.getElementById('examDate').value,
        studyTime: document.getElementById('studyTime').value,
        weakSkill: document.getElementById('weakSkill').value
    };
    appState.profile = profile;
    
    generatePastData();
    
    generateTasks();
    saveState();
    showDashboard();
});

resetBtn.addEventListener('click', () => {
    if(confirm("Are you sure you want to reset your profile?")) {
        localStorage.removeItem('studyMomentumState');
        location.reload();
    }
});

generateTasksBtn.addEventListener('click', () => {
    generateTasks();
    updateUI();
});

function showOnboarding() {
    onboardingSection.classList.remove('hidden');
    dashboardSection.classList.add('hidden');
}

function generatePastData() {
    if (appState.isDemoDataAdded) return;

    const skills = ["Reading", "Writing", "Listening", "Speaking"];
    
    for (let i = 0; i < 10; i++) {
        for (let j = 0; j < 3; j++) {
            const skill = skills[Math.floor(Math.random() * skills.length)];
            appState.skillStats[skill]++;
            appState.completedTasksCount++;
        }
    }

    appState.streak = 10;
    appState.momentum = 100;
    
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    appState.lastCompletedDate = yesterday.toDateString();
    
    appState.isDemoDataAdded = true;
}

function showDashboard() {
    onboardingSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    updateUI();
    initChart();
}

function generateTasks() {
    const tasks = [];
    const weakSkill = appState.profile.weakSkill;
    const skills = ["Reading", "Writing", "Listening", "Speaking"];

    const weakTasks = TASK_POOL[weakSkill];
    const t1 = weakTasks[Math.floor(Math.random() * weakTasks.length)];
    tasks.push({ ...t1, skill: weakSkill, completed: false, id: Date.now() + 1 });

    while (tasks.length < 3) {
        const skill = skills[Math.floor(Math.random() * skills.length)];
        const pool = TASK_POOL[skill];
        const t = pool[Math.floor(Math.random() * pool.length)];
        
        if (!tasks.find(task => task.desc === t.desc)) {
            tasks.push({ ...t, skill: skill, completed: false, id: Date.now() + tasks.length + 1 });
        }
    }

    appState.tasks = tasks;
    saveState();
}

function toggleTask(id) {
    const task = appState.tasks.find(t => t.id === id);
    if (task) {
        const wasCompleted = task.completed;
        task.completed = !wasCompleted;
        
        if (task.completed) {
            appState.momentum = Math.min(100, appState.momentum + 5);
            appState.completedTasksCount++;
            appState.skillStats[task.skill]++;
        } else {
            appState.momentum = Math.max(0, appState.momentum - 5);
            appState.completedTasksCount--;
            appState.skillStats[task.skill]--;
        }

        const allCompleted = appState.tasks.every(t => t.completed);
        if (allCompleted && !wasCompleted) {
             appState.momentum = Math.min(100, appState.momentum + 10);
             checkStreak();
        } else if (!allCompleted && wasCompleted && appState.tasks.filter(t => t.completed).length === 2) {
             appState.momentum = Math.max(0, appState.momentum - 10);
        }

        saveState();
        updateUI();
    }
}

function checkStreak() {
    const today = new Date().toDateString();
    if (appState.lastCompletedDate !== today) {
        appState.streak++;
        appState.lastCompletedDate = today;
    }
}

function updateUI() {
    taskList.innerHTML = '';
    let allCompleted = true;

    appState.tasks.forEach(task => {
        if (!task.completed) allCompleted = false;
        const div = document.createElement('div');
        div.className = `task-item ${task.completed ? 'completed' : ''}`;
        div.innerHTML = `
            <input type="checkbox" class="task-checkbox" 
                ${task.completed ? 'checked' : ''} 
                onchange="toggleTask(${task.id})">
            <div class="task-content">
                <span class="task-skill">${task.skill}</span>
                <div class="task-desc">${task.desc}</div>
            </div>
            <span class="task-time">${task.time}m</span>
        `;
        taskList.appendChild(div);
    });

    if (allCompleted && appState.tasks.length > 0) {
        completionMessage.classList.remove('hidden');
    } else {
        completionMessage.classList.add('hidden');
    }

    momentumDisplay.textContent = appState.momentum;
    momentumBar.style.width = `${appState.momentum}%`;
    streakDisplay.textContent = appState.streak;
    completedDisplay.textContent = appState.completedTasksCount;

    if (appState.profile.examDate) {
        const exam = new Date(appState.profile.examDate);
        const today = new Date();
        const diffTime = Math.ceil((exam - today) / (1000 * 60 * 60 * 24)); 
        daysLeftDisplay.textContent = `${diffTime > 0 ? diffTime : 0} days to exam`;
    }

    updateChart();
}

function initChart() {
    const ctx = document.getElementById('skillChart').getContext('2d');
    
    if (skillChart) skillChart.destroy();

    skillChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(appState.skillStats),
            datasets: [{
                label: 'Tasks Completed',
                data: Object.values(appState.skillStats),
                borderColor: '#bb86fc',
                backgroundColor: 'rgba(187, 134, 252, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#03dac6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#ffffff' } }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#333' },
                    ticks: { color: '#b0b0b0', stepSize: 1 }
                },
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#b0b0b0' }
                }
            }
        }
    });
}

function updateChart() {
    if (skillChart) {
        skillChart.data.datasets[0].data = Object.values(appState.skillStats);
        skillChart.update();
    }
}

function saveState() {
    localStorage.setItem('studyMomentumState', JSON.stringify(appState));
}

function loadState() {
    const saved = localStorage.getItem('studyMomentumState');
    if (saved) {
        appState = JSON.parse(saved);
        
        if (appState.profile && !appState.isDemoDataAdded) {
            generatePastData();
            saveState();
        }
    }
}

window.toggleTask = toggleTask;