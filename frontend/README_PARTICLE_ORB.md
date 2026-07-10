# Particle Orb Component

## Overview
The `ParticleOrb` component is an enhanced version of the original `Orb` component with a **particle burst effect** that creates a stunning visual experience when users hover over it.

## Features

### 🎆 Particle Burst Animation
- **80 particles** arranged in a circular pattern
- Particles burst **outward radially** when hovering
- Smooth transition back to circle form when hover is removed
- Organic turbulent motion for natural feel

### 🔄 Smooth Transitions
- **Easing function**: 0.08 speed on hover in, 0.12 on hover out
- Circle edge gradually dissolves during burst
- Particles grow in size during burst effect
- Alpha channel boosts for particle visibility

### 🎨 Visual Effects
- Circle circumference disintegrates into individual particles
- Radial expansion with rotational movement
- Sine/cosine turbulence for wave-like motion
- Color blending between gradient colors

## Usage

```jsx
import ParticleOrb from '../components/ParticleOrb';

<ParticleOrb 
  hue={20}                    // Color hue shift (0-360)
  hoverIntensity={1.2}        // Burst intensity (0-2)
  rotateOnHover={true}        // Enable rotation during hover
  backgroundColor="#09090B"   // Background color
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `hue` | number | 0 | Color hue adjustment in degrees (0-360) |
| `hoverIntensity` | number | 0.2 | Controls burst intensity (higher = more dramatic) |
| `rotateOnHover` | boolean | true | Enable/disable rotation during hover |
| `forceHoverState` | boolean | false | Force burst state permanently |
| `backgroundColor` | string | '#000000' | Background color (hex, rgb, or hsl) |

## How the Burst Works

### Shader Logic

1. **Particle Field Generation**
   ```glsl
   // 80 particles in circular arrangement
   for(float i = 0.0; i < 80.0; i++) {
     float angle = i * 0.0785398; // 2*PI / 80
     float radius = 0.7 + burstAmount * 0.4;
     
     // Calculate particle position with burst motion
     vec2 particlePos = vec2(cos(angle), sin(angle)) * radius;
     particlePos += normalize(particlePos) * burstAmount * 0.3;
   }
   ```

2. **Smooth Transition**
   - Base circle radius expands during burst
   - Edge dissolution controlled by `burstAmount`
   - Particles fade in as circle fades out

3. **Turbulent Motion**
   ```glsl
   particlePos.x += sin(time * 2.0 + i) * burstAmount * 0.1;
   particlePos.y += cos(time * 2.0 + i) * burstAmount * 0.1;
   ```

### JavaScript Easing

```javascript
// Asymmetric easing for natural feel
const easing = effectiveHover > program.uniforms.hover.value 
  ? 0.08  // Slower burst out
  : 0.12; // Faster collapse in

program.uniforms.hover.value += 
  (effectiveHover - program.uniforms.hover.value) * easing;
```

## Integration in Homepage

The ParticleOrb is used in the Home page as a fixed background element:

```jsx
<div className="fixed top-0 left-0 w-full h-screen pointer-events-none z-0">
  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 
                  w-[800px] h-[800px] opacity-60 pointer-events-auto">
    <ParticleOrb 
      hue={20} 
      hoverIntensity={1.2} 
      rotateOnHover={true} 
      backgroundColor="#09090B" 
    />
  </div>
</div>
```

### Key CSS Classes

- `fixed`: Keeps orb in place while page scrolls
- `pointer-events-none`: Parent doesn't block clicks
- `pointer-events-auto`: Child orb responds to hover
- `z-0`: Behind content, `z-10` for scrollable content

## Performance Considerations

- **WebGL accelerated**: Runs on GPU for smooth 60fps
- **Optimized shader**: Efficient particle calculations
- **Automatic cleanup**: Resources freed on unmount
- **Canvas resize handling**: Adapts to window changes

## Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (WebKit)
- ⚠️ Requires WebGL support

## Customization Tips

### Adjust Burst Intensity
```jsx
hoverIntensity={1.5}  // More dramatic burst
hoverIntensity={0.8}  // Subtle burst
```

### Change Particle Count
Edit the shader loop:
```glsl
for(float i = 0.0; i < 120.0; i++) {  // More particles
  float angle = i * (6.283185 / 120.0);
  // ...
}
```

### Modify Colors
```jsx
hue={180}  // Cyan-heavy palette
hue={300}  // Magenta-heavy palette
```

## Troubleshooting

**Orb not visible?**
- Check opacity value (0-1)
- Ensure container has dimensions
- Verify z-index layering

**Performance issues?**
- Reduce particle count in shader
- Lower devicePixelRatio
- Disable on mobile devices

**Hover not working?**
- Check pointer-events CSS
- Verify mouse event listeners attached
- Test hover radius calculation

## Credits

Built on top of the original Orb component using:
- **OGL**: Lightweight WebGL library
- **GLSL**: OpenGL Shading Language
- **React**: Component framework
