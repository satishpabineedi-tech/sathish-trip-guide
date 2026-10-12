
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];

let activeCategory = '';

function money(n) {
  return '₹' + Number(n || 0).toLocaleString('en-IN');
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[c]);
}

// Open destination details page
function openDestination(destinationId) {
  if (!destinationId) {
    alert('Destination ID not found.');
    return;
  }

  window.location.href =
    `/destination/${encodeURIComponent(destinationId)}`;
}

// Load destinations from Flask API
async function loadDestinations() {
  const cards = $('#destinationCards');

  if (!cards) {
    console.error('destinationCards element not found.');
    return;
  }

  const params = new URLSearchParams();

  const stateFilter = $('#stateFilter');
  const search = $('#search');

  if (stateFilter?.value) {
    params.set('state', stateFilter.value);
  }

  if (search?.value.trim()) {
    params.set('q', search.value.trim());
  }

  if (activeCategory) {
    params.set('category', activeCategory);
  }

  try {
    cards.innerHTML = '<p>Loading destinations...</p>';

    const res = await fetch(
      '/api/destinations?' + params.toString()
    );

    if (!res.ok) {
      throw new Error('Unable to load destinations.');
    }

    const places = await res.json();

    if (!Array.isArray(places)) {
      throw new Error('Invalid destination data received.');
    }

    cards.innerHTML = places.map(d => `
      <article
        class="destination-card"
        data-id="${escapeHtml(d.id)}"
        tabindex="0"
        role="link"
        aria-label="View ${escapeHtml(d.name)} trip details">

        <div
          class="card-image"
          style="background-image:url('${escapeHtml(d.image_url)}')">

          <span class="tag">
            ${escapeHtml(d.state)}
          </span>
        </div>

        <div class="card-body">

          <p class="card-category">
            ${escapeHtml(d.category || 'Destination')}
          </p>

          <h3>${escapeHtml(d.name)}</h3>

          <p class="muted small">
            ${escapeHtml(d.attractions || '')}
          </p>

          <div class="card-bottom">

            <div>
              <small>Sample trip estimate from</small>

              <strong>
                ${money(d.base_budget)}
                <small>/ person</small>
              </strong>
            </div>

            <button
              type="button"
              class="round-btn choose-dest"
              data-destination="${escapeHtml(d.name)}"
              aria-label="Plan ${escapeHtml(d.name)}">

              ↗

            </button>

          </div>
        </div>
      </article>
    `).join('');

    const emptyState = $('#emptyState');

    if (emptyState) {
      emptyState.classList.toggle(
        'hidden',
        places.length > 0
      );
    }

    // Click on a destination card opens details
    $$('.destination-card').forEach(card => {

      card.addEventListener('click', (event) => {

        // Arrow button should open the planner instead
        if (event.target.closest('.choose-dest')) {
          return;
        }

        openDestination(card.dataset.id);
      });

      // Keyboard accessibility
      card.addEventListener('keydown', (event) => {

        if (event.target.closest('.choose-dest')) {
          return;
        }

        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openDestination(card.dataset.id);
        }
      });

    });

    // Arrow button selects destination for trip planning
    $$('.choose-dest').forEach(btn => {

      btn.addEventListener('click', (event) => {

        event.stopPropagation();

        const destination = $('#destination');

        if (destination) {
          destination.value = btn.dataset.destination;
        }

        $('#planner')?.scrollIntoView({
          behavior: 'smooth'
        });

      });

    });

  } catch (error) {

    console.error('Destination loading error:', error);

    cards.innerHTML = `
      <p>Unable to load destinations.
      Please refresh the page and try again.</p>
    `;

    const emptyState = $('#emptyState');

    if (emptyState) {
      emptyState.classList.remove('hidden');
    }

  }
}


// Search button
$('#searchBtn')?.addEventListener('click', () => {
  loadDestinations();
});

// Search using Enter key
$('#search')?.addEventListener('keydown', event => {

  if (event.key === 'Enter') {
    event.preventDefault();
    loadDestinations();
  }

});

// State filter
$('#stateFilter')?.addEventListener('change', () => {
  loadDestinations();
});

// Category filter buttons
$$('.chip').forEach(btn => {

  btn.addEventListener('click', () => {

    $$('.chip').forEach(chip => {
      chip.classList.remove('active');
    });

    btn.classList.add('active');

    activeCategory = btn.dataset.category || '';

    loadDestinations();

  });

});

// Budget selection
$$('.budget-option').forEach(label => {

  label.addEventListener('click', () => {

    $$('.budget-option').forEach(option => {
      option.classList.remove('selected');
    });

    label.classList.add('selected');

  });

});


