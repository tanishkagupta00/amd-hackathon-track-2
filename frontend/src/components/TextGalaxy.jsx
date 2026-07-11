import React, { useEffect, useRef, useState } from 'react';
import './TextGalaxy.css';

const DEFAULT_CAPTIONS = [
  'Vision', 'Reasoning', 'Style', 'AI', 'Captions', 'Extract', 
  'Context', 'Video', 'NLP', 'Transformers', 'FastAPI', 
  '</>', '{ }', '[ ]', '||', '&&', 'λ', '⌘'
];

export default function TextGalaxy({ 
  captions = DEFAULT_CAPTIONS, 
  density = 40, 
  speed = 1.0 
}) {
  const containerRef = useRef(null);
  const particlesRef = useRef([]);
  const mouseRef = useRef({ x: 0, y: 0, active: false });
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    // initialize particles
    const newParticles = [];
    for (let i = 0; i < density; i++) {
      newParticles.push({
        id: i,
        text: captions[i % captions.length],
        x: (Math.random() - 0.5) * 2500, // Clustered closer to center to ensure screen is full
        y: (Math.random() - 0.5) * 1500,
        z: 200 - (i / density) * 3200, // Evenly space them along a shorter Z axis for more density
        baseX: 0,
        baseY: 0,
        repelX: 0,
        repelY: 0,
      });
    }
    
    // Assign base positions immediately after creation
    newParticles.forEach(p => {
      p.baseX = p.x;
      p.baseY = p.y;
    });

    particlesRef.current = newParticles;
    setNodes(newParticles);

    let animationId;
    let lastTime = performance.now();

    const animate = (time) => {
      const dt = (time - lastTime) / 16.66; // normalize to 60fps
      lastTime = time;

      const { x: mx, y: my, active } = mouseRef.current;
      
      let rect;
      if (containerRef.current) {
         rect = containerRef.current.getBoundingClientRect();
      }

      particlesRef.current.forEach(p => {
        // Move forward
        p.z += 5 * speed * dt; // Slightly faster to maintain momentum
        if (p.z > 200) { // Past the camera
          p.z -= 3200; // Seamless conveyor-belt reset (preserves exact spacing)
          p.baseX = (Math.random() - 0.5) * 2500;
          p.baseY = (Math.random() - 0.5) * 1500;
          p.repelX = 0;
          p.repelY = 0;
        }

        // Mouse repulsion
        if (active && rect) {
          // simple orthographic projection approximation for mouse interaction
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          
          // Map mouse to container space - center origin
          const mouseContainerX = mx - rect.left - centerX;
          const mouseContainerY = my - rect.top - centerY;
          
          // Z scale factor to match css perspective (1000px)
          const scale = 1000 / (1000 - p.z);
          const screenX = (p.baseX + p.repelX) * scale;
          const screenY = (p.baseY + p.repelY) * scale;
          
          const dx = screenX - mouseContainerX;
          const dy = screenY - mouseContainerY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 1500) { 
            // Apply seamless inverse-distance falloff without any depth cutoffs
            // so every single text reacts smoothly based on screen distance
            const force = 120000 / (dist * dist + 3000); 
            p.repelX += (dx / dist) * force * dt;
            p.repelY += (dy / dist) * force * dt;
          }
        }
        
        // Spring back to base - buttery smooth return
        p.repelX *= 0.88;
        p.repelY *= 0.88;
        
        p.x = p.baseX + p.repelX;
        p.y = p.baseY + p.repelY;
      });

      // Force update DOM nodes directly for 60fps performance without React reconciliation
      if (containerRef.current) {
         const elements = containerRef.current.children;
         for (let i = 0; i < elements.length; i++) {
            const p = particlesRef.current[i];
            if (p) {
               elements[i].style.transform = `translate3d(${p.x}px, ${p.y}px, ${p.z}px)`;
               // fade out as they get close to camera or spawn far away
               const alpha = p.z < -2500 ? (p.z + 3000) / 500 : (p.z > 0 ? (200 - p.z) / 200 : 1);
               elements[i].style.opacity = Math.max(0, Math.min(1, alpha));
            }
         }
      }
      
      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    const handleMouseMove = (e) => {
      mouseRef.current = { x: e.clientX, y: e.clientY, active: true };
    };
    const handleMouseLeave = () => {
      mouseRef.current.active = false;
    };

    // Global listeners so it interacts no matter what is on top of it
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [captions, density, speed]);

  return (
    <div className="text-galaxy-container" ref={containerRef}>
      {nodes.map(p => (
        <div key={p.id} className="text-galaxy-particle">
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-gold to-ai-goldLight font-bold tracking-wider text-xs sm:text-sm uppercase">
            {p.text}
          </span>
        </div>
      ))}
    </div>
  );
}
