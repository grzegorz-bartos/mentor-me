document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('id_date');
    const startTimeSelect = document.getElementById('id_start_time');
    const durationSelect = document.getElementById('id_duration_hours');
    const listingId = document.getElementById('listing-id').value;

    startTimeSelect.disabled = true;
    durationSelect.disabled = true;

    const originalTimeOption = startTimeSelect.querySelector('option');
    const originalDurationOption = durationSelect.querySelector('option');

    dateInput.addEventListener('change', function() {
        const selectedDate = this.value;

        if (!selectedDate) {
            startTimeSelect.disabled = true;
            durationSelect.disabled = true;
            return;
        }

        startTimeSelect.innerHTML = '<option value="">Loading...</option>';
        startTimeSelect.disabled = true;

        fetch(`/listings/${listingId}/available-slots/?date=${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                startTimeSelect.innerHTML = '';

                if (data.slots && data.slots.length > 0) {
                    const placeholder = document.createElement('option');
                    placeholder.value = '';
                    placeholder.textContent = '---------';
                    startTimeSelect.appendChild(placeholder);

                    data.slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot.value;
                        option.textContent = slot.display;
                        startTimeSelect.appendChild(option);
                    });

                    startTimeSelect.disabled = false;
                    durationSelect.disabled = false;
                } else {
                    const noSlots = document.createElement('option');
                    noSlots.value = '';
                    noSlots.textContent = 'No available time slots';
                    startTimeSelect.appendChild(noSlots);
                }
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
                startTimeSelect.innerHTML = '<option value="">Error loading slots</option>';
            });
    });
});