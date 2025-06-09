document.getElementById('submit-query').addEventListener('click', async () => {
    const queryInput = document.getElementById('query-input').value;
    if (!queryInput) {
        alert('Please enter a query.');
        return;
    }

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

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;

        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;
            if (value) {
                const chunk = decoder.decode(value, { stream: true });
                const data = JSON.parse(chunk);

                if (data.wrong_answer) {
                    document.getElementById('wrong-answer').textContent = data.wrong_answer;
                }

                if (data.correct_answer) {
                    document.getElementById('correct-answer').textContent = data.correct_answer;
                }

                if (data.confidence_score) {
                    document.getElementById('confidence').textContent = data.confidence_score;
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing your query.');
    }
});