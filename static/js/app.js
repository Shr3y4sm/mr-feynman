function initApp() {
    const form = document.getElementById('feynmanForm');
    if (!form) return; 

    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingIcon = document.getElementById('loadingIcon');
    const arrowIcon = document.getElementById('arrowIcon');
    const buttonText = analyzeBtn.querySelector('span');
    const resultsSection = document.getElementById('resultsSection');

    // Phase 2 State
    let currentSourceText = null;
    let lastAttemptId = null;
    
    // Phase 4 State
    let sessionState = { 
        sessionId: null, 
        turnIndex: 1 
    };

    // Robust State Sync: Watch for mode changes from inline script
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === "attributes" && mutation.attributeName === "data-purpose") {
                const newMode = document.body.getAttribute('data-purpose');
                console.log("App.js: Mode switched to", newMode);
                // Reset session when switching modes to ensure clean slate
                sessionState = { sessionId: null, turnIndex: 1 };
                
                // Optional: Clear previous results or show a toast
                const guidance = document.getElementById('guidanceMessage');
                if(guidance && newMode === 'interview') {
                   // Pre-prompt guidance for interview
                   const p = document.getElementById('guidanceText');
                   if(p) p.textContent = "The AI will challenge your understanding.";
                }
            }
        });
    });
    
    observer.observe(document.body, {
        attributes: true, 
        attributeFilter: ["data-purpose"]
    });
    
    // Note: Mode UI switching is now handled by inline script in index.html due to timing issues.
    // We will read the 'data-purpose' attribute from document.bodyPayload when submitting.
    // --- Phase 2: PDF Upload Logic ---
    const pdfUpload = document.getElementById('pdfUpload');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadBtnText = document.getElementById('uploadBtnText');
    
    // New UX Elements
    const guidanceMessage = document.getElementById('guidanceMessage');
    const contextBadge = document.getElementById('contextBadge');

    pdfUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // UI Feedback: Loading state
        uploadBtnText.textContent = "Ingesting...";
        uploadBtn.classList.add('opacity-70', 'cursor-wait');
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v2/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                currentSourceText = data.text; // Store in memory
                
                // 1. Visual Acknowledgement (Button) - Persistent state
                uploadBtnText.textContent = "✔ Source material added";
                uploadBtn.classList.remove('opacity-70', 'cursor-wait', 'text-textMuted');
                uploadBtn.classList.add('text-primary', 'border-primary', 'bg-primary/10');
                
                // 2. Inline Guidance Update
                const guidanceText = document.getElementById('guidanceText');
                if (guidanceText) {
                    guidanceText.textContent = "Your explanation will be checked against the uploaded material.";
                }
                guidanceMessage.classList.remove('hidden');
                
                // 3. Context Badge
                const contextBadge = document.getElementById('contextBadge');
                if (contextBadge) { 
                    contextBadge.classList.remove('hidden');
                }
                
                // Optional: Focus the concept input to encourage starting
                setTimeout(() => document.getElementById('concept').focus(), 500);

            } else {
                throw new Error(data.detail || "Upload failed");
            }
        } catch (err) {
            console.error(err);
            uploadBtnText.textContent = "Upload Failed";
            uploadBtn.classList.remove('opacity-70', 'cursor-wait');
            uploadBtn.classList.add('text-red-500', 'border-red-500');
            
            setTimeout(() => {
                uploadBtnText.textContent = "Add Source Material (PDF)";
                uploadBtn.classList.remove('text-red-500', 'border-red-500');
            }, 3000);
        }
    });

    // --- Phase 2: History Logic ---
    const toggleHistoryBtn = document.getElementById('toggleHistoryBtn');
    const historyPanel = document.getElementById('historyPanel');
    const historyList = document.getElementById('historyList');

    toggleHistoryBtn.addEventListener('click', async () => {
        const isHidden = historyPanel.classList.contains('hidden');
        if (isHidden) {
            historyPanel.classList.remove('hidden');
            toggleHistoryBtn.textContent = "Hide past explanations";
            await loadHistory();
        } else {
            historyPanel.classList.add('hidden');
            toggleHistoryBtn.textContent = "Show past explanations";
        }
    });

    async function loadHistory() {
        try {
            const res = await fetch('/api/v1/history');
            const attempts = await res.json();
            
            historyList.innerHTML = '';
            if (attempts.length === 0) {
                historyList.innerHTML = '<li class="italic opacity-50">No attempts yet.</li>';
                return;
            }

            attempts.forEach(attempt => {
                const li = document.createElement('li');
                li.className = "flex justify-between items-center p-2 hover:bg-background rounded cursor-pointer transition-colors group";
                const date = new Date(attempt.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                li.innerHTML = `
                    <span>${attempt.concept} <span class="text-xs opacity-50 ml-1">(${date})</span></span>
                    <span class="text-xs opacity-0 group-hover:opacity-100 text-primary">Load →</span>
                `;
                li.onclick = () => {
                    document.getElementById('concept').value = attempt.concept;
                    document.getElementById('explanation').value = attempt.explanation_text;
                    // Trigger "Previous ID" tracking logic for Phase 2 comparison
                    lastAttemptId = attempt.attempt_id;
                    window.scrollTo({top: 0, behavior: 'smooth'});
                    
                    // Show a subtle hint
                    // We reuse the guidance message area for simplicity, or create a temporary toast if we had one.
                    // Let's modify the Primary Guidance text temporarily or add a status message.
                    const guide = document.getElementById('guidanceMessage');
                    if(guide) {
                        guide.classList.remove('hidden');
                        const p = guide.querySelector('p:last-child');
                        if(p) p.textContent = "Loaded a previous explanation — you can revise it.";
                        // Hide the specific PDF icon part if needed, but keeping it simple is better for now.
                        guide.querySelector('.text-primary').innerHTML = '<span>↺</span>'; // Simple icon swap
                    }
                };
                historyList.appendChild(li);
            });

        } catch (e) { console.error("History load failed", e); }
    }


    // --- Phase 3: Speech to Text Logic ---
    const micBtn = document.getElementById('micBtn');
    const micText = document.getElementById('micText');
    const explanationInput = document.getElementById('explanation');
    
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    // Metrics State
    let speechMetrics = {
        startTime: 0,
        totalDuration: 0,
        activeDuration: 0,
        currentActiveStart: 0
    };
    
    // Explicit Input Mode: "text" | "speech"
    let inputMode = "text";

    if (SpeechRecognition && micBtn) {
        micBtn.classList.remove('hidden');
        const recognition = new SpeechRecognition();
        
        // Toggle Logic: continuous allows user to control stop
        recognition.continuous = true; 
        recognition.interimResults = true; // Changed to partial updates for better UX
        recognition.lang = 'en-US';

        let isListening = false;
        let finalTranscript = '';

        // Helpers
        const resetMetrics = () => {
            speechMetrics = {
                startTime: Date.now(),
                totalDuration: 0,
                activeDuration: 0,
                currentActiveStart: 0
            };
            inputMode = "speech"; // Explicitly set to speech mode
        };

        const updateButtonState = (listening) => {
            if (listening) {
                micText.textContent = "Stop Recording";
                micBtn.classList.add('animate-pulse', 'text-red-500');
            } else {
                micText.textContent = "Explain by speaking";
                micBtn.classList.remove('animate-pulse', 'text-red-500');
            }
            micBtn.disabled = false;
        };

        // Click Handler (Toggle)
        micBtn.addEventListener('click', () => {
             if (isListening) {
                 // User manual stop
                 recognition.stop();
                 // Duration calc happens in onend
             } else {
                 // Start
                 try {
                     finalTranscript = explanationInput.value; // Snapshot current text to append to
                     resetMetrics();
                     recognition.start();
                     isListening = true;
                     updateButtonState(true);
                 } catch (err) {
                     console.error("Speech start error", err);
                     isListening = false;
                     updateButtonState(false);
                 }
             }
        });

        // Metrics Tracking
        recognition.onspeechstart = () => {
            speechMetrics.currentActiveStart = Date.now();
        };

        recognition.onspeechend = () => {
            if (speechMetrics.currentActiveStart > 0) {
                speechMetrics.activeDuration += (Date.now() - speechMetrics.currentActiveStart);
                speechMetrics.currentActiveStart = 0;
            }
        };

        recognition.onend = () => {
             if (isListening) {
                 // Calculate final total time
                 speechMetrics.totalDuration = Date.now() - speechMetrics.startTime;
                 
                 // Handle active time edge case (if stopped while speaking)
                 if (speechMetrics.currentActiveStart > 0) {
                     speechMetrics.activeDuration += (Date.now() - speechMetrics.currentActiveStart);
                 }
             }

             isListening = false;
             updateButtonState(false);
             
             // Show helpful text if we actually recorded something
             if (speechMetrics.totalDuration > 1000) {
                micText.textContent = "You can edit the text before analyzing";
                setTimeout(() => {
                    if(!isListening && micText.textContent === "You can edit the text before analyzing") {
                        micText.textContent = "Explain by speaking";
                    }
                }, 4000);
             }
        };

        recognition.onresult = (event) => {
             let interim = '';
             let final = '';

             for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    final += event.results[i][0].transcript;
                } else {
                    interim += event.results[i][0].transcript;
                }
             }

             // Append to what was there before recording started
             // Simple spacing logic
             const existing = finalTranscript;
             const prefix = (existing && !existing.endsWith(' ') && !existing.endsWith('\n')) ? ' ' : '';
             
             // Update UI live
             // Identify if we are appending or replacing the 'interim' part
             // Simplest approach: Just update value with (Base + Final + Interim)
             // Note: event.results accumulates in continuous mode usually, 
             // but we need to manage the text cursor carefully.
             // Strategy: Just rewrite the tail.
             
             // Actually, continuous mode accumulates results in event.results.
             // We can just reconstruct the whole *new* segment.
             
             let newTranscript = '';
             for (let i = 0; i < event.results.length; ++i) {
                 newTranscript += event.results[i][0].transcript;
             }
             
             explanationInput.value = existing + prefix + newTranscript;
             explanationInput.scrollTop = explanationInput.scrollHeight;
             explanationInput.dispatchEvent(new Event('input'));
        };

        recognition.onerror = (event) => {
             console.error("Speech error", event.error);
             isListening = false;
             updateButtonState(false);
        };
    }

    // Simple interaction: Auto-expand textarea
    const textarea = document.getElementById('explanation');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        // Update char count if needed
        const count = this.value.length;
        // Fix for new specific DOM structure (div wrapper)
        const counter = this.parentElement.querySelector('p.text-right');
        if (counter) counter.textContent = `${count} / 2000 chars`;
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Data
        const concept = document.getElementById('concept').value;
        const audience = document.getElementById('audience').value;
        const explanation = document.getElementById('explanation').value;

        if(!concept || !explanation) return;

        // UI State: Loading
        setLoading(true);
        resultsSection.classList.add('hidden');

        try {
            // Prepare Speech Metrics (Phase 3)
            let durationPayload = null;
            if (inputMode === "speech" && typeof speechMetrics !== 'undefined' && speechMetrics.totalDuration > 0) {
                 durationPayload = {
                     total_seconds: Math.round(speechMetrics.totalDuration / 1000),
                     active_seconds: Math.round(speechMetrics.activeDuration / 1000)
                 };
            }

            // Phase 4: Get Purpose from Attribute set by Inline Script
            const currentPurpose = document.body.getAttribute('data-purpose') || 'learning';
            console.log("Preparing analysis request. Purpose:", currentPurpose);
            
            // Loop Logic: Only send session ID if in interview mode
            const sessionPayload = (currentPurpose === 'interview') ? {
                session_id: sessionState.sessionId,
                turn_index: sessionState.turnIndex
            } : {};

            // API Call (Updated for Phase 2, 3 & 4)
            const payload = {
                concept: concept,
                explanation: explanation,
                target_audience: audience,
                source_text: currentSourceText, // Pass if loaded
                previous_attempt_id: lastAttemptId, // Pass if revision
                input_mode: inputMode, // Source of truth
                speaking_duration: durationPayload, // Phase 3: Metrics
                purpose: currentPurpose, // Phase 4: Learning vs Interview
                ...sessionPayload
            };
            
            console.log("Request Payload:", payload);

            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Analysis failed');

            const data = await response.json();
            
            // Phase 2: Update last id to form a chain
            if (data.attempt_id) {
                lastAttemptId = data.attempt_id;
            }

            // Phase 4b: Handle Turn Logic
            console.log("Response Data:", data);
            
            if (data.session_id) {
                sessionState.sessionId = data.session_id;
            }
            
            if (data.interviewer_followup) {
                // Update turn index for next reply
                sessionState.turnIndex = (data.turn_index || sessionState.turnIndex) + 1;
                
                // Show follow-up hint
                 const guide = document.getElementById('guidanceMessage');
                 if(guide) {
                     guide.classList.remove('hidden');
                     // Simple visual hack for turn tracking
                     guide.querySelector('div.text-primary').innerHTML = `<span class="font-bold text-lg">${data.turn_index}/3</span>`;
                     const p = guide.querySelector('p#guidanceText');
                     if(p) p.textContent = `Interviewer follow-up received. Answer below to continue.`;
                 }
            } else if (data.conversation_complete) {
                sessionState = { sessionId: null, turnIndex: 1 }; // Reset
                const guide = document.getElementById('guidanceMessage');
                 if(guide) {
                     guide.classList.remove('hidden');
                     guide.querySelector('div.text-primary').innerHTML = `<span class="font-bold text-lg">✔</span>`;
                     const p = guide.querySelector('p#guidanceText');
                     if(p) p.textContent = `Interview Complete. Great job!`;
                 }
            }

            // Phase 2: Render
            renderResults(data.analysis, data.interviewer_followup);
            renderComparison(data.comparison);
            renderSpeakingMetrics(data.analysis.speaking_metrics);
            renderFillerAnalysis(data.analysis.filler_analysis);

            // Reset flags for next attempt
            inputMode = "text";

        } catch (error) {
            console.error(error);
            // Mock response for UI testing if API fails (e.g. model execution error)
            // Remove checks in production
            renderResults({
                summary: 'We encountered an error connecting to the brain (LLM). Since this is a local environment, looking at the logs might help. However, here is what the UI would look like!',
                gaps: ['Connection to LLM failed', 'Python backend might be missing the model'],
                suggestions: ['Check console logs', 'Ensure GGUF model is in models/'],
                follow_up_questions: ['Did you install the requirements?', 'is uvicorn running?']
            });
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            analyzeBtn.disabled = true;
            buttonText.textContent = 'Analyzing...';
            loadingIcon.classList.remove('hidden');
            arrowIcon.classList.add('hidden');
            analyzeBtn.classList.add('opacity-80', 'cursor-wait');
        } else {
            analyzeBtn.disabled = false;
            buttonText.textContent = 'Analyze Explanation';
            loadingIcon.classList.add('hidden');
            arrowIcon.classList.remove('hidden');
            analyzeBtn.classList.remove('opacity-80', 'cursor-wait');
        }
    }

    function renderComparison(comparisonData) {
        const box = document.getElementById('comparisonBox');
        const text = document.getElementById('progressText');
        const list = document.getElementById('improvementsList');
        
        // Update header if exists, though we hardcoded it in HTML now.
        // But logic check remains.
        
        if (!comparisonData || comparisonData.summary_of_progress === "Unable to generate comparison.") {
            box.classList.add('hidden');
            return;
        }

        text.textContent = comparisonData.summary_of_progress;
        list.innerHTML = '';
        
        // Show improvements
        if (comparisonData.improvements && comparisonData.improvements.length > 0) {
            comparisonData.improvements.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `✓ ${item}`;
                list.appendChild(li);
            });
        }
        
        // Optionally show remaining gaps here if desired, 
        // but they are usually covered by the main "Gaps" card.
        
        box.classList.remove('hidden');
    }

    function renderSpeakingMetrics(metrics) {
        const box = document.getElementById('speakingMetricsBox');
        
        // Defensive cleaner: ensure hidden by default
        box.classList.add('hidden');

        if (!metrics || !metrics.total_time_seconds || metrics.total_time_seconds === 0) {
            return;
        }

        // Metrics
        document.getElementById('metricTotalTime').textContent = `${metrics.total_time_seconds}s`;
        document.getElementById('metricActiveTime').textContent = `${metrics.active_speaking_seconds}s`; // Note: Schema uses active_speaking_seconds
        document.getElementById('metricPauseRatio').textContent = `${Math.round(metrics.pause_ratio * 100)}%`;

        // Insight
        document.getElementById('speakingInsight').textContent = metrics.insight || "No insight available.";

        // Suggestions
        const list = document.getElementById('speakingSuggestions');
        list.innerHTML = '';
        if (metrics.suggestions && metrics.suggestions.length > 0) {
            metrics.suggestions.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `✓ ${item}`;
                list.appendChild(li);
            });
        }

        box.classList.remove('hidden');
    }

    function renderFillerAnalysis(fillers) {
        const box = document.getElementById('fillerBox');
        if (!fillers || fillers.total_filler_count === 0) {
            box.classList.add('hidden');
            return;
        }

        document.getElementById('fillerCount').textContent = fillers.total_filler_count;
        document.getElementById('commonFillers').textContent = (fillers.common_fillers || []).join(', ');
        document.getElementById('fillerInsight').textContent = fillers.insight || "Consider reducing filler words.";

        box.classList.remove('hidden');
    }

    function renderResults(data, followup=null) {
        // Update Feedback Framing based on context
        const framing = document.getElementById('feedbackFraming');
        if (framing) {
             if (followup) {
                 framing.textContent = "INTERVIEWER FOLLOW-UP";
                 framing.className = "text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500";
             } else if (currentSourceText) {
                framing.textContent = "This feedback is based on your explanation and the material you uploaded.";
                framing.className = "text-sm text-textMuted";
             } else {
                framing.textContent = "This feedback is based on your explanation.";
                framing.className = "text-sm text-textMuted";
             }
        }

        // Phase 4: Prioritize Follow-Up Question if present
        const summaryElement = document.getElementById('summaryText');
        if (followup && followup.question) {
             const followupHtml = `
                <div class="p-4 bg-[rgba(255,104,3,0.1)] border border-primary rounded-xl mb-4 animate-pulse-slow">
                    <h4 class="text-primary font-bold mb-2 uppercase text-xs tracking-wider">Interviewer Follow-up</h4>
                    <p class="text-white text-lg font-medium">"${followup.question}"</p>
                    <p class="text-sm text-textMuted mt-2 italic">Intent: ${followup.intent}</p>
                </div>
             `;
             summaryElement.innerHTML = followupHtml + `<p class="opacity-80">${data.summary}</p>`;
        } else {
            summaryElement.textContent = data.summary;
        }

        // Helper to create cards
        if (followup && followup.question) {
             const followupHtml = `
                <div class="p-4 bg-[rgba(255,104,3,0.1)] border border-primary rounded-xl mb-4 animate-pulse-slow">
                    <h4 class="text-primary font-bold mb-2 uppercase text-xs tracking-wider">Interviewer Follow-up</h4>
                    <p class="text-white text-lg font-medium">"${followup.question}"</p>
                    <p class="text-sm text-textMuted mt-2 italic">Intent: ${followup.intent}</p>
                </div>
             `;
             summaryElement.innerHTML = followupHtml + `<p class="opacity-80">${data.summary}</p>`;
        } else {
            summaryElement.textContent = data.summary;
        }

        // Helper to create cards
        const createCard = (text, bgClass = 'bg-surface') => {
            const div = document.createElement('div');
            div.className = `${bgClass} p-5 rounded-2xl border border-border text-gray-300 text-base leading-relaxed animate-fade-in-up`;
            div.textContent = text;
            return div;
        };

        // Gaps
        const gapsContainer = document.getElementById('gapsList');
        gapsContainer.innerHTML = '';
        (data.gaps || []).forEach(gap => gapsContainer.appendChild(createCard(gap, 'bg-[#1A0F0A]'))); // Subtle red tint bg if desired, keeping dark for now

        // Suggestions
        const suggestionsContainer = document.getElementById('suggestionsList');
        suggestionsContainer.innerHTML = '';
        (data.suggestions || []).forEach(sug => suggestionsContainer.appendChild(createCard(sug)));

        // Questions
        const questionsContainer = document.getElementById('questionsList');
        questionsContainer.innerHTML = '';
        (data.follow_up_questions || []).forEach(q => {
            const div = document.createElement('div');
            div.className = 'bg-background p-4 rounded-xl border border-border border-l-4 border-l-primary/50 text-gray-300 italic hover:border-l-primary transition-colors cursor-help';
            div.textContent = `"${q}"`;
            questionsContainer.appendChild(div);
        });

        // Reveal
        resultsSection.classList.remove('hidden');
        
        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// Initialize application
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
