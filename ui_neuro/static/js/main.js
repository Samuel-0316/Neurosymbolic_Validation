document.getElementById('submit-query').addEventListener('click', async () => {
    const queryInput = document.getElementById('query-input').value;
    if (!queryInput) {
        alert('Please enter a query.');
        return;
    }

    // Show loading states
    document.getElementById('wrong-answer').textContent = 'Thinking...';
    document.getElementById('correct-answer').textContent = 'Processing...';
    animateConfidenceBar(0);
    animateConfidenceCircle(0);
    document.getElementById('confidence-score-text').textContent = '0.00';

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: queryInput })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch results.');
        }

        const data = await response.json();

        // Animate and display LLM generated answer
        typeWriterEffect('wrong-answer', data.wrong_answer || '—');
        // Animate and display processed answer
        typeWriterEffect('correct-answer', data.correct_answer || '—');

        // Animate confidence bar and circle
        let score = parseFloat(data.confidence_score);
        if (isNaN(score)) score = 0;
        animateConfidenceBar(score);
        animateConfidenceCircle(score);
        document.getElementById('confidence-score-text').textContent = score.toFixed(2);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('wrong-answer').textContent = 'Error!';
        document.getElementById('correct-answer').textContent = 'Error!';
        animateConfidenceBar(0);
        animateConfidenceCircle(0);
        document.getElementById('confidence-score-text').textContent = '0.00';
        alert('An error occurred while processing your query.');
    }
});

// Typewriter effect for chat bubbles
function typeWriterEffect(elementId, text) {
    const el = document.getElementById(elementId);
    el.textContent = '';
    let i = 0;
    function type() {
        if (i < text.length) {
            el.textContent += text.charAt(i);
            i++;
            setTimeout(type, 18 + Math.random() * 30);
        }
    }
    type();
}

// Animate confidence bar width
function animateConfidenceBar(score) {
    const bar = document.getElementById('confidence-bar');
    const percent = Math.max(0, Math.min(1, score)) * 100;
    bar.style.width = percent + '%';
}

// Animate SVG confidence circle
function animateConfidenceCircle(score) {
    const circle = document.getElementById('confidence-circle');
    const max = 314; // Circumference (2 * pi * r)
    const offset = max - (Math.max(0, Math.min(1, score)) * max);
    circle.style.strokeDashoffset = offset;
}