async function analyzeTasks() {
    const input = document.getElementById('taskInput').value;
    let tasks;
    try {
      tasks = JSON.parse(input);
    } catch (e) {
      alert("Invalid JSON");
      return;
    }
    try {
      const res = await fetch('/api/tasks/analyze/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tasks)
      });
      const data = await res.json();
      if (res.ok) {
        renderResults(data.results);
      } else {
        alert(JSON.stringify(data));
      }
    } catch (err) {
      alert("Failed to call API: " + err.message);
    }
  }
  
  async function suggestTasks() {
    const input = document.getElementById('taskInput').value;
    let tasks;
    try {
      tasks = JSON.parse(input);
    } catch (e) {
      alert("Invalid JSON");
      return;
    }
    try {
      const res = await fetch('/api/tasks/suggest/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tasks)
      });
      const data = await res.json();
      if (res.ok) {
        const el = document.getElementById('results');
        el.innerHTML = '<h3>Top 3 suggestions</h3>';
        data.top.forEach(t => {
          const div = document.createElement('div');
          div.className = 'card high';
          div.innerHTML = `<strong>${t.task}</strong><div class="meta">${t.explanation}</div>`;
          el.appendChild(div);
        });
      } else {
        alert(JSON.stringify(data));
      }
    } catch (err) {
      alert("Failed to call API: " + err.message);
    }
  }
  
  function renderResults(results) {
    const el = document.getElementById('results');
    el.innerHTML = '';
    results.forEach(r => {
      const div = document.createElement('div');
      const cls = r.score >= 100 ? 'high' : (r.score >= 50 ? 'medium' : 'low');
      div.className = 'card ' + cls;
      div.innerHTML = `<strong>${r.title || r.name || '<untitled>'}</strong>
        <div class="meta">Score: ${r.score} | Due: ${r.due_date || '—'} | Importance: ${r.importance || '—'} | Est: ${r.estimated_hours || '—'}h</div>`;
      el.appendChild(div);
    });
  }
  