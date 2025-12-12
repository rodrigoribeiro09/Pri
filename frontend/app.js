// Configuration
const USE_PROXY = true; // Set to true to use Flask proxy (recommended)
const SOLR_BASE_URL = 'http://localhost:8983/solr';
const API_BASE_URL = '/api'; // Flask proxy endpoint

// System configurations matching the Python script logic
const SYSTEMS = {
    'simple-simple': {
        core: 'simple',
        queryType: 'simple'
    },
    'songs-simple': {
        core: 'songs',
        queryType: 'simple'
    },
    'songs-enhanced': {
        core: 'songs',
        queryType: 'enhanced'
    },
    'semantic-simple': {
        core: 'semantic',
        queryType: 'simple'
    },
    'boosted-enhanced': {
        core: 'boosted',
        queryType: 'enhanced'
    }
};

async function searchSongs() {
    const query = document.getElementById('searchInput').value.trim();
    const systemKey = document.getElementById('searchSystem').value;
    const system = SYSTEMS[systemKey];
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    showLoading(true);
    
    try {
        const params = buildSolrParams(system, query);
        
        let data;
        if (USE_PROXY) {
            // Use Flask proxy to avoid CORS issues
            data = await searchViaProxy(system.core, params);
        } else {
            // Direct Solr access (may have CORS issues)
            data = await searchDirectly(system.core, params);
        }
        
        displayResults(data.response.docs, system);
    } catch (error) {
        console.error('Error searching:', error);
        document.getElementById('results').innerHTML = `
            <div class="error-message">
                <strong>Error performing search.</strong><br>
                ${USE_PROXY ? 
                    'Make sure the Flask server is running and Solr is accessible.' :
                    `Make sure Solr is running at ${SOLR_BASE_URL}`
                }<br>
                Erro: ${error.message}
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

async function searchViaProxy(core, params) {
    const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            core: core,
            params: params
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

async function searchDirectly(core, params) {
    const solrUrl = `${SOLR_BASE_URL}/${core}/select`;
    
    const response = await fetch(solrUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(params)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

function buildSolrParams(system, query) {
    // Base parameters
    const params = {
        'wt': 'json',
        'rows': '10',
        'fl': '*,score'
    };
    
    if (system.core === 'boosted' && system.queryType === 'enhanced') {
        // Hybrid search (boosted + enhanced)
        // This requires backend support for embeddings, so we'll use simplified version
        params['q'] = query;
        params['defType'] = 'edismax';
        params['qf'] = 'song_lyrics^4 song_name^2 artist_name^1 artist_bio^2 album_name^1 artist_nationality^20 song_genre^20';
        params['pf'] = 'song_lyrics^2 song_name^1 artist_bio^2';
        params['pf2'] = 'song_lyrics^2 song_name^1 artist_bio^2';
        params['pf1'] = 'artist_bio^3 artist_nationality^10 song_genre^10';
        params['ps'] = '3';
        params['ps2'] = '2';
        params['mm'] = '75%';
        params['tie'] = '0.1';
    } else if (system.core === 'semantic') {
        // Semantic search
        // Note: This requires embedding support, fallback to basic search
        params['q'] = query;
        params['defType'] = 'edismax';
        params['qf'] = 'song_lyrics song_name artist_name artist_bio album_name';
    } else {
        // Simple or Enhanced queries for other cores
        params['q'] = query;
        params['defType'] = 'edismax';
        params['qf'] = 'song_lyrics song_name artist_name artist_bio album_name';
        
        if (system.queryType === 'enhanced') {
            // Enhanced configuration
            params['qf'] = 'song_lyrics^5 song_name^3 artist_name^2 artist_bio^2 album_name^1';
            params['pf'] = 'song_lyrics^10 song_name^5';
            params['pf2'] = 'song_lyrics^7 song_name^3 artist_bio^1';
            params['pf1'] = 'song_lyrics^2 song_name^1 artist_bio^1';
            params['ps'] = '3';
            params['ps2'] = '2';
            params['mm'] = '75%';
            params['tie'] = '0.1';
        }
    }
    
    return params;
}

function displayResults(docs, system) {
    const resultsDiv = document.getElementById('results');
    
    if (!docs || docs.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h2>No results found</h2>
                <p>Try adjusting your search or using a different search system.</p>
            </div>
        `;
        return;
    }
    
    const systemName = getSystemName(system);
    let html = `<h2>Top ${Math.min(docs.length, 10)} Results - ${systemName}</h2>`;
    
    docs.forEach((doc, index) => {
        const songName = extractValue(doc.song_name);
        const artistName = extractValue(doc.artist_name);
        const score = doc.score ? doc.score.toFixed(4) : 'N/A';
        
        html += `
            <div class="song-item" onclick="toggleDetails('song-${index}')">
                <div class="song-header">
                    <div class="song-info">
                        <div class="song-title">${escapeHtml(songName || 'Unknown Title')}</div>
                        <div class="song-artist">by ${escapeHtml(artistName || 'Unknown Artist')}</div>
                    </div>
                    <div class="song-score">Score: ${score}</div>
                </div>
                <div id="song-${index}" class="song-details">
                    ${buildDetailsHtml(doc)}
                </div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

function buildDetailsHtml(doc) {
    let html = '<div>';
    
    const fields = [
        { key: 'album_name', label: 'Album' },
        { key: 'song_genre', label: 'Genre' },
        { key: 'artist_nationality', label: 'Artist Nationality' },
        { key: 'song_lyrics', label: 'Lyrics (preview)', preview: true },
        { key: 'artist_bio', label: 'Artist Bio (preview)', preview: true }
    ];
    
    fields.forEach(field => {
        const value = extractValue(doc[field.key]);
        if (value) {
            let displayValue = value;
            if (field.preview && value.length > 300) {
                displayValue = value.substring(0, 300) + '...';
            }
            html += `
                <div class="detail-row">
                    <span class="detail-label">${field.label}:</span>
                    <span class="detail-value">${escapeHtml(displayValue)}</span>
                </div>
            `;
        }
    });
    
    // Add ID for reference
    if (doc.id) {
        html += `
            <div class="detail-row">
                <span class="detail-label">ID:</span>
                <span class="detail-value">${escapeHtml(doc.id)}</span>
            </div>
        `;
    }
    
    html += '</div>';
    return html || '<p>Sem informação adicional disponível.</p>';
}

function extractValue(field) {
    if (Array.isArray(field)) {
        return field.join(', ');
    }
    return field || '';
}

function toggleDetails(id) {
    const element = document.getElementById(id);
    element.classList.toggle('show');
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    document.getElementById('results').style.display = show ? 'none' : 'block';
}

function getSystemName(system) {
    const names = {
        'simple-simple': 'Simple Core + Simple Query',
        'songs-simple': 'Songs Core + Simple Query',
        'songs-enhanced': 'Songs Core + Enhanced Query',
        'semantic-simple': 'Semantic Core + Simple Query',
        'boosted-enhanced': 'Boosted Core + Enhanced Query'
    };
    
    const key = Object.keys(SYSTEMS).find(k => 
        SYSTEMS[k].core === system.core && SYSTEMS[k].queryType === system.queryType
    );
    
    return names[key] || 'Unknown System';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow search on Enter key
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchSongs();
        }
    });
});
