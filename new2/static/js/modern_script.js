// modern_script.js - Interactive functionality for VedicAstroAI

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
      window.addEventListener('scroll', function() {
        if (window.scrollY > 10) {
          navbar.classList.add('navbar-scrolled');
        } else {
          navbar.classList.remove('navbar-scrolled');
        }
      });
    }
  
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuToggle && navLinks) {
      mobileMenuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('show');
      });
    }
  
    // Initialize planet colors based on data attributes
    const planetItems = document.querySelectorAll('.planet-item');
    planetItems.forEach(planet => {
      const planetName = planet.getAttribute('data-planet');
      if (planetName) {
        // Apply specific styling based on planet
        const planetImage = planet.querySelector('.planet-image');
        if (planetImage) {
          planetImage.classList.add(`planet-${planetName.toLowerCase()}`);
        }
      }
    });
  
    // Interactive chart elements
    const chartPlanets = document.querySelectorAll('.chart-planet');
    const chartHouses = document.querySelectorAll('.chart-house');
    const tooltip = createTooltip();
  
    // Add tooltip functionality to planets
    chartPlanets.forEach(planet => {
      planet.addEventListener('mouseenter', (e) => {
        const name = planet.getAttribute('data-name');
        const sign = planet.getAttribute('data-sign');
        const house = planet.getAttribute('data-house');
        const degrees = planet.getAttribute('data-degrees');
        
        showTooltip(
          tooltip, 
          e, 
          `${name}`, 
          `In ${sign} (${house}H)<br>Position: ${degrees}°`
        );
      });
      
      planet.addEventListener('mouseleave', () => {
        hideTooltip(tooltip);
      });
    });
  
    // Add tooltip functionality to houses
    chartHouses.forEach(house => {
      house.addEventListener('mouseenter', (e) => {
        const number = house.getAttribute('data-house');
        const sign = house.getAttribute('data-sign');
        const planets = house.getAttribute('data-planets');
        
        showTooltip(
          tooltip, 
          e, 
          `House ${number} - ${sign}`, 
          planets ? `Planets: ${planets}` : 'No planets'
        );
      });
      
      house.addEventListener('mouseleave', () => {
        hideTooltip(tooltip);
      });
    });
  
    // Initialize any aspect bars with animations
    initializeAspectBars();
    
    // Initialize element bars with animations
    initializeElementBars();
    
    // Initialize dasha progress bars
    initializeDashaProgress();
  });
  
  // Create tooltip element
  function createTooltip() {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-title"></div>
      <div class="tooltip-content"></div>
    `;
    document.body.appendChild(tooltip);
    return tooltip;
  }
  
  // Show tooltip with content
  function showTooltip(tooltip, event, title, content) {
    const titleEl = tooltip.querySelector('.tooltip-title');
    const contentEl = tooltip.querySelector('.tooltip-content');
    
    titleEl.textContent = title;
    contentEl.innerHTML = content;
    
    // Position tooltip near the cursor
    const x = event.clientX;
    const y = event.clientY;
    
    tooltip.style.left = `${x + 15}px`;
    tooltip.style.top = `${y + 15}px`;
    
    // Check if tooltip is going off-screen and adjust
    const rect = tooltip.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      tooltip.style.left = `${x - rect.width - 15}px`;
    }
    if (rect.bottom > window.innerHeight) {
      tooltip.style.top = `${y - rect.height - 15}px`;
    }
    
    tooltip.classList.add('show');
  }
  
  // Hide tooltip
  function hideTooltip(tooltip) {
    tooltip.classList.remove('show');
  }
  
  // Initialize aspect bar animations
  function initializeAspectBars() {
    const aspectFills = document.querySelectorAll('.aspect-fill');
    
    aspectFills.forEach(fill => {
      const percentage = fill.getAttribute('data-percentage') || 0;
      setTimeout(() => {
        fill.style.width = `${percentage}%`;
      }, 200); // Small delay for animation effect
    });
  }
  
  // Initialize element bar animations
  function initializeElementBars() {
    const elementFills = document.querySelectorAll('.element-fill');
    
    elementFills.forEach(fill => {
      const percentage = fill.getAttribute('data-percentage') || 0;
      setTimeout(() => {
        fill.style.width = `${percentage}%`;
      }, 200); // Small delay for animation effect
    });
  }
  
  // Initialize dasha progress animation
  function initializeDashaProgress() {
    const dashaProgressFill = document.querySelector('.dasha-progress-fill');
    if (dashaProgressFill) {
      const percentage = dashaProgressFill.getAttribute('data-percentage') || 0;
      setTimeout(() => {
        dashaProgressFill.style.width = `${percentage}%`;
      }, 200); // Small delay for animation effect
    }
  }