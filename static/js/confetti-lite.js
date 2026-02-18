(() => {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;

  const colors = ['#0066cc', '#28a745', '#ffc107', '#ff6b6b', '#7c3aed'];

  function createParticle(originX, originY, spread) {
    const particle = document.createElement('span');
    const size = Math.random() * 6 + 6;
    const angle = (Math.random() - 0.5) * spread * (Math.PI / 180);
    const velocity = 10 + Math.random() * 6;
    const rotate = Math.random() * 360;
    const duration = 1000 + Math.random() * 400;

    particle.style.position = 'fixed';
    particle.style.top = `${originY}px`;
    particle.style.left = `${originX + (Math.random() - 0.5) * 200}px`;
    particle.style.width = `${size}px`;
    particle.style.height = `${size * 0.4}px`;
    particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    particle.style.opacity = '0.9';
    particle.style.transform = `translate(0, 0) rotate(${rotate}deg)`;
    particle.style.borderRadius = '2px';
    particle.style.pointerEvents = 'none';
    particle.style.transition = `transform ${duration}ms ease-out, opacity ${duration}ms linear`;
    particle.style.zIndex = 9999;

    document.body.appendChild(particle);

    requestAnimationFrame(() => {
      const dx = Math.cos(angle) * velocity * 25;
      const dy = (Math.sin(angle) + 1.5) * velocity * 25;
      particle.style.transform = `translate(${dx}px, ${dy}px) rotate(${rotate + 720}deg)`;
      particle.style.opacity = '0';
    });

    setTimeout(() => particle.remove(), duration + 200);
  }

  window.confetti = function confetti(options = {}) {
    const {
      particleCount = 100,
      spread = 70,
      origin = { x: 0.5, y: 0.2 }
    } = options;

    const originX = (origin.x ?? 0.5) * window.innerWidth;
    const originY = (origin.y ?? 0.2) * window.innerHeight;

    for (let i = 0; i < particleCount; i++) {
      createParticle(originX, originY, spread);
    }
  };
})();
