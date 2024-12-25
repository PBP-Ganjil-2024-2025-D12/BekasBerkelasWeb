document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector(".mobile-menu-button");
    const menu = document.querySelector(".mobile-menu");
    const hamburgerIcon = document.querySelector(".hamburger-icon");
    const xIcon = document.querySelector(".x-icon");

    if (btn) {
        btn.addEventListener("click", () => {
            menu.classList.toggle("hidden");
            
            if (menu.classList.contains("hidden")) {
                hamburgerIcon.classList.remove("hidden");
                xIcon.classList.add("hidden");
            } else {
                hamburgerIcon.classList.add("hidden");
                xIcon.classList.remove("hidden");
            }
        });
    }

    const dropdownButton = document.getElementById('dropdown-button');
    const dropdownMenu = document.getElementById('dropdown-menu');
    const downArrow = document.querySelector(".down-arrow");
    const upArrow = document.querySelector(".up-arrow");
    
    // Check Implementation
    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', () => {
            dropdownMenu.classList.toggle("hidden");

            if (dropdownMenu.classList.contains("hidden")) {
                downArrow.classList.remove("hidden");
                upArrow.classList.add("hidden");
            } else {
                downArrow.classList.add("hidden");
                upArrow.classList.remove("hidden");
            }
        });        
    }
});