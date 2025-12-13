document.addEventListener('DOMContentLoaded', function() {
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const hiddenDateInput = document.getElementById('selected-date');
    const hiddenTimeInput = document.getElementById('selected-time');
    const submitButton = document.getElementById('submit-booking');
    const timeLabel = document.getElementById('time-label');
    const listingId = document.getElementById('listing-id').value;

    initializeTimeSlots();

    document.querySelectorAll('.calendar-day').forEach(day => {
        day.addEventListener('click', function() {
            if (this.classList.contains('past') ||
                this.classList.contains('other-month') ||
                this.classList.contains('unavailable')) {
                return;
            }

            const previouslySelected = document.querySelector('.calendar-day.selected');
            if (previouslySelected) {
                previouslySelected.classList.remove('selected');
            }

            this.classList.add('selected');
            const selectedDate = this.dataset.date;
            hiddenDateInput.value = selectedDate;

            hiddenTimeInput.value = '';
            submitButton.disabled = true;

            timeLabel.textContent = 'Select Time';

            fetchAvailableSlots(selectedDate);
        });
    });

    function initializeTimeSlots() {
        timeSlotsContainer.innerHTML = '';

        for (let hour = 6; hour < 23; hour++) {
            const timeButton = document.createElement('button');
            timeButton.type = 'button';
            timeButton.className = 'time-slot-btn booked';
            timeButton.disabled = true;

            const displayHour = hour % 12 || 12;
            const period = hour < 12 ? 'AM' : 'PM';
            timeButton.textContent = `${displayHour}:00 ${period}`;
            timeButton.dataset.value = `${hour.toString().padStart(2, '0')}:00`;

            timeSlotsContainer.appendChild(timeButton);
        }
    }

    function fetchAvailableSlots(date) {
        fetch(`/listings/${listingId}/available-slots/?date=${date}`)
            .then(response => response.json())
            .then(data => {
                const buttons = timeSlotsContainer.querySelectorAll('.time-slot-btn');

                buttons.forEach(btn => {
                    const slot = data.slots.find(s => s.value === btn.dataset.value);

                    if (slot) {
                        btn.disabled = !slot.is_available;
                        btn.className = slot.is_available ? 'time-slot-btn' : 'time-slot-btn booked';

                        if (slot.is_available && !btn.hasAttribute('data-initialized')) {
                            btn.setAttribute('data-initialized', 'true');
                            btn.addEventListener('click', function() {
                                buttons.forEach(b => b.classList.remove('selected'));
                                this.classList.add('selected');
                                hiddenTimeInput.value = this.dataset.value;
                                submitButton.disabled = false;
                            });
                        }
                    } else {
                        btn.disabled = true;
                        btn.className = 'time-slot-btn booked';
                    }

                    btn.classList.remove('selected');
                });
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
            });
    }
});