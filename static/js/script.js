// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

// Check for saved theme preference or use system preference
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
const savedTheme = localStorage.getItem('theme');

if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme.matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeIcon.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
});

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function getTranscript() {
    const url = document.getElementById('youtubeUrl').value;
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    // Show loading indicator
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('transcriptContainer').style.display = 'none';
    document.getElementById('chaptersContainer').style.display = 'none';
    document.getElementById('chunksContainer').style.display = 'none';

    // Send request to server
    fetch('/get_transcript', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        
        if (data.error) {
            showError(data.error);
            return;
        }

        if (data.success) {
            if (data.transcript) {
                displayTranscript(data.transcript);
                document.getElementById('transcriptContainer').style.display = 'block';
            }
            if (data.chapters && data.chapters.length > 0) {
                displayChapters(data.chapters);
                document.getElementById('chaptersContainer').style.display = 'block';
            }
            if (data.transcript_chunks && data.transcript_chunks.length > 0) {
                displayChunks(data.transcript_chunks);
            }
        }
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        showError('An error occurred while fetching the transcript');
        console.error('Error:', error);
    });
}

function displayTranscript(transcript) {
    const container = document.getElementById('transcriptContainer');
    container.innerHTML = ''; // Clear previous content
    const lines = transcript.split('\n');
    
    lines.forEach(line => {
        if (line.trim()) {
            const div = document.createElement('div');
            div.className = 'transcript-line';
            div.textContent = line;
            container.appendChild(div);
        }
    });
}

function displayChapters(chapters) {
    const container = document.getElementById('chaptersContainer');
    const content = document.getElementById('chaptersContent');
    content.innerHTML = '';
    
    chapters.forEach(chapter => {
        const div = document.createElement('div');
        div.className = 'chapter-item';
        div.innerHTML = `
            <span class="chapter-time">${formatTime(chapter.time)}</span>
            <span class="chapter-title">${chapter.title}</span>
        `;
        div.onclick = () => {
            // Find the transcript line closest to this chapter time
            const transcriptLines = document.querySelectorAll('.transcript-line');
            let closestLine = null;
            let minDiff = Infinity;
            
            transcriptLines.forEach(line => {
                const timeMatch = line.textContent.match(/^(\d{1,2}:\d{2}(?::\d{2})?)/);
                if (timeMatch) {
                    const timeStr = timeMatch[1];
                    const [minutes, seconds] = timeStr.split(':').map(Number);
                    const lineTime = minutes * 60 + seconds;
                    const diff = Math.abs(lineTime - chapter.time);
                    
                    if (diff < minDiff) {
                        minDiff = diff;
                        closestLine = line;
                    }
                }
            });
            
            if (closestLine) {
                closestLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
                closestLine.style.backgroundColor = 'var(--highlight-bg)';
                setTimeout(() => {
                    closestLine.style.backgroundColor = '';
                }, 2000);
            }
        };
        content.appendChild(div);
    });
    
    container.style.display = 'block';
}

function displayChunks(chunks) {
    const container = document.getElementById('chunksContainer');
    const content = document.getElementById('chunksContent');
    content.innerHTML = '';
    
    chunks.forEach((chunk, index) => {
        const section = document.createElement('div');
        section.className = 'chunk-section';
        section.id = `chunk-${index}`;
        
        // Create header with toggle button
        const header = document.createElement('div');
        header.className = 'chunk-header';
        
        const title = document.createElement('h4');
        title.className = 'chapter-title';
        title.textContent = chunk.chapter;
        
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'btn btn-sm btn-outline-secondary toggle-chunk';
        toggleBtn.innerHTML = '<span class="toggle-icon">▼</span>';
        toggleBtn.setAttribute('aria-expanded', 'true');
        toggleBtn.onclick = function() {
            const content = this.closest('.chunk-section').querySelector('.chunk-content');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            if (isExpanded) {
                content.style.display = 'none';
                this.setAttribute('aria-expanded', 'false');
                this.querySelector('.toggle-icon').textContent = '▶';
            } else {
                content.style.display = 'block';
                this.setAttribute('aria-expanded', 'true');
                this.querySelector('.toggle-icon').textContent = '▼';
            }
        };
        
        header.appendChild(title);
        header.appendChild(toggleBtn);
        section.appendChild(header);
        
        // Create content container
        const contentDiv = document.createElement('div');
        contentDiv.className = 'chunk-content';
        
        // Create main points section
        if (chunk.main_points && chunk.main_points.length > 0) {
            const mainPointsDiv = document.createElement('div');
            mainPointsDiv.className = 'analysis-section';
            
            const mainPointsTitle = document.createElement('h5');
            mainPointsTitle.textContent = 'Main Points:';
            mainPointsDiv.appendChild(mainPointsTitle);
            
            const mainPointsList = document.createElement('ul');
            chunk.main_points.forEach(point => {
                const li = document.createElement('li');
                li.textContent = point;
                mainPointsList.appendChild(li);
            });
            mainPointsDiv.appendChild(mainPointsList);
            contentDiv.appendChild(mainPointsDiv);
        }
        
        // Create related topics section
        if (chunk.related_topics && chunk.related_topics.length > 0) {
            const topicsDiv = document.createElement('div');
            topicsDiv.className = 'analysis-section';
            
            const topicsTitle = document.createElement('h5');
            topicsTitle.textContent = 'Related Topics:';
            topicsDiv.appendChild(topicsTitle);
            
            const topicsList = document.createElement('ul');
            chunk.related_topics.forEach(topic => {
                const li = document.createElement('li');
                li.textContent = topic;
                topicsList.appendChild(li);
            });
            topicsDiv.appendChild(topicsList);
            contentDiv.appendChild(topicsDiv);
        }
        
        // Create collapsible transcript text section
        const transcriptToggle = document.createElement('button');
        transcriptToggle.className = 'btn btn-sm btn-outline-secondary mt-3';
        transcriptToggle.textContent = 'Show Transcript';
        transcriptToggle.onclick = function() {
            const textDiv = this.nextElementSibling;
            if (textDiv.style.display === 'none') {
                textDiv.style.display = 'block';
                this.textContent = 'Hide Transcript';
            } else {
                textDiv.style.display = 'none';
                this.textContent = 'Show Transcript';
            }
        };
        contentDiv.appendChild(transcriptToggle);
        
        const textDiv = document.createElement('div');
        textDiv.className = 'chunk-text';
        textDiv.style.display = 'none'; // Hidden by default
        const lines = chunk.text.split('\n');
        lines.forEach(line => {
            const p = document.createElement('p');
            p.className = 'chunk-line';
            p.textContent = line;
            textDiv.appendChild(p);
        });
        contentDiv.appendChild(textDiv);
        
        section.appendChild(contentDiv);
        content.appendChild(section);
    });
    
    container.style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
} 