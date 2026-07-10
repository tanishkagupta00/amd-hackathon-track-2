# Testing Guide - Homepage Enhancements

## 🚀 Quick Start

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies (if needed)
```bash
npm install
```

### 3. Start Development Server
```bash
npm run dev
```

The app will typically start on `http://localhost:5173`

## ✅ Testing Checklist

### Orb Animation Tests

#### Test 1: Fixed Position
- [ ] Open the homepage
- [ ] Scroll down the page
- [ ] **Expected**: Orb stays centered and doesn't move
- [ ] **Success Criteria**: Orb remains in viewport center regardless of scroll position

#### Test 2: Particle Burst Effect
- [ ] Locate the orb in the center of the screen
- [ ] Hover your mouse over the orb
- [ ] **Expected**: Circle circumference disintegrates into 80 particles
- [ ] **Expected**: Particles burst outward in a radial pattern
- [ ] **Expected**: Smooth animation with turbulent motion
- [ ] Move mouse away from orb
- [ ] **Expected**: Particles smoothly collapse back into circle

#### Test 3: Hover Transitions
- [ ] Hover over orb and watch the transition
- [ ] **Expected**: Smooth burst-out animation (~0.08 speed)
- [ ] Remove hover
- [ ] **Expected**: Faster collapse animation (~0.12 speed)
- [ ] **Success Criteria**: No jittery or abrupt movements

#### Test 4: Rotation During Hover
- [ ] Hover over orb for several seconds
- [ ] **Expected**: Orb gradually rotates while hovered
- [ ] Remove hover
- [ ] **Expected**: Rotation stops but position is maintained

### Homepage Content Tests

#### Test 5: Hero Section
- [ ] Check headline is visible and gradient text renders correctly
- [ ] Verify "AMD Developer Hackathon · Track 2" badge is visible
- [ ] Check stats grid shows: "4 Styles", "Multi-Stage", "High Accuracy"
- [ ] Click "Get Started" button
- [ ] **Expected**: Navigate to `/app` route

#### Test 6: Scrolling Experience
- [ ] Scroll through entire page
- [ ] **Expected**: Smooth scroll behavior (not instant jumps)
- [ ] **Expected**: Content scrolls while orb stays fixed
- [ ] **Expected**: No content overlapping issues

#### Test 7: Navigation Bar
- [ ] Scroll down the page
- [ ] **Expected**: Navbar stays at top (sticky)
- [ ] **Expected**: Backdrop blur effect visible
- [ ] Click GitHub link
- [ ] **Expected**: Opens GitHub repo in new tab
- [ ] Click "Launch App" button
- [ ] **Expected**: Navigate to `/app` route

#### Test 8: Section Visibility
- [ ] Scroll through and verify all sections are present:
  - [ ] Hero Section
  - [ ] Core Features (3 cards)
  - [ ] How It Works (4 steps)
  - [ ] Key Features (6 items)
  - [ ] Tech Stack (8 technologies)
  - [ ] Why CaptionForge (4 points)
  - [ ] CTA Section
  - [ ] Footer

#### Test 9: Interactive Elements
- [ ] Hover over feature cards
- [ ] **Expected**: Cards lift up slightly (translate-y)
- [ ] **Expected**: Border color changes
- [ ] Hover over tech stack badges
- [ ] **Expected**: Cyan border glow appears
- [ ] Hover over CTA button
- [ ] **Expected**: Scale increase and shadow glow

#### Test 10: Responsive Design
- [ ] Resize browser window to mobile size (~375px width)
- [ ] **Expected**: Layout adapts to single column
- [ ] **Expected**: Text remains readable
- [ ] **Expected**: Buttons remain accessible
- [ ] Test tablet size (~768px width)
- [ ] **Expected**: Grid layouts adjust appropriately

### Performance Tests

#### Test 11: Animation Performance
- [ ] Open browser DevTools (F12)
- [ ] Go to Performance tab
- [ ] Start recording
- [ ] Hover over orb multiple times
- [ ] Stop recording
- [ ] **Expected**: Consistent 60 FPS
- [ ] **Expected**: No dropped frames during animation

#### Test 12: Page Load
- [ ] Refresh page (Ctrl+R or Cmd+R)
- [ ] **Expected**: Orb loads and renders within 1-2 seconds
- [ ] **Expected**: No console errors
- [ ] **Expected**: All content loads progressively

