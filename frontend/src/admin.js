// TODO The file is yet to update
// Определение констант URL
const apiUrl = 'http://127.0.0.1:8000/cafes';
const categoriesUrl = 'http://127.0.0.1:8000/categories';
const authUrl = `${apiUrl.replace('/cafes', '')}/auth/jwt/login`;

// DOM элементы
const authSection = document.getElementById('auth-section');
const loginForm = document.getElementById('login-form');
const addForm = document.getElementById('add-form');
const logoutButton = document.getElementById('logout-button');
const editForm = document.getElementById('edit-form');

// Schemas (Interfaces) - using JSDoc for typing in JS
/** @typedef {{id: number, title: string, city: string, description: string, image_url: string|null, best_for: string|null, also_good_for: string[]}} CafeData */
/** @typedef {{name: string}} Category */

	// Models
class Cafe {
	constructor(data) {
		this.id = data.id;
		this.title = data.title;
		this.city = data.city;
		this.description = data.description;
		this.image_url = data.image_url;
		this.best_for = data.best_for || 'N/A';
		this.also_good_for = data.also_good_for || [];
	}

	getFormattedAlsoGoodFor() {
		return this.also_good_for.join(', ') || 'None';
	}
}

// UI Components
class AdminUIRenderer {
	constructor(grid, addError, addSuccess, authError, loading, editModal, closeSpan) {
		this.grid = grid;
		this.addError = addError;
		this.addSuccess = addSuccess;
		this.authError = authError;
		this.loading = loading;
		this.editModal = editModal;
		this.closeSpan = closeSpan;
		this.editModal.classList.remove('visible'); // Ensure hidden initially

		// Modal close events
		this.closeSpan.onclick = () => this.hideEditModal();
		window.onclick = (event) => {
			if (event.target === this.editModal) this.hideEditModal();
		};
	}

	createCafeCard(cafe, onEdit, onDelete) {
		const card = document.createElement('div');
		card.className = 'cafe-card';

		const titleEl = document.createElement('h2');
		titleEl.textContent = cafe.title;
		card.appendChild(titleEl);

		const cityEl = document.createElement('p');
		cityEl.innerHTML = `<strong>City:</strong> ${cafe.city}`;
		card.appendChild(cityEl);

		const descEl = document.createElement('p');
		descEl.textContent = cafe.description;
		card.appendChild(descEl);

		const bestForEl = document.createElement('p');
		bestForEl.className = 'categories';
		bestForEl.innerHTML = `<strong>Best for:</strong> ${cafe.best_for}`;
		card.appendChild(bestForEl);

		const alsoGoodEl = document.createElement('p');
		alsoGoodEl.className = 'categories';
		alsoGoodEl.innerHTML = `<strong>Also good for:</strong> ${cafe.getFormattedAlsoGoodFor()}`;
		card.appendChild(alsoGoodEl);

		const editBtn = document.createElement('button');
		editBtn.textContent = 'Edit';
		editBtn.className = 'edit';
		editBtn.onclick = () => onEdit(cafe);
		card.appendChild(editBtn);

		const deleteBtn = document.createElement('button');
		deleteBtn.textContent = 'Delete';
		deleteBtn.onclick = () => onDelete(cafe.title, cafe.city);
		card.appendChild(deleteBtn);

		return card;
	}

	renderCafes(cafes, onEdit, onDelete) {
		this.grid.innerHTML = '';
		cafes.forEach(cafe => {
			this.grid.appendChild(this.createCafeCard(cafe, onEdit, onDelete));
		});
	}

	showMessage(element, text) {
		element.textContent = text;
		setTimeout(() => { element.textContent = ''; }, 5000);
	}

	showEditModal(cafe) {
		document.getElementById('edit_title').value = cafe.title;
		document.getElementById('edit_city').value = cafe.city;
		document.getElementById('edit_description').value = cafe.description;
		document.getElementById('edit_image_url').value = cafe.image_url || '';
		document.getElementById('edit_best_for').value = cafe.best_for;

		const editAlsoSelect = document.getElementById('edit_also_good_for');
		Array.from(editAlsoSelect.options).forEach(option => {
			option.selected = cafe.also_good_for.includes(option.value);
		});

		this.editModal.classList.add('visible');
	}

	hideEditModal() {
		this.editModal.classList.remove('visible');
	}

	hideLoading() {
		this.loading.style.display = 'none';
	}

	showLoading() {
		this.loading.style.display = 'block';
	}
}

