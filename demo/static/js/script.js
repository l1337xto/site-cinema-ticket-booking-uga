const container = document.querySelector('.container');
const seats = document.querySelectorAll('.row .seat:not(.occupied');
const count = document.getElementById('count');
const movieSelect = document.getElementById('movie');
const maxSeats = document.getElementById('limit')
const payButton = document.getElementById('payButton')
let ticketPrice = +movieSelect.value;
let bookableSeats = +maxSeats.innerText
payButton.style.display='none';
function updateSelectedCount() {
  const selectedSeats = document.querySelectorAll('.row .seat.selected');
  const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat));
  console.log(seatsIndex)
  const selectedSeatsCount = selectedSeats.length;
  if(selectedSeatsCount<=bookableSeats){
    count.innerText = selectedSeatsCount;
  }
  else{
	count.innerText = bookableSeats;
  }
  if(bookableSeats===selectedSeatsCount){
	payButton.style.display='block';
  }
  else{
	  payButton.style.display='none';
  }
}
// Seat click event
container.addEventListener('click', (e) => {
	const selectedSeats = document.querySelectorAll('.row .seat.selected');
	const selectedSeatsCount = selectedSeats.length;
	const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat));
    
	if(selectedSeatsCount<bookableSeats){
	if (e.target.classList.contains('seat') && !e.target.classList.contains('occupied')) {
		e.target.classList.toggle('selected');
		updateSelectedCount();
	}
	}
	else{
		e.target.classList.remove('selected');
		updateSelectedCount();
	}
});