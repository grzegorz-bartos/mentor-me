document.addEventListener('DOMContentLoaded', function() {
    const startTimeSelect = document.getElementById('id_start_time');
    const hiddenDateInput = document.getElementById('selected-date');
    const listingId = document.getElementById('listing-id').value;

    // Calendar day click handler
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.addEventListener('click', function() {
            // Ignore past dates, other-month dates, and unavailable dates
            if (this.classList.contains('past') ||
                this.classList.contains('other-month') ||
                this.classList.contains('unavailable')) {
                return;
            }

            // Remove previous selection
            const previouslySelected = document.querySelector('.calendar-day.selected');
            if (previouslySelected) {
                previouslySelected.classList.remove('selected');
            }

            // Mark as selected
            this.classList.add('selected');
            const selectedDate = this.dataset.date;
            hiddenDateInput.value = selectedDate;

            // Fetch available slots
            fetchAvailableSlots(selectedDate);
        });
    });

    function fetchAvailableSlots(date) {
        startTimeSelect.innerHTML = '<option value="">Loading...</option>';
        startTimeSelect.disabled = true;

        fetch(`/listings/${listingId}/available-slots/?date=${date}`)
            .then(response => response.json())
            .then(data => {
                startTimeSelect.innerHTML = '';

                if (data.slots && data.slots.length > 0) {
                    const placeholder = document.createElement('option');
                    placeholder.value = '';
                    placeholder.textContent = 'Select a time';
                    startTimeSelect.appendChild(placeholder);

                    data.slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot.value;
                        option.textContent = slot.display;
                        startTimeSelect.appendChild(option);
                    });

                    startTimeSelect.disabled = false;
                } else {
                    const noSlots = document.createElement('option');
                    noSlots.value = '';
                    noSlots.textContent = 'No available time slots for this day';
                    startTimeSelect.appendChild(noSlots);
                }
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
                startTimeSelect.innerHTML = '<option value="">Error loading slots</option>';
            });
    }
});