// Data Managers / Services
class ApiService {
	async login(email, password) {
		const data = { username: email, password }; // Assuming email is username for JWT
		const response = await fetch(authUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: new URLSearchParams(data),
			credentials: 'include'
		});
		if (!response.ok) throw new Error('Login failed');
		return await response.json();
	}

	async loadCategories() {
		const response = await fetch(categoriesUrl);
		if (!response.ok) throw new Error('Failed to load categories');
		return await response.json();
	}

	async loadCafes(token) {
		const response = await fetch(apiUrl, {
			headers: { 'Authorization': `Bearer ${token}` },
			credentials: 'include'
		});
		if (!response.ok) throw new Error('Failed to load cafes');
		const data = await response.json();
		return data.map(item => new Cafe(item));
	}

	async addCafe(data, token) {
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
			body: JSON.stringify(data),
			credentials: 'include'
		});
		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.detail || 'Error adding cafe');
		}
		return await response.json();
	}

	async updateCafe(oldTitle, oldCity, data, token) {
		const response = await fetch(`${apiUrl}?title=${encodeURIComponent(oldTitle)}&city=${encodeURIComponent(oldCity)}`, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
			body: JSON.stringify(data),
			credentials: 'include'
		});
		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.detail || 'Error editing cafe');
		}
		return await response.json();
	}

	async deleteCafe(title, city, token) {
		const response = await fetch(`${apiUrl}?title=${encodeURIComponent(title)}&city=${encodeURIComponent(city)}`, {
			method: 'DELETE',
			headers: { 'Authorization': `Bearer ${token}` },
			credentials: 'include'
		});
		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.detail || 'Error deleting cafe');
		}
		return true;
	}
}

// State Management
class AppState {
	constructor() {
		this.cafes = [];
		this.categories = [];
		this.token = localStorage.getItem('token');
		this.eventTarget = new EventTarget();
		this.currentEditCafe = null;
	}

	async init() {
		uiRenderer.showLoading();
		try {
			if (this.token) {
				authSection.style.display = 'none';
				logoutButton.style.display = 'block';
				this.categories = await apiService.loadCategories();
				this.populateSelects(this.categories);
				this.cafes = await apiService.loadCafes(this.token);
				this.updateUI();
			}
		} catch (error) {
			uiRenderer.showMessage(uiRenderer.authError, `Error: ${error.message}`);
		} finally {
			uiRenderer.hideLoading();
		}
	}

	populateSelects(categories) {
		// Add form
		const bestSelect = document.getElementById('best_for');
		bestSelect.innerHTML = '<option value="" disabled selected>Select Best For</option>';
		const alsoSelect = document.getElementById('also_good_for');
		alsoSelect.innerHTML = '';

		// Edit form
		const editBestSelect = document.getElementById('edit_best_for');
		editBestSelect.innerHTML = '<option value="" disabled selected>Select Best For</option>';
		const editAlsoSelect = document.getElementById('edit_also_good_for');
		editAlsoSelect.innerHTML = '';

		categories.forEach(cat => {
			const option = document.createElement('option');
			option.value = cat.name;
			option.textContent = cat.name;
			bestSelect.appendChild(option.cloneNode(true));
			alsoSelect.appendChild(option.cloneNode(true));
			editBestSelect.appendChild(option.cloneNode(true));
			editAlsoSelect.appendChild(option.cloneNode(true));
		});
	}

	updateUI() {
		uiRenderer.renderCafes(this.cafes, this.editCafe.bind(this), this.deleteCafe.bind(this));
		this.dispatchChange();
	}

	async login(email, password) {
		try {
			const { access_token } = await apiService.login(email, password);
			this.token = access_token;
			localStorage.setItem('token', access_token);
			authSection.style.display = 'none';
			logoutButton.style.display = 'block';
			await this.init();  // Reload data after login
		} catch (error) {
			uiRenderer.showMessage(uiRenderer.authError, `Error: ${error.message}`);
		}
	}

	logout() {
		localStorage.removeItem('token');
		this.token = null;
		location.reload();
	}

	async addCafe(data) {
		if (!this.token) {
			uiRenderer.showMessage(uiRenderer.addError, 'Please login first');
			return;
		}
		try {
			await apiService.addCafe(data, this.token);
			uiRenderer.showMessage(uiRenderer.addSuccess, 'Cafe added successfully!');
			this.cafes = await apiService.loadCafes(this.token);
			this.updateUI();
		} catch (error) {
			uiRenderer.showMessage(uiRenderer.addError, `Error: ${error.message}`);
		}
	}

