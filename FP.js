// Tab Switching
document.querySelectorAll('.tab-btn').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    document.querySelectorAll('.packages-container').forEach(container => {
      container.style.display = container.id === button.dataset.tab ? 'grid' : 'none';
    });
  });
});
// Phone Number Validation
const phoneRegex = /^(07\d{8}|254\d{9}|\+254\d{9})$/;
document.querySelectorAll('.payment-form').forEach(form => {
  const phoneInput = form.querySelector('input[name="phone"]');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (phoneRegex.test(phoneInput.value)) {
      const packageName = form.dataset.package;
      const amount = form.dataset.amount;
      showModal(`Jaysolution: Payment of KSH ${amount} for ${packageName} confirmed! Check ${phoneInput.value} for M-Pesa prompt.`);
      form.reset();
    } else {
      alert('Please enter a valid Kenyan phone number (e.g., 07XXXXXXXX or +254XXXXXXXX)');
    }
  });
});

// Modal Handling
const modal = document.getElementById('payment-modal');
const modalMessage = document.getElementById('modal-message');
const closeBtn = document.querySelector('.close-btn');
const modalCloseBtn = document.querySelector('.modal-close-btn');
function showModal(message) {
  modalMessage.textContent = message;
  modal.style.display = 'flex';
}
closeBtn.addEventListener('click', () => modal.style.display = 'none');
modalCloseBtn.addEventListener('click', () => modal.style.display = 'none');
window.addEventListener('click', (e) => {
  if (e.target === modal) modal.style.display = 'none';
});