### Cross-Browser Tests

#### Test 13: Chrome/Edge
- [ ] Test all above features in Chrome or Edge
- [ ] **Expected**: All features work perfectly

#### Test 14: Firefox
- [ ] Test all above features in Firefox
- [ ] **Expected**: All features work perfectly

#### Test 15: Safari (if available)
- [ ] Test all above features in Safari
- [ ] **Expected**: All features work perfectly

## 🐛 Common Issues & Solutions

### Issue 1: Orb Not Visible
**Symptoms**: Can't see the orb on the page

**Solutions**:
- Check browser console for WebGL errors
- Verify browser supports WebGL (visit `https://get.webgl.org/`)
- Try refreshing the page
- Check if container has proper dimensions

### Issue 2: Particles Not Bursting
**Symptoms**: Hover doesn't trigger particle effect

**Solutions**:
- Verify `pointer-events` CSS is set correctly
- Check if hover intensity is set too low
- Inspect element to ensure hover area is correct
- Try clicking directly on orb to test interaction

### Issue 3: Scroll Issues
**Symptoms**: Page doesn't scroll smoothly or orb scrolls with page

**Solutions**:
- Clear browser cache
- Check if CSS was properly updated
- Verify `position: fixed` is applied to orb container
- Check z-index layering

### Issue 4: Performance Issues
**Symptoms**: Laggy animations or low FPS

**Solutions**:
- Close other browser tabs
- Disable browser extensions
- Check GPU acceleration is enabled
- Reduce `hoverIntensity` value

### Issue 5: Broken Layout on Mobile
**Symptoms**: Content overlaps or doesn't fit on mobile

**Solutions**:
- Check Tailwind responsive classes are correct
- Test with device emulation in DevTools
- Verify viewport meta tag is present
- Check for hardcoded widths

## 📊 Expected Results Summary

| Test | Expected Result | Status |
|------|----------------|--------|
| Fixed Orb | Stays centered while scrolling | ⏳ |
| Particle Burst | 80 particles burst outward on hover | ⏳ |
| Smooth Transition | Gradual burst/collapse animations | ⏳ |
| Rotation | Rotates during hover | ⏳ |
| Smooth Scroll | Page scrolls smoothly | ⏳ |
| Navigation | Buttons navigate correctly | ⏳ |
| All Sections | 8 sections visible and styled | ⏳ |
| Hover Effects | Cards and buttons respond to hover | ⏳ |
| Responsive | Works on mobile, tablet, desktop | ⏳ |
| Performance | 60 FPS animations | ⏳ |

## 🎯 Acceptance Criteria

✅ **PASS** if:
- Orb is fixed and doesn't scroll with page content
- Particle burst effect works smoothly on hover
- Particles transition back to circle seamlessly
- All 8 homepage sections are visible and professional
- Page scrolls smoothly without janky behavior
- All interactive elements respond correctly
- No console errors
- 60 FPS during animations

❌ **FAIL** if:
- Orb scrolls with the page
- Particle effect doesn't work or is glitchy
- Layout is broken or unprofessional
- Performance is poor (< 30 FPS)
- Content is missing or misaligned
- Console shows critical errors

## 🔧 Developer Tools Tips

### Check Animation FPS
1. Open DevTools (F12)
2. Go to Performance tab
3. Enable "Show FPS meter"
4. Observe FPS counter in top-right

### Inspect WebGL
1. Open DevTools Console
2. Type: `!!document.createElement('canvas').getContext('webgl')`
3. Should return `true`

### Debug Hover Events
1. Open DevTools Elements tab
2. Select orb container
3. Go to Event Listeners tab
4. Verify `mousemove` and `mouseleave` are registered

### Check CSS Application
1. Right-click on orb container
2. Select "Inspect"
3. Verify in Styles panel:
   - `position: fixed`
   - `z-index: 0`
   - `pointer-events: auto` on child

## 📝 Reporting Issues

If you find any issues, please report with:
- Browser name and version
- Operating system
- Screen size/resolution
- Steps to reproduce
- Screenshot or video
- Console errors (if any)

---

**Last Updated**: After homepage enhancements implementation
**Testing Environment**: Chrome, Firefox, Safari
**Status**: Ready for testing ✅