	editCafe(cafe) {
		this.currentEditCafe = cafe;
		uiRenderer.showEditModal(cafe);
	}

	async updateCafe(data) {
		if (!this.token || !this.currentEditCafe) return;
		try {
			await apiService.updateCafe(this.currentEditCafe.title, this.currentEditCafe.city, data, this.token);
			uiRenderer.showMessage(uiRenderer.addSuccess, 'Cafe updated successfully!');
			uiRenderer.hideEditModal();
			this.cafes = await apiService.loadCafes(this.token);
			this.updateUI();
		} catch (error) {
			uiRenderer.showMessage(uiRenderer.addError, `Error: ${error.message}`);
		}
	}

	async deleteCafe(title, city) {
		if (!this.token) {
			uiRenderer.showMessage(uiRenderer.addError, 'Please login first');
			return;
		}
		if (!confirm('Are you sure you want to delete this cafe?')) return;
		try {
			await apiService.deleteCafe(title, city, this.token);
			uiRenderer.showMessage(uiRenderer.addSuccess, 'Cafe deleted successfully!');
			this.cafes = await apiService.loadCafes(this.token);
			this.updateUI();
		} catch (error) {
			uiRenderer.showMessage(uiRenderer.addError, `Error: ${error.message}`);
		}
	}

	onChange(callback) {
		this.eventTarget.addEventListener('stateChange', callback);
	}

	dispatchChange() {
		this.eventTarget.dispatchEvent(new Event('stateChange'));
	}
}

// Инициализация
const apiService = new ApiService();
const uiRenderer = new AdminUIRenderer(
	document.getElementById('cafe-grid'),
	document.getElementById('add-error'),
	document.getElementById('add-success'),
	document.getElementById('auth-error'),
	document.getElementById('loading'),
	document.getElementById('edit-modal'),
	document.querySelector('.close')
);
const appState = new AppState();

appState.init();

// Event listeners
loginForm.addEventListener('submit', (e) => {
	e.preventDefault();
	const email = document.getElementById('email').value;
	const password = document.getElementById('password').value;
	appState.login(email, password);
});

addForm.addEventListener('submit', (e) => {
	e.preventDefault();
	const alsoSelect = document.getElementById('also_good_for');
	const data = {
		title: document.getElementById('title').value.trim(),
		city: document.getElementById('city').value.trim(),
		description: document.getElementById('description').value.trim(),
		image_url: document.getElementById('image_url').value.trim() || null,
		best_for: document.getElementById('best_for').value,
		also_good_for: Array.from(alsoSelect.selectedOptions).map(o => o.value),
	};
	if (!data.title || !data.city || !data.description || !data.best_for) {
		uiRenderer.showMessage(uiRenderer.addError, 'All required fields must be filled');
		return;
	}
	if (!appState.categories.some(cat => cat.name === data.best_for)) {
		uiRenderer.showMessage(uiRenderer.addError, `Invalid best_for: ${data.best_for}`);
		return;
	}
	const invalidCats = data.also_good_for.filter(cat => !appState.categories.some(c => c.name === cat));
	if (invalidCats.length) {
		uiRenderer.showMessage(uiRenderer.addError, `Invalid also_good_for: ${invalidCats.join(', ')}`);
		return;
	}
	appState.addCafe(data);
});

editForm.addEventListener('submit', (e) => {
	e.preventDefault();
	const editAlsoSelect = document.getElementById('edit_also_good_for');
	const data = {
		title: document.getElementById('edit_title').value.trim(),
		city: document.getElementById('edit_city').value.trim(),
		description: document.getElementById('edit_description').value.trim(),
		image_url: document.getElementById('edit_image_url').value.trim() || null,
		best_for: document.getElementById('edit_best_for').value,
		also_good_for: Array.from(editAlsoSelect.selectedOptions).map(o => o.value),
	};
	if (!data.title || !data.city || !data.description || !data.best_for) {
		uiRenderer.showMessage(uiRenderer.addError, 'All required fields must be filled');
		return;
	}
	if (!appState.categories.some(cat => cat.name === data.best_for)) {
		uiRenderer.showMessage(uiRenderer.addError, `Invalid best_for: ${data.best_for}`);
		return;
	}
	const invalidCats = data.also_good_for.filter(cat => !appState.categories.some(c => c.name === cat));
	if (invalidCats.length) {
		uiRenderer.showMessage(uiRenderer.addError, `Invalid also_good_for: ${invalidCats.join(', ')}`);
		return;
	}
	appState.updateCafe(data);
});

logoutButton.addEventListener('click', () => appState.logout());