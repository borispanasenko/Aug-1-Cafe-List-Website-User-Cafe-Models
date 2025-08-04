// 1. URLs (Конфигурация — самый базовый уровень)
const apiUrl = 'http://127.0.0.1:8000/cafes';
const categoriesUrl = 'http://127.0.0.1:8000/categories';

// 2. Interfaces (Типы данных — основа для моделей)
/** @typedef {{id: number, title: string, city: string, description: string, image_url: string|null, best_for: string|null, also_good_for: string[]}} CafeData */
/** @typedef {{name: string}} Category */

// 3. Utils (Вспомогательные функции — используются в моделях)
function normalizeString(str) {
	return (str || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

// 4. HttpClient (Низкоуровневый клиент для HTTP-запросов — абстрагирует fetch, используется в ApiService)
class HttpClient {
	async get(url) {
		try {
			const response = await fetch(url);
			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				throw new Error(errorData.detail || `HTTP error: ${response.status}`);
			}
			return await response.json();
		} catch (error) {
			throw new Error(`Network error: ${error.message}`);
		}
	}
}

// 5. Frontend Models (Модели данных — строятся на типах и утилитах)
class Cafe {
	constructor(data) {
		if (!data || typeof data.id !== 'number' || typeof data.title !== 'string') {
			throw new Error('Invalid Cafe data');
		}
		this.id = data.id;
		this.title = data.title;
		this.city = data.city || '';
		this.description = data.description || '';
		this.image_url = data.image_url || null;
		this.best_for = data.best_for || 'N/A';
		this.also_good_for = data.also_good_for || [];
	}

	getNormalizedCity() {
		return normalizeString(this.city);
	}

	getNormalizedBestFor() {
		return normalizeString(this.best_for);
	}

	getNormalizedAlsoGoodFor() {
		return this.also_good_for.map(normalizeString);
	}

	getFormattedAlsoGoodFor() {
		return this.also_good_for.join(', ') || 'None';
	}
}

// 6. ApiService (Сервисы — низкоуровневый доступ к данным, зависит от HttpClient и моделей)
class ApiService {
	constructor(httpClient) {
		if (!(httpClient instanceof HttpClient)) {
			throw new Error('HttpClient instance required');
		}
		this.httpClient = httpClient;
	}

	async loadCategories() {
		return await this.httpClient.get(categoriesUrl);
	}

	async loadCafes() {
		const data = await this.httpClient.get(apiUrl);
		return data.map(item => new Cafe(item));
	}
}

// 7. CafeFilterService (Сервис фильтрации — отдельный компонент для логики фильтров, зависит от моделей и утилит)
class CafeFilterService {
	static filter(cafes, filters) {
		return cafes
			.filter(cafe => this.matchCity(cafe, filters.city))
			.filter(cafe => this.matchBestFor(cafe, filters.bestFor))
			.filter(cafe => this.matchAlsoGoodFor(cafe, filters.alsoGoodFor));
	}

	static matchCity(cafe, city) {
		const norm = normalizeString(city);
		return !norm || cafe.getNormalizedCity().includes(norm);
	}

	static matchBestFor(cafe, bestFor) {
		const norm = normalizeString(bestFor);
		return !norm ||
			cafe.getNormalizedBestFor().includes(norm) ||
			cafe.getNormalizedAlsoGoodFor().some(cat => cat.includes(norm));
	}

	static matchAlsoGoodFor(cafe, tags) {
		const normTags = (tags || []).map(normalizeString);
		return normTags.length === 0 ||
			cafe.getNormalizedAlsoGoodFor().some(cat => normTags.includes(cat));
	}
}

// 7. CafeSorterService (Сервис сортировки — отдельный компонент для упорядочивания результатов по релевантности)
class CafeSorterService {
	static sortByBestForRelevance(cafes, bestFor) {
		const bestForNorm = normalizeString(bestFor || '');
		if (!bestForNorm) {
			return cafes; // Нет фильтра — не сортируем, возвращаем как есть
		}

		// Сортировка: прямые совпадения (в best_for) выше косвенных (в also_good_for)
		return cafes.slice().sort((a, b) => {
			const aDirect = a.getNormalizedBestFor().includes(bestForNorm);
			const bDirect = b.getNormalizedBestFor().includes(bestForNorm);
			return aDirect === bDirect ? 0 : aDirect ? -1 : 1;
		});
	}
}

// 8. AppState (Состояние приложения — зависит от сервисов и моделей)
class AppState {
	constructor() {
		this.cafes = [];
		this.categories = [];
		this.cityQuery = '';
		this.bestFor = '';
		this.alsoGoodFor = [];
		this.isLoading = false;
		this.error = null;
		this.eventTarget = new EventTarget();
	}

	async init() {
		this.isLoading = true;
		this.dispatchChange();
		try {
			this.categories = await apiService.loadCategories();
			this.cafes = await apiService.loadCafes();
		} catch (error) {
			this.error = `Initialization error: ${error.message}`;
		} finally {
			this.isLoading = false;
			this.dispatchChange();
		}
	}

	setCityQuery(query) {
		this.cityQuery = query || '';
		this.dispatchChange();
	}

	setBestFor(value) {
		this.bestFor = value || '';
		this.dispatchChange();
	}

	setAlsoGoodFor(values) {
		this.alsoGoodFor = values || [];
		this.dispatchChange();
	}

	resetFilters() {
		this.cityQuery = '';
		this.bestFor = '';
		this.alsoGoodFor = [];
		this.dispatchChange();
	}

	getFilteredCafes() {
		const filtered = CafeFilterService.filter(this.cafes, {
			city: this.cityQuery,
			bestFor: this.bestFor,
			alsoGoodFor: this.alsoGoodFor
		});
		return CafeSorterService.sortByBestForRelevance(filtered, this.bestFor);
	}

	onChange(callback) {
		this.eventTarget.addEventListener('stateChange', callback);
	}

	dispatchChange() {
		this.eventTarget.dispatchEvent(new Event('stateChange'));
	}
}

// 9. UI Renderer (UI-компоненты для рендеринга — зависят от моделей)
class CafeRenderer {
	constructor(grid) {
		if (!grid || !(grid instanceof HTMLElement)) {
			throw new Error('Valid grid element required');
		}
		this.grid = grid;
	}

	createCafeCard(cafe) {
		const card = document.createElement('div');
		card.className = 'cafe-card';

		const img = document.createElement('img');
		img.src = cafe.image_url || 'https://via.placeholder.com/300x220?text=No+Image';
		img.alt = cafe.title;
		card.appendChild(img);

		const content = document.createElement('div');
		content.className = 'cafe-card-content';

		const title = document.createElement('h2');
		title.textContent = cafe.title;
		content.appendChild(title);

		const rating = document.createElement('p');
		rating.className = 'rating';
		rating.innerHTML = '★★★★☆ (4.5)'; // Плейсхолдер
		content.appendChild(rating);

		const city = document.createElement('p');
		city.innerHTML = `<strong>City:</strong> ${cafe.city}`;
		content.appendChild(city);

		const description = document.createElement('p');
		description.textContent = cafe.description;
		content.appendChild(description);

		const bestFor = document.createElement('p');
		bestFor.className = 'categories';
		bestFor.innerHTML = `<strong>Best for:</strong> ${cafe.best_for}`;
		content.appendChild(bestFor);

		const alsoGoodFor = document.createElement('p');
		alsoGoodFor.className = 'categories';
		alsoGoodFor.innerHTML = `<strong>Also good for:</strong> ${cafe.getFormattedAlsoGoodFor()}`;
		content.appendChild(alsoGoodFor);

		card.appendChild(content);
		return card;
	}

	renderCafes(cafes) {
		this.grid.innerHTML = '';
		if (cafes.length === 0) {
			const empty = document.createElement('p');
			empty.className = 'empty';
			empty.textContent = 'No cafes found matching your filters.';
			this.grid.appendChild(empty);
			return;
		}
		cafes.forEach(cafe => this.grid.appendChild(this.createCafeCard(cafe)));
	}

	showError(message) {
		this.grid.innerHTML = `<p class="error">Error: ${message}</p>`;
	}
}

// 10. UIController (Контроллер UI — high-level, зависит от состояния и рендерера)
class UIController {
	constructor(appState, renderer, dom) {
		if (!(appState instanceof AppState) || !(renderer instanceof CafeRenderer) || !dom || typeof dom !== 'object') {
			throw new Error('Invalid constructor parameters');
		}
		this.appState = appState;
		this.renderer = renderer;
		this.dom = dom;
		this.appState.onChange(this.render.bind(this));
		this.setupEventListeners();
	}

	setupEventListeners() {
		this.dom.cityFilter.addEventListener('keypress', (e) => {
			if (e.key === 'Enter') {
				this.appState.setCityQuery(this.dom.cityFilter.value);
			}
		});
		this.dom.searchBtn.addEventListener('click', () => {
			this.appState.setCityQuery(this.dom.cityFilter.value);
		});
		this.dom.bestForFilter.addEventListener('change', () => {
			this.appState.setBestFor(this.dom.bestForFilter.value);
		});
		this.dom.alsoGoodForFilter.addEventListener('change', () => {
			const selected = Array.from(this.dom.alsoGoodForFilter.selectedOptions).map(opt => opt.value);
			this.appState.setAlsoGoodFor(selected);
		});
		this.dom.resetFiltersBtn.addEventListener('click', () => {
			this.appState.resetFilters();
			this.dom.cityFilter.value = '';
		});
	}

	populateFilters(categories) {
		if (!Array.isArray(categories)) {
			throw new Error('Categories must be an array');
		}
		this.dom.bestForFilter.innerHTML = '<option value="" selected>All Categories</option>';
		this.dom.alsoGoodForFilter.innerHTML = '';
		categories.forEach(cat => {
			const option = document.createElement('option');
			option.value = cat.name;
			option.textContent = cat.name;
			this.dom.bestForFilter.appendChild(option.cloneNode(true));
			this.dom.alsoGoodForFilter.appendChild(option.cloneNode(true));
		});
	}

	syncSelects() {
		this.dom.bestForFilter.value = this.appState.bestFor;
		Array.from(this.dom.alsoGoodForFilter.options).forEach(opt => {
			opt.selected = this.appState.alsoGoodFor.includes(opt.value);
		});
	}

	updateChips() {
		this.dom.selectedChips.innerHTML = '';
		this.appState.alsoGoodFor.forEach(value => {
			const chip = document.createElement('div');
			chip.className = 'chip';
			chip.textContent = value;
			const removeBtn = document.createElement('button');
			removeBtn.textContent = '×';
			removeBtn.onclick = () => {
				const newValues = this.appState.alsoGoodFor.filter(v => v !== value);
				this.appState.setAlsoGoodFor(newValues);
			};
			chip.appendChild(removeBtn);
			this.dom.selectedChips.appendChild(chip);
		});
	}

	render() {
		this.syncSelects();
		this.updateChips();
		this.dom.sidebar.classList.toggle('visible', !!this.appState.cityQuery.trim());
		if (this.appState.error) {
			this.renderer.showError(this.appState.error);
			this.dom.loading.style.display = 'none';
			return;
		}
		if (this.appState.isLoading) {
			this.dom.loading.style.display = 'block';
			this.renderer.renderCafes([]);
			return;
		}
		this.dom.loading.style.display = 'none';
		const filtered = this.appState.getFilteredCafes();
		this.renderer.renderCafes(filtered);
		this.dom.resultsCount.textContent = `Found ${filtered.length} cafes`;
	}
}

// 11. DOM Elements (Элементы DOM — используются в UI)
const domElements = {
	cafeGrid: document.getElementById('cafe-grid'),
	cityFilter: document.getElementById('city-filter'),
	bestForFilter: document.getElementById('best-for-filter'),
	alsoGoodForFilter: document.getElementById('also-good-for-filter'),
	resetFiltersBtn: document.getElementById('reset-filters'),
	searchBtn: document.getElementById('search-btn'),
	loading: document.getElementById('loading'),
	sidebar: document.getElementById('sidebar'),
	selectedChips: document.getElementById('selected-chips'),
	resultsCount: document.getElementById('results-count')
};

// 12. Initialization (Инициализация — самый верхний уровень, собирает всё вместе)
const httpClient = new HttpClient();
const apiService = new ApiService(httpClient);
const renderer = new CafeRenderer(domElements.cafeGrid);
const appState = new AppState();
const uiController = new UIController(appState, renderer, domElements);

(async () => {
	await appState.init();
	if (!appState.error) {
		uiController.populateFilters(appState.categories);
	}
})();