class SearchableSelect {
    constructor(inputId, dropdownId, hiddenInputId, options) {
        this.input = document.getElementById(inputId);
        this.dropdown = document.getElementById(dropdownId);
        this.hiddenInput = document.getElementById(hiddenInputId);
        this.options = options;
        this.filteredOptions = options;
        this.highlightedIndex = -1;
        
        this.init();
    }
    
    init() {
        this.input.addEventListener('input', this.handleInput.bind(this));
        // this.input.addEventListener('focus', this.showDropdown.bind(this));
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        document.addEventListener('click', this.handleOutsideClick.bind(this));
    }
    
    handleInput(e) {
        const query = e.target.value;
        this.filterOptions(query);
        this.showDropdown();
    }
    
    handleKeydown(e) {
        if (!this.dropdown.style.display || this.dropdown.style.display === 'none') {
            if (e.key === 'Enter' || e.key === 'ArrowDown') {
                e.preventDefault();
                this.showDropdown();
            }
            return;
        }
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.highlightNext();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.highlightPrevious();
                break;
            case 'Enter':
                e.preventDefault();
                this.selectHighlighted();
                break;
            case 'Escape':
                this.hideDropdown();
                break;
        }
    }
    
    filterOptions(query) {
        this.filteredOptions = this.options.filter(option => 
            option.toLowerCase().includes(query.toLowerCase())
        );
        this.highlightedIndex = -1;
        this.renderDropdown();
    }
    
    renderDropdown() {
        this.dropdown.innerHTML = '';
        
        if (this.filteredOptions.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'no-results';
            noResults.textContent = 'No results found';
            this.dropdown.appendChild(noResults);
            return;
        }
        
        this.filteredOptions.forEach((option, index) => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.textContent = option;
            item.addEventListener('click', () => this.selectOption(option));
            this.dropdown.appendChild(item);
        });
    }
    
    showDropdown() {
        if (this.filteredOptions.length === 0 && this.input.value === '') {
            this.filteredOptions = this.options;
            this.renderDropdown();
        }
        this.dropdown.style.display = 'block';
    }
    
    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.highlightedIndex = -1;
    }
    
    selectOption(option) {
        this.input.value = option;
        this.hiddenInput.value = option;
        this.hideDropdown();
    }
    
    highlightNext() {
        const items = this.dropdown.querySelectorAll('.dropdown-item');
        if (items.length === 0) return;
        
        this.clearHighlight();
        this.highlightedIndex = Math.min(this.highlightedIndex + 1, items.length - 1);
        items[this.highlightedIndex].classList.add('highlighted');
        this.scrollToHighlighted();
    }
    
    highlightPrevious() {
        const items = this.dropdown.querySelectorAll('.dropdown-item');
        if (items.length === 0) return;
        
        this.clearHighlight();
        this.highlightedIndex = Math.max(this.highlightedIndex - 1, 0);
        items[this.highlightedIndex].classList.add('highlighted');
        this.scrollToHighlighted();
    }
    
    selectHighlighted() {
        const items = this.dropdown.querySelectorAll('.dropdown-item');
        if (this.highlightedIndex >= 0 && items[this.highlightedIndex]) {
            this.selectOption(items[this.highlightedIndex].textContent);
        }
    }
    
    clearHighlight() {
        const highlighted = this.dropdown.querySelector('.highlighted');
        if (highlighted) {
            highlighted.classList.remove('highlighted');
        }
    }
    
    scrollToHighlighted() {
        const highlighted = this.dropdown.querySelector('.highlighted');
        if (highlighted) {
            highlighted.scrollIntoView({ block: 'nearest' });
        }
    }
    
    handleOutsideClick(e) {
        if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
            this.hideDropdown();
        }
    }
}