// Trip budget calculator
$('#plannerForm')?.addEventListener('submit', async event => {

  event.preventDefault();

  const budgetInput = $('input[name="budget"]:checked');

  if (!budgetInput) {
    alert('Please select a budget option.');
    return;
  }

  const payload = {
    start: $('#start')?.value || '',
    destination: $('#destination')?.value || '',
    people: $('#people')?.value || '1',
    days: $('#days')?.value || '1',
    budget_type: budgetInput.value
  };

  if (!payload.start || !payload.destination) {
    alert('Please enter your starting place and destination.');
    return;
  }

  const button = $(
    '#plannerForm button[type="submit"]'
  );

  const originalText = button
    ? button.textContent
    : 'Calculate my trip budget ↗';

  if (button) {
    button.disabled = true;
    button.textContent = 'Calculating...';
  }

  try {

    const res = await fetch('/api/calculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.error || 'Could not calculate estimate.'
      );
    }

    $('#results')?.classList.remove('hidden');

    if ($('#resultTitle')) {
      $('#resultTitle').textContent =
        `${data.days}-day ${data.destination} trip`;
    }

    if ($('#resultSubtitle')) {
      $('#resultSubtitle').textContent =
        `${data.start} → ${data.destination} · ` +
        `${data.people} traveller(s) · ` +
        `${String(data.budget_type).replace('-', ' ')} plan`;
    }

    if ($('#groupTotal')) {
      $('#groupTotal').textContent =
        money(data.group_total);
    }

    if ($('#perPerson')) {
      $('#perPerson').textContent =
        `${money(data.per_person)} per person`;
    }

    const costs = [
      ['Intercity transport', data.transport, '↔'],
      ['Room / stay', data.room, '⌂'],
      ['Food', data.food, '♨'],
      ['Local transport', data.local_transport, '⇄'],
      ['Tickets / activities', data.tickets, '◎'],
      ['Other expenses', data.other, '＋']
    ];

    if ($('#costGrid')) {
      $('#costGrid').innerHTML = costs.map(
        ([label, value, icon]) => `
          <div class="cost-item">
            <span>${icon}</span>
            <small>${escapeHtml(label)}</small>
            <strong>
              ${money(value)}
              <small>/ person</small>
            </strong>
          </div>
        `
      ).join('');
    }

    if ($('#itinerary')) {
      const itinerary = Array.isArray(data.itinerary)
        ? data.itinerary
        : [];

      $('#itinerary').innerHTML = itinerary.map(day => `
        <div class="itinerary-day">
          <span>DAY ${escapeHtml(day.day)}</span>
          <p>${escapeHtml(day.task)}</p>
        </div>
      `).join('');
    }

    $('#results')?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });

  } catch (error) {

    console.error('Trip calculation error:', error);
    alert(error.message || 'Something went wrong.');

  } finally {

    if (button) {
      button.disabled = false;
      button.textContent = originalText;
    }

  }

});


// Quick suggestion buttons
$$('.prompt').forEach(btn => {

  btn.addEventListener('click', () => {

    const prompt = btn.dataset.prompt;

    if (prompt === 'kerala') {

      if ($('#stateFilter')) {
        $('#stateFilter').value = 'Kerala';
      }

      loadDestinations();

      $('#explore')?.scrollIntoView({
        behavior: 'smooth'
      });

    } else if (prompt === 'nearby') {

      if ($('#search')) {
        $('#search').value = 'Hyderabad';
      }

      if ($('#stateFilter')) {
        $('#stateFilter').value = 'Telangana';
      }

      loadDestinations();

      $('#explore')?.scrollIntoView({
        behavior: 'smooth'
      });

    } else {

      if ($('#days')) {
        $('#days').value = 2;
      }

      if ($('#people')) {
        $('#people').value = 1;
      }

      $('#planner')?.scrollIntoView({
        behavior: 'smooth'
      });

      alert(
        'Choose a destination and Ultra budget ' +
        'to compare your trip against ₹5,000.'
      );

    }

  });

});


// Initial destination loading
document.addEventListener('DOMContentLoaded', () => {
  loadDestinations();
});

const showRouteBtn = document.getElementById("showRouteBtn");

if (showRouteBtn) {
    showRouteBtn.addEventListener("click", function () {
        const start = document.getElementById("start").value.trim();
        const destination =
            document.getElementById("destination").value.trim();
        const routeStatus = document.getElementById("routeStatus");

        if (!start || !destination) {
            routeStatus.textContent =
                "Please enter a starting point and select a destination.";
            return;
        }

        const mapsUrl =
            "https://www.google.com/maps/dir/" +
            encodeURIComponent(start) + "/" +
            encodeURIComponent(destination);

        window.open(mapsUrl, "_blank", "noopener");
        routeStatus.textContent =
            "Route opened in Google Maps.";
    });
}
function getDestinationImage(name) {
    const place = encodeURIComponent(name + " India tourism");
    return `https://loremflickr.com/900/600/${place}`;
}