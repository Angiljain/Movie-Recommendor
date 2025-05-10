document.addEventListener('DOMContentLoaded', function() {
    // Movie search functionality
    const searchInput = document.getElementById('movie-search');
    const searchResults = document.getElementById('search-results');
    const selectedMovieInput = document.getElementById('selected-movie');
    const recommendationForm = document.getElementById('recommendation-form');
    
    if (searchInput && searchResults) {
        searchInput.addEventListener('input', debounce(function() {
            const query = searchInput.value.trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.classList.remove('show');
                return;
            }
            
            fetch(`/search?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) {
                        searchResults.innerHTML = '<div class="search-result">No movies found</div>';
                    } else {
                        searchResults.innerHTML = '';
                        data.forEach(movie => {
                            const div = document.createElement('div');
                            div.className = 'search-result';
                            div.textContent = movie;
                            div.addEventListener('click', () => {
                                searchInput.value = movie;
                                selectedMovieInput.value = movie;
                                searchResults.classList.remove('show');
                            });
                            searchResults.appendChild(div);
                        });
                    }
                    searchResults.classList.add('show');
                })
                .catch(error => {
                    console.error('Error fetching search results:', error);
                });
        }, 300));
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
                searchResults.classList.remove('show');
            }
        });
        
        // Form validation
        if (recommendationForm) {
            recommendationForm.addEventListener('submit', function(event) {
                if (!selectedMovieInput.value) {
                    event.preventDefault();
                    alert('Please select a movie from the search results');
                }
            });
        }
    }
    
    // Carousel functionality
    const carousel = document.querySelector('.carousel');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    
    if (carousel && prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: -500, behavior: 'smooth' });
        });
        
        nextBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: 500, behavior: 'smooth' });
        });
    }
    
    // Utility function for debouncing
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});