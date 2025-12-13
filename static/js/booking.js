document.addEventListener('DOMContentLoaded', function() {
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const hiddenDateInput = document.getElementById('selected-date');
    const hiddenTimeInput = document.getElementById('selected-time');
    const submitButton = document.getElementById('submit-booking');
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

            // Clear time selection
            hiddenTimeInput.value = '';
            submitButton.disabled = true;

            // Fetch available slots
            fetchAvailableSlots(selectedDate);
        });
    });

    function fetchAvailableSlots(date) {
        timeSlotsContainer.innerHTML = '<div class="text-muted small">Loading...</div>';

        fetch(`/listings/${listingId}/available-slots/?date=${date}`)
            .then(response => response.json())
            .then(data => {
                timeSlotsContainer.innerHTML = '';

                if (data.slots && data.slots.length > 0) {
                    data.slots.forEach(slot => {
                        const timeButton = document.createElement('button');
                        timeButton.type = 'button';
                        timeButton.className = slot.is_available ? 'time-slot-btn' : 'time-slot-btn booked';
                        timeButton.textContent = slot.display;
                        timeButton.dataset.value = slot.value;
                        timeButton.disabled = !slot.is_available;

                        if (slot.is_available) {
                            timeButton.addEventListener('click', function() {
                                document.querySelectorAll('.time-slot-btn').forEach(btn => {
                                    btn.classList.remove('selected');
                                });

                                this.classList.add('selected');
                                hiddenTimeInput.value = this.dataset.value;
                                submitButton.disabled = false;
                            });
                        }

                        timeSlotsContainer.appendChild(timeButton);
                    });
                } else {
                    timeSlotsContainer.innerHTML = '<div class="text-muted small">No time slots available</div>';
                }
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
                timeSlotsContainer.innerHTML = '<div class="text-danger small">Error loading slots</div>';
            });
    }
});