// Navbar dropdown functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle dropdown toggles for mobile/touch devices
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle, .user-button');

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = this.nextElementSibling;
            if (dropdown) {
                dropdown.classList.toggle('active');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown, .user-dropdown')) {
            document.querySelectorAll('.dropdown-menu, .user-menu').forEach(menu => {
                menu.classList.remove('active');
            });
        }
    });

    // Theme toggle functionality
    const themeSwitch = document.getElementById('theme-switch');

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Theme switch change event
    themeSwitch.addEventListener('change', function() {
        const theme = this.checked ? 'dark' : 'light';
        setTheme(theme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        themeSwitch.checked = theme === 'dark';
    }
});