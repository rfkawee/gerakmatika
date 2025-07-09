// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Intersection Observer for fade-in animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = "running";
    }
  });
}, observerOptions);

// Observe all fade-in elements
document.querySelectorAll(".fade-in").forEach((el) => {
  el.style.animationPlayState = "paused";
  observer.observe(el);
});

// Start app function
function startApp() {
  // Cek apakah Streamlit sudah berjalan di localhost:8501
  fetch("http://localhost:8501")
    .then(() => {
      // Jika sudah berjalan, redirect ke Streamlit
      window.location.href = "http://localhost:8501";
    })
    .catch(() => {
      // Jika belum berjalan, tampilkan instruksi
      alert(`🚀 Welcome to Math Gestures AI!

            To start the application:

            1. Open Command Prompt (CMD)
            2. Navigate to your project folder
            3. Run: streamlit run main.py
            4. Wait for the browser to open automatically

            Or click OK to try opening the app directly.`);

      // Coba buka Streamlit URL
      window.open("http://localhost:8501", "_blank");
    });
}

// Add floating animation to math symbols
function createFloatingMath() {
  const symbols = ["∑", "∫", "∆", "∞", "π", "√", "α", "β", "γ"];
  const container = document.querySelector(".hero");

  symbols.forEach((symbol, index) => {
    const element = document.createElement("div");
    element.textContent = symbol;
    element.style.cssText = `
                    position: absolute;
                    font-size: 2rem;
                    color: rgba(79, 70, 229, 0.1);
                    pointer-events: none;
                    z-index: 0;
                    left: ${Math.random() * 100}%;
                    top: ${Math.random() * 100}%;
                    animation: float ${
                      3 + Math.random() * 2
                    }s ease-in-out infinite;
                    animation-delay: ${index * 0.5}s;
                `;
    container.appendChild(element);
  });
}

// Initialize floating math symbols
createFloatingMath();
