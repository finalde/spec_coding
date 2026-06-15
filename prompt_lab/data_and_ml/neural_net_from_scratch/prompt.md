# Neural Net From Scratch — backprop by hand, no frameworks

**Stack:** Python (numpy + scikit-learn for the dataset only) · **Est:** 15–25 min · **Output:** a trained digit classifier + a prediction grid PNG

## ✨ 1. Expectation — what you'll get
You end up with a real neural network trained to recognize handwritten digits — dense layers, ReLU + softmax, cross-entropy, forward pass, full backprop, and mini-batch SGD all hand-written in pure numpy with no PyTorch or TensorFlow anywhere. As it trains it streams live per-epoch train/test accuracy (climbing past 90%), and when it finishes it saves `predictions.png`: a color-coded grid of test digits, green for correct and red for wrong, that you open and read at a glance.

**Why it's cool:** Every gradient is derived by hand in the comments rather than hidden behind a library autograd call — so the finished artifact proves the backprop math is genuinely understood, not just imported.

**Use cases:** Truly learning how neural nets work by reading forward/backward passes you can trace line by line; a standout interview or portfolio piece that demonstrates the math, not just framework fluency; a teaching aid for explaining backprop and SGD with a runnable, visual result; and a minimal from-scratch base you extend with momentum, Adam, or a conv layer once the fundamentals click.

## ▶️ 2. How to run
Copy-paste-and-walk-away: drop the prompt below into Claude Code in an empty folder, answer 2 short setup questions, then it builds, trains, self-reviews, and shows results autonomously.
Prerequisites: `pip install numpy scikit-learn matplotlib` (the prompt runs this). Dataset loads offline via sklearn.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [karpathy/micrograd](https://github.com/karpathy/micrograd) · **Expected result:** [reference images](https://www.google.com/search?q=mnist+digit+predictions+grid&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are implementing a neural network FROM SCRATCH in pure Python + numpy. No deep-learning frameworks
(no torch/tensorflow/keras). Allowed deps: numpy, scikit-learn (only for the dataset + train/test split),
matplotlib (only for the result image). Run `pip install numpy scikit-learn matplotlib` yourself.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Network depth? (simple one-hidden-layer / deeper two-hidden-layer MLP)
2. Show me the backprop math derivation in comments? (yes / keep it brief)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN training, read the actual accuracy/errors,
self-review against the checklist, fix, repeat.

Design:
- Load sklearn's load_digits (8x8 images, offline). Normalize; one-hot labels; train/test split.
- Implement by hand: dense layers, ReLU + softmax, cross-entropy loss, forward pass, and full backprop
  (gradients derived in comments per my choice), mini-batch SGD with a learning rate.
- Train for enough epochs to clearly learn; print train + test accuracy each epoch (live).
- After training, render a grid of test digits with predicted vs true labels to predictions.png,
  color-coded green (correct) / red (wrong). Print final test accuracy.
- Set a fixed random seed for reproducibility. Pure-numpy gradients (no autograd).

ACCEPTANCE CHECKLIST (finish line):
- [ ] Runs end-to-end with no traceback after the pip install.
- [ ] Implements forward + backprop manually in numpy (no framework autograd anywhere).
- [ ] Test accuracy clearly improves over epochs and reaches a respectable level (aim >= 90% on digits).
- [ ] Per-epoch train/test accuracy prints live.
- [ ] predictions.png is generated with color-coded correct/wrong predictions.
- [ ] Backprop math appears in comments per my choice.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open predictions.png and tell me the final test accuracy + one thing that would improve it.
```

---

## Remix ideas
"Add momentum / Adam." · "Add a from-scratch conv layer." · "Plot the loss curve." · "Let me draw a digit and classify it live in a tiny GUI."
