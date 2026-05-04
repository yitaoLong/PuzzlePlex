const socket = io();
const tabBar = document.getElementById('tab-bar');
const chatContainer = document.getElementById('chat-container');
const chatWrapper = document.getElementById('chat-wrapper');
const statsContainer = document.getElementById('stats-container');

let activeRoom = null;
let rooms = [];
let globalStats = [];

socket.on('connect', () => {
    console.log('Connected to server');
    fetchRooms();
    fetchStats();
    fetchPuzzle();
});

socket.on('new_message', (data) => {
    console.log('New message received:', data);
    const room = rooms.find(r => r.type === data.receiver);
    if (room) {
        room.messages.push(data.message);
        if (activeRoom === data.receiver) {
            appendMessage(data.message);
            scrollToBottom();
        }
    }
});

socket.on('stats_update', (stats) => {
    updateStatsDisplay(stats);
});

function fetchRooms() {
    fetch('/api/rooms')
        .then(response => response.json())
        .then(fetchedRooms => {
            rooms = Array.isArray(fetchedRooms) ? fetchedRooms : Object.values(fetchedRooms);
            tabBar.innerHTML = ''; // Clear existing tabs
            rooms.forEach((room) => {
                createTabElement(room.id, room);
            });
            if (rooms.length > 0) {
                switchRoom(rooms[0].id);
            }
        })
        .catch(error => console.error('Error fetching rooms:', error));
}

function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            updateStatsDisplay(stats);
        });
}

function fetchPuzzle() {
    fetch('/api/puzzle')
        .then(response => response.json())
        .then(puzzle => {
            const puzzleContainer = document.getElementById('puzzle-container');
            const puzzleDiv = document.createElement('div');
            puzzleDiv.className = 'puzzle';
            puzzleDiv.textContent = puzzle;
            puzzleContainer.appendChild(puzzleDiv);
        });
}

function createTabElement(roomId, roomData) {
    const tabDiv = document.createElement('div');
    tabDiv.className = 'tab';
    tabDiv.textContent = `${roomData.type}`;
    tabDiv.onclick = () => switchRoom(roomId);
    tabBar.appendChild(tabDiv);
}

function switchRoom(roomId) {
    console.log('Switching room:', roomId);
    tabBar.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    
    const room = rooms.find(r => r.id === roomId);
    if (room) {
        const tabDiv = Array.from(tabBar.children).find(tab => tab.textContent.includes(room.type));
        if (tabDiv) {
            tabDiv.classList.add('active');
        }
        activeRoom = room.type;
        displayRoom(roomId);
    }
}

function displayRoom(roomId) {
    chatContainer.innerHTML = ''; // Clear previous messages

    const roomData = rooms.find(r => r.id === roomId);
    if (roomData && roomData.messages) {
        roomData.messages.forEach(message => {
            appendMessage(message);
        });
    }
    scrollToBottom();
}

function appendMessage(data) {
    const messageDiv = createMessageElement(data);
    chatContainer.appendChild(messageDiv);
}

function createMessageElement(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';

    const roleSpan = document.createElement('span');
    roleSpan.className = 'role';
    roleSpan.textContent = data.role;
    messageDiv.appendChild(roleSpan);

    data.components.forEach(component => {
        if (component.type === 'text') {
            const textP = document.createElement('div');
            textP.innerHTML = component.content;
            messageDiv.appendChild(textP);
        } else if (component.type === 'image') {
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${component.content}`;
            img.onload = scrollToBottom; // Scroll after image loads
            messageDiv.appendChild(img);
        }
    });

    return messageDiv;
}

function updateStatsDisplay(stats) {
    globalStats = stats;
    const statsContainer = document.getElementById('stats-container');
    statsContainer.innerHTML = '';
    stats.forEach(stat => {
        const statItem = document.createElement('div');
        statItem.className = 'stat-item';
        statItem.textContent = `${stat.type}: ${stat.value}`;
        statsContainer.appendChild(statItem);
    });
}

function scrollToBottom() {
    chatWrapper.scrollTop = chatWrapper.scrollHeight;
}

// Observe changes in the chat container
const observer = new MutationObserver(scrollToBottom);
observer.observe(chatContainer, { childList: true, subtree: true });