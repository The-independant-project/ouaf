document.addEventListener('DOMContentLoaded', () => {
  const dogs = document.querySelectorAll('.spin_target');

  dogs.forEach(wrapper => {
    const img = wrapper.querySelector('.team__badgeDog');
    wrapper.dataset.direction = '1';

    wrapper.addEventListener('click', () => {
      if (wrapper.dataset.spinning === 'true') return;

      wrapper.dataset.spinning = 'true';

      const direction = parseInt(wrapper.dataset.direction, 10);
      const totalSpins = Math.floor(Math.random() * 3) + 3; // 3 à 5 tours
      const duration = 1500; // durée totale
      const start = performance.now();
      const initialAngle = -5;


      function animateSpin(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);


        const eased = progress < 0.5
          ? 2 * progress * progress
          : -1 + (4 - 2 * progress) * progress;

        const angle = initialAngle + direction * eased * (360 * totalSpins);
        img.style.transform = `rotate(${angle}deg)`;

        if (progress < 1) {
          requestAnimationFrame(animateSpin);
        } else {
          const inertiaStart = performance.now();
          const inertiaDuration = 900;
          const inertiaAmplitude = 20 * direction;

          function animateInertia(inertiaNow) {
            const inertiaElapsed = inertiaNow - inertiaStart;
            const t = Math.min(inertiaElapsed / inertiaDuration, 1);

            const damping = Math.pow(1 - t, 2);
            const oscillation = Math.sin(t * Math.PI * 2);

            const angle = initialAngle + oscillation * inertiaAmplitude * damping;
            img.style.transform = `rotate(${angle}deg)`;

            if (t < 1) {
              requestAnimationFrame(animateInertia);
            } else {
              img.style.transform = `rotate(${initialAngle}deg)`;
              wrapper.dataset.spinning = 'false';
              wrapper.dataset.direction = direction === 1 ? '-1' : '1';
            }
          }

          requestAnimationFrame(animateInertia);
        }
      }

      requestAnimationFrame(animateSpin);
    });
  });
});