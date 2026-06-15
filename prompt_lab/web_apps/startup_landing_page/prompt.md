# Startup Landing Page — agency-quality, one file

**Stack:** single `index.html` + Tailwind via CDN · **Est:** 10–15 min · **Output:** a landing page that looks like a funded startup's

## ✨ 1. Expectation — what you'll get
Run the prompt, answer two quick questions, and minutes later a single `index.html` opens in your browser: a dark-mode, editorial landing page for a fictional product, complete with an animated gradient-mesh hero, a sticky nav that shrinks and blurs on scroll, a feature grid with hand-drawn inline-SVG icons, pricing tiers behind a live monthly/annual toggle, testimonials, and an FAQ accordion that all actually work. Scroll-reveal animations fire as you move down the page, and every word of copy is specific to your chosen product — no lorem ipsum, no placeholder boxes. You can open it offline, drop it on any static host, or text the file to someone, and it reads like a finished, $50k agency job.

**Why it's cool:** One prompt produces real product-specific copy *and* polished, interactive motion — animated backgrounds, working toggles, scroll choreography — end to end with zero build step and zero dependencies beyond a CDN script tag.

**Use cases:** Spin up a convincing pitch mockup for a client or investor deck in the time it takes to grab coffee; add a striking, original landing page to your portfolio without licensing a template; prototype your own startup's hero-and-pricing story before committing to a real codebase; or read the generated Tailwind, IntersectionObserver, and vanilla-JS toggle code to learn how modern marketing pages are actually wired together.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Drop the prompt below into Claude Code in an empty folder, answer the 2 short setup questions (which product, which aesthetic), and it runs autonomously, self-reviewing against a checklist until the page is done, then opens it. Prerequisites: none — Tailwind loads from CDN and the page opens directly in a modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [cruip/tailwind-landing-page-template](https://github.com/cruip/tailwind-landing-page-template) · **Expected result:** [landing-page gallery](https://land-book.com/)

---

## 📋 COPY-PASTE PROMPT

```
You are building a marketing landing page as a SINGLE self-contained index.html file using
Tailwind via CDN. Vanilla JS only for interactions. No build step.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. What's the fictional product? (give me 3 options if I say "you pick" — e.g. an AI sleep coach,
   a carbon-tracking bank, a focus app — and use the one I choose)
2. Aesthetic? (sleek-dark-editorial / bright-playful / brutalist-high-energy)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Page design (write real, specific copy — no lorem ipsum):
- Sticky nav that shrinks/blurs on scroll, with smooth-scroll anchor links.
- Hero: animated gradient-mesh or aurora background (CSS/canvas), bold headline, sub, dual CTAs, a mock UI/product visual.
- Logos/social-proof strip. Feature grid (3–6 cards with icons drawn as inline SVG).
- A "how it works" 3-step section. Pricing: 3 tiers with a highlighted "popular" plan + monthly/annual toggle.
- Testimonial cards. FAQ accordion (expand/collapse). Footer with columns.
- Scroll-reveal animations (IntersectionObserver), tasteful hover states, fully responsive (mobile → desktop).
- Cohesive type scale and palette for the chosen aesthetic. Accessible contrast and focus states.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors; looks finished, not templated.
- [ ] Nav shrinks on scroll; anchor links smooth-scroll.
- [ ] Hero background is animated; CTAs are styled and obvious.
- [ ] Pricing toggle switches monthly/annual prices; FAQ accordion opens/closes.
- [ ] Scroll-reveal animations fire; all sections responsive on mobile width.
- [ ] Real, product-specific copy throughout (no placeholder text).

STOP CONDITIONS: stop when every item passes, OR after 5 self-review rounds.
Then open index.html and summarize the sections in 3 lines.
```

---

## Remix ideas
"Add a dark/light toggle." · "Add an interactive product demo in the hero." · "Generate 3 more color themes I can switch between." · "Add a contact form that validates."
