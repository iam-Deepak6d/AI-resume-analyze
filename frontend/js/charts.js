/* ==========================================================================
   TalentLens AI - Canvas Radar Chart & Visual Metrics
   ========================================================================== */

class RadarChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.labels = ['Frontend', 'Backend', 'Databases', 'Cloud & DevOps', 'Algorithms & AI'];
    this.animationProgress = 0;
  }

  render(dataScores) {
    if (!this.canvas) return;
    const scores = [
      dataScores.Frontend || 30,
      dataScores.Backend || 30,
      dataScores.Databases || 30,
      dataScores['Cloud & DevOps'] || 30,
      dataScores['Algorithms & AI'] || 30
    ];

    // High DPI scaling
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 45;
    const sides = this.labels.length;

    // Animate drawing
    let start = null;
    const duration = 1000;

    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const elapsed = timestamp - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // easeOutCubic

      this.ctx.clearRect(0, 0, width, height);

      // Draw background concentric web polygons (20%, 40%, 60%, 80%, 100%)
      const levels = 5;
      for (let l = 1; l <= levels; l++) {
        const r = (radius / levels) * l;
        this.ctx.beginPath();
        for (let i = 0; i < sides; i++) {
          const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
          const x = centerX + r * Math.cos(angle);
          const y = centerY + r * Math.sin(angle);
          if (i === 0) this.ctx.moveTo(x, y);
          else this.ctx.lineTo(x, y);
        }
        this.ctx.closePath();
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
      }

      // Draw axis spokes
      for (let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);

        this.ctx.beginPath();
        this.ctx.moveTo(centerX, centerY);
        this.ctx.lineTo(x, y);
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        this.ctx.stroke();

        // Draw labels
        const labelX = centerX + (radius + 22) * Math.cos(angle);
        const labelY = centerY + (radius + 22) * Math.sin(angle);
        this.ctx.font = '600 11px "Plus Jakarta Sans", sans-serif';
        this.ctx.fillStyle = '#94a3b8';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(this.labels[i], labelX, labelY);
      }

      // Draw Target Industry Benchmark polygon (dashed line)
      this.ctx.beginPath();
      this.ctx.setLineDash([4, 4]);
      for (let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
        const benchmarkScore = 80;
        const r = (radius * (benchmarkScore / 100));
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) this.ctx.moveTo(x, y);
        else this.ctx.lineTo(x, y);
      }
      this.ctx.closePath();
      this.ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();
      this.ctx.setLineDash([]); // reset dash

      // Draw Candidate Animated Polygon
      this.ctx.beginPath();
      for (let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
        const currentScore = scores[i] * ease;
        const r = (radius * (currentScore / 100));
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) this.ctx.moveTo(x, y);
        else this.ctx.lineTo(x, y);
      }
      this.ctx.closePath();

      // Glowing fill
      const grad = this.ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, radius);
      grad.addColorStop(0, 'rgba(6, 182, 212, 0.45)');
      grad.addColorStop(1, 'rgba(99, 102, 241, 0.15)');
      this.ctx.fillStyle = grad;
      this.ctx.fill();

      this.ctx.strokeStyle = '#06b6d4';
      this.ctx.lineWidth = 2.5;
      this.ctx.stroke();

      // Draw point markers
      for (let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
        const currentScore = scores[i] * ease;
        const r = (radius * (currentScore / 100));
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);

        this.ctx.beginPath();
        this.ctx.arc(x, y, 4, 0, Math.PI * 2);
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fill();
        this.ctx.strokeStyle = '#6366f1';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
      }

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }
}

// Animated score counter utility
function animateNumber(elementId, targetValue, duration = 1200) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (targetValue - start) * ease);
    el.textContent = current;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = targetValue;
    }
  }

  requestAnimationFrame(update);
}
