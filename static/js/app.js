document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('feynmanForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingIcon = document.getElementById('loadingIcon');
    const arrowIcon = document.getElementById('arrowIcon');
    const buttonText = analyzeBtn.querySelector('span');
    const resultsSection = document.getElementById('resultsSection');

    // Simple interaction: Auto-expand textarea
    const textarea = document.getElementById('explanation');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        // Update char count if needed
        const count = this.value.length;
        this.nextElementSibling.textContent = `${count} / 2000 chars`;
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
            // API Call
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    concept: concept,
                    explanation: explanation,
                    target_audience: audience
                })
            });

            if (!response.ok) throw new Error('Analysis failed');

            const data = await response.json();
            renderResults(data);

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

    function renderResults(data) {
        // Populate Data
        document.getElementById('summaryText').textContent = data.summary;
        
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
        data.gaps.forEach(gap => gapsContainer.appendChild(createCard(gap, 'bg-[#1A0F0A]'))); // Subtle red tint bg if desired, keeping dark for now

        // Suggestions
        const suggestionsContainer = document.getElementById('suggestionsList');
        suggestionsContainer.innerHTML = '';
        data.suggestions.forEach(sug => suggestionsContainer.appendChild(createCard(sug)));

        // Questions
        const questionsContainer = document.getElementById('questionsList');
        questionsContainer.innerHTML = '';
        data.follow_up_questions.forEach(q => {
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
});
