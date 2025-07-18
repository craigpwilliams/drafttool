html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Fantasy Draft App</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    input, button { margin: 5px; }
    .player { margin-bottom: 10px; }
    .summary { margin-top: 20px; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Fantasy Draft</h1>

  <div>
    <input type="text" id="ownerName" placeholder="Owner Name">
    <input type="text" id="playerName" placeholder="Player Name">
    <input type="number" id="bidAmount" placeholder="Bid Amount" min="1">
    <button onclick="addPlayer()">Add Player</button>
    <button onclick="resetDraft()">Reset Draft</button>
  </div>

  <div id="playersList"></div>

  <div class="summary">
    Remaining Budget: $<span id="remainingBudget">200</span><br>
    Max Remaining Bid: $<span id="maxBid">200</span>
  </div>

  <script>
    const MAX_BUDGET = 200;
    const ROSTER_SIZE = 14;

    let draftPicks = JSON.parse(localStorage.getItem('draftPicks')) || [];

    function saveDraft() {
      localStorage.setItem('draftPicks', JSON.stringify(draftPicks));
    }

    function updateUI() {
      const list = document.getElementById('playersList');
      list.innerHTML = '';
      draftPicks.forEach((p, i) => {
        const div = document.createElement('div');
        div.className = 'player';
        div.textContent = `${i + 1}. ${p.owner} - ${p.name} - $${p.bid}`;
        list.appendChild(div);
      });

      const totalSpent = draftPicks.reduce((sum, p) => sum + p.bid, 0);
      const remaining = MAX_BUDGET - totalSpent;
      const spotsLeft = ROSTER_SIZE - draftPicks.length;
      const maxBid = remaining - (spotsLeft - 1);

      document.getElementById('remainingBudget').textContent = remaining;
      document.getElementById('maxBid').textContent = spotsLeft > 0 ? Math.max(maxBid, 1) : 0;
    }

    function addPlayer() {
      const owner = document.getElementById('ownerName').value.trim();
      const name = document.getElementById('playerName').value.trim();
      const bid = parseInt(document.getElementById('bidAmount').value);

      if (!owner || !name || isNaN(bid) || bid < 1) {
        alert('Please enter a valid owner name, player name, and bid.');
        return;
      }

      const totalSpent = draftPicks.reduce((sum, p) => sum + p.bid, 0);
      const remaining = MAX_BUDGET - totalSpent;
      const spotsLeft = ROSTER_SIZE - draftPicks.length;
      const maxBid = remaining - (spotsLeft - 1);

      if (draftPicks.length >= ROSTER_SIZE) {
        alert('Roster is full!');
        return;
      }

      if (bid > maxBid) {
        alert(`Bid too high! Max allowed bid is $${maxBid}`);
        return;
      }

      draftPicks.push({ owner, name, bid });
      saveDraft();
      updateUI();

      document.getElementById('ownerName').value = '';
      document.getElementById('playerName').value = '';
      document.getElementById('bidAmount').value = '';
    }

    function resetDraft() {
      if (confirm('Are you sure you want to reset the draft?')) {
        draftPicks = [];
        localStorage.removeItem('draftPicks');
        updateUI();
      }
    }

    updateUI();
  </script>
</body>
</html>
"""