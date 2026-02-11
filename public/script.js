let selectedSeats = [];

async function loadCampaigns() {
    const res = await fetch('/campaigns');
    const campaigns = await res.json();

    const select = document.getElementById('campaignSelect');

    campaigns.forEach(campaign => {
        const option = document.createElement('option');
        option.value = campaign.id;
        option.textContent = campaign.name;
        option.dataset.color = campaign.color_hex;
        select.appendChild(option);
    });
}

async function loadSeats() {
    const res = await fetch('/seats');
    const seats = await res.json();

    const floor = document.getElementById('floor');
    floor.innerHTML = '';

    seats.forEach(seat => {
        const seatDiv = document.createElement('div');
        seatDiv.classList.add('seat');

        seatDiv.style.left = seat.position_x + 'px';
        seatDiv.style.top = seat.position_y + 'px';

        seatDiv.innerText = seat.label;
            if (seat.booking_status === "pending") {
                seatDiv.style.backgroundColor = seat.color_hex;
                seatDiv.style.opacity = "0.6";
            }


       if (seat.status === "available") {
            seatDiv.addEventListener('click', () => toggleSeat(seat.id, seatDiv));
        }

        floor.appendChild(seatDiv);
    });
}

function toggleSeat(seatId, seatDiv) {
    if (selectedSeats.includes(seatId)) {
        selectedSeats = selectedSeats.filter(id => id !== seatId);
        seatDiv.style.backgroundColor = '#ddd';
    } else {
        selectedSeats.push(seatId);
        seatDiv.style.backgroundColor = '#4CAF50';
    }

    console.log("Selected Seats:", selectedSeats);
}

loadCampaigns();
loadSeats();

async function bookSeats() {
    if (selectedSeats.length === 0) {
        alert("Please select at least one seat.");
        return;
    }

    const campaignSelect = document.getElementById('campaignSelect');
    const campaignId = campaignSelect.value;

    const response = await fetch('/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: 1, // dummy user for now
            campaign_id: campaignId,
            seat_ids: selectedSeats
        })
    });

    const result = await response.json();
    alert(result.message);

    selectedSeats = [];
    loadSeats();
}

