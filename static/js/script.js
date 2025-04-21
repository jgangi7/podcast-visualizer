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
    document.getElementById('transcriptSection').style.display = 'none';
    document.getElementById('chaptersContainer').style.display = 'none';
    document.getElementById('chunksContainer').style.display = 'none';
    document.getElementById('flowChartContainer').style.display = 'none';

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
                generateFlowChart(data.transcript_chunks);
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
    const section = document.getElementById('transcriptSection');
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

    // Show the transcript section
    section.style.display = 'block';
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

function generateFlowChart(chunks) {
    // Send chunks to backend to generate flow chart
    fetch('/generate_flow_chart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chunks: chunks })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display the flow chart
            const container = document.getElementById('flowChartContainer');
            const content = document.getElementById('flowChartContent');
            
            // Load the SVG file
            fetch(data.svg_path)
                .then(response => response.text())
                .then(svg => {
                    content.innerHTML = svg;
                    container.style.display = 'block';
                    
                    // Initialize SVG Pan Zoom
                    const panZoom = svgPanZoom(content.querySelector('svg'), {
                        zoomEnabled: true,
                        controlIconsEnabled: false,
                        fit: true,
                        center: true,
                        minZoom: 0.1,
                        maxZoom: 10,
                        zoomScaleSensitivity: 0.5
                    });
                    
                    // Store initial state after first fit
                    const initialState = {
                        zoom: panZoom.getZoom(),
                        pan: panZoom.getPan()
                    };
                    
                    // Add event listeners for zoom controls
                    document.getElementById('zoomIn').addEventListener('click', () => {
                        const currentZoom = panZoom.getZoom();
                        if (currentZoom < panZoom.getMaxZoom()) {
                            panZoom.zoomIn();
                        }
                    });
                    
                    document.getElementById('zoomOut').addEventListener('click', () => {
                        const currentZoom = panZoom.getZoom();
                        if (currentZoom > initialState.zoom * 0.1) {
                            panZoom.zoomOut();
                        }
                    });
                    
                    document.getElementById('resetZoom').addEventListener('click', () => {
                        // Reset to initial state
                        panZoom.zoom(initialState.zoom);
                        panZoom.pan(initialState.pan.x, initialState.pan.y);
                    });
                    
                    // Handle window resize
                    let resizeTimeout;
                    window.addEventListener('resize', () => {
                        // Clear any existing timeout
                        if (resizeTimeout) {
                            clearTimeout(resizeTimeout);
                        }
                        
                        // Set a new timeout to prevent multiple rapid calls
                        resizeTimeout = setTimeout(() => {
                            panZoom.resize();
                            panZoom.fit();
                            panZoom.center();
                            
                            // Update initial state after resize
                            initialState.zoom = panZoom.getZoom();
                            initialState.pan = panZoom.getPan();
                        }, 250);
                    });
                    
                    // Add export functionality
                    const exportBtn = document.getElementById('exportChart');
                    const youtubeUrl = document.getElementById('youtubeUrl').value;
                    const videoId = youtubeUrl.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)?.[1] || 'chart';
                    
                    // Create and append dropdown
                    const dropdownTemplate = document.getElementById('exportFormatTemplate');
                    const dropdown = dropdownTemplate.content.cloneNode(true);
                    exportBtn.appendChild(dropdown);
                    
                    const exportDropdown = exportBtn.querySelector('.export-dropdown');
                    
                    // Toggle dropdown on button click
                    exportBtn.addEventListener('click', (e) => {
                        if (e.target.closest('.export-format-btn')) return;
                        exportDropdown.classList.toggle('show');
                    });
                    
                    // Close dropdown when clicking outside
                    document.addEventListener('click', (e) => {
                        if (!e.target.closest('.export-btn')) {
                            exportDropdown.classList.remove('show');
                        }
                    });
                    
                    // Handle format selection
                    exportDropdown.addEventListener('click', async (e) => {
                        if (!e.target.classList.contains('export-format-btn')) return;
                        
                        const format = e.target.textContent.toLowerCase();
                        const svg = content.querySelector('svg');
                        const filename = `youtube-${videoId}-flow-chart.${format}`;
                        
                        // Store current pan/zoom state
                        const currentPan = panZoom.getPan();
                        const currentZoom = panZoom.getZoom();
                        
                        // Reset view to show entire chart
                        panZoom.reset();
                        
                        // Temporarily disable pan-zoom for export
                        panZoom.disablePan();
                        panZoom.disableZoom();
                        
                        try {
                            if (format === 'png') {
                                // Get the SVG's dimensions after reset
                                const svgRect = svg.getBoundingClientRect();
                                const viewBox = svg.viewBox.baseVal;
                                
                                // Configure PNG export options for highest quality
                                const options = {
                                    scale: 4, // Increased scale for higher quality
                                    backgroundColor: getComputedStyle(document.documentElement)
                                        .getPropertyValue('--bg-color')
                                        .trim(),
                                    encoderOptions: 1, // Highest quality
                                    width: viewBox.width || svgRect.width * 4, // Use viewBox width if available
                                    height: viewBox.height || svgRect.height * 4, // Use viewBox height if available
                                    left: viewBox.x || 0, // Include full viewBox
                                    top: viewBox.y || 0,
                                    excludeCss: false // Include CSS styles
                                };
                                
                                await saveSvgAsPng(svg, filename, options);
                            } else if (format === 'pdf') {
                                // Create PDF with svg2pdf
                                const { jsPDF } = window.jspdf;
                                const doc = new jsPDF({
                                    orientation: 'landscape',
                                    unit: 'pt',
                                    format: 'a4'
                                });
                                
                                // Get the SVG's original dimensions
                                const viewBox = svg.viewBox.baseVal;
                                const width = viewBox.width || svg.getBoundingClientRect().width;
                                const height = viewBox.height || svg.getBoundingClientRect().height;
                                
                                // Calculate scale to fit PDF page while maintaining aspect ratio
                                const pageWidth = doc.internal.pageSize.getWidth();
                                const pageHeight = doc.internal.pageSize.getHeight();
                                const scale = Math.min(pageWidth / width, pageHeight / height) * 0.95;
                                
                                await doc.svg(svg, {
                                    x: 0,
                                    y: 0,
                                    width: width * scale,
                                    height: height * scale,
                                    viewBox: {
                                        x: viewBox.x || 0,
                                        y: viewBox.y || 0,
                                        width: width,
                                        height: height
                                    }
                                });
                                
                                doc.save(filename);
                            }
                        } catch (error) {
                            console.error(`Error exporting chart as ${format}:`, error);
                        } finally {
                            // Restore previous pan/zoom state
                            panZoom.zoom(currentZoom);
                            panZoom.pan(currentPan);
                            
                            // Re-enable pan-zoom after export
                            panZoom.enablePan();
                            panZoom.enableZoom();
                            exportDropdown.classList.remove('show');
                        }
                    });
                })
                .catch(error => {
                    console.error('Error loading flow chart:', error);
                });
        } else {
            console.error('Error generating flow chart:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    const transcriptSection = document.getElementById('transcriptSection');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    transcriptSection.style.display = 'none';
} 