import OrbWithCaptions from './OrbWithCaptions';

export default function CaptionOrbDemo() {
  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
      <OrbWithCaptions
        hue={0}
        hoverIntensity={0.5}
        rotateOnHover={true}
        captions={[
          'A dog sprints across a beach',
          'Wow, sand. Groundbreaking.',
          'while(fetching) { wag_tail(); }',
          'Kitten discovers a leaf, chaos ensues',
          'Urban traffic moves through golden hour',
          "Oh look, more cars. Riveting.",
        ]}
      />
    </div>
  );
}
