# SEO Review Board

An AI-powered review framework with SEO content strategy evaluation.

English | [中文](README.md)

## What it does

You have a proposal (product, technical, SEO content strategy...) and want different expert perspectives to find problems.

Traditional way: Schedule meetings, wait for people, discuss, document. Takes days, costs money.

This way: AI plays PM, Operations, Tech, SEO, Design roles. Each reviews independently, debates the others, gives you a report with scoring matrix and solutions. Takes minutes.

## Why not just ask AI to review

Ask ChatGPT/Claude "review this proposal" — it tends to agree with you.

This framework:
1. **Independent review**: Each role reviews separately, no cross-reference
2. **Debate mechanism**: After seeing others' opinions, roles argue, challenge, add
3. **Quantified scoring**: Each dimension scored 1-5, not vague "looks good"
4. **Must provide solutions**: Can't just criticize, every problem needs a fix

Like a real meeting — different perspectives arguing is better than one person talking to themselves.

## Especially good at SEO content strategy review

This is what other frameworks don't have. 4 SEO-specific roles:

| Role | What it does |
|------|--------------|
| SEO Strategist | Are the keywords right? Search volume? Competition? |
| Content Quality Review | Does it meet Google E-E-A-T? Content farm risk? |
| Technical SEO Review | Page speed, mobile, structured data |
| Competitor Analyst | What are competitors doing? Traffic? Your gap? |

Plus Google policy compliance — violation = 5/5 risk score, instant rejection.

## Install

### One-liner

```bash
curl -sSL https://raw.githubusercontent.com/lennney/seo-review-board/master/install.sh | bash
```

Files go to `~/.hermes/skills/seo/ai-team-review/`.

### Hermes

```bash
hermes skills install https://raw.githubusercontent.com/lennney/seo-review-board/master/SKILL.md
# Pick "seo" category
```

### Claude Code / Codex / Other AI

```bash
# Clone repo
git clone https://github.com/lennney/seo-review-board.git

# Or just grab the core file
curl -sSL https://raw.githubusercontent.com/lennney/seo-review-board/master/SKILL.md -o SKILL.md
```

Then paste `SKILL.md` content at the start of your conversation and tell the AI "follow this framework for review".

## Usage

```
You: Review this SEO content strategy
AI: [Sends 4 SEO roles to review independently, aggregates scores, debates, provides solutions]
```

That simple. No config, no API to learn.

## Review example

gamixo.org first round review (real data):

```
| Dimension | PM | Ops | Tech | SEO | Design | Avg |
|-----------|-----|------|------|-----|--------|-----|
| Feasibility | 3 | 4 | 2 | 5 | 3 | 3.4 |
| Cost | 2 | 5 | 3 | 2 | 1 | 2.6 |
| Risk | 4 | 3 | 4 | 5 | 2 | 3.6 |
```

SEO gave 5/5 risk — "RSS aggregation + AI rewrite = content farm, Google will penalize".

This review caused us to scrap the original plan and pivot to "daily puzzle games + walkthroughs". Ran 4 iterations, score went from 3.0 to 4.2.

That's the value of multi-perspective review: blind spots one person misses, multiple perspectives catch.

## File structure

```
├── SKILL.md                    # Core methodology (8k words, 10 min read)
├── install.sh                  # One-liner installer
├── adapters/
│   ├── hermes.md              # Hermes parallel review
│   ├── claude-code.md         # Claude Code adapter
│   └── codex.md               # Codex adapter
├── scenarios/
│   ├── product-review.md      # Product review template
│   ├── seo-content-review.md  # SEO content review template
│   └── tech-review.md         # Technical review template
├── roles/
│   └── library.md             # 12 role definitions
└── references/
    ├── scoring-system.md      # Scoring system (with SEO-specific dimensions)
    ├── data-verification.md   # Data verification methods
    └── ... (other practical references)
```

## FAQ

**Q: How is this different from just asking AI to review?**

A: Ask directly, AI tends to agree. This framework makes multiple roles review independently + debate, so AI actually challenges you.

**Q: Are AI-played roles reliable?**

A: Not perfect, but better than nothing. The key is concrete scoring criteria and verification mechanisms, not letting AI freestyle.

**Q: Can I use this without Hermes?**

A: Yes. SKILL.md is a universal methodology, works with any AI tool.

**Q: How long does a review take?**

A: Simple proposals 5-10 minutes, complex ones 30 minutes (including research and debate).

## License

MIT. Use it, modify it, no need to ask.

## Contributing

Used this framework? Found issues or have ideas? Open a PR/Issue.

Especially: if you used it in a real project, share the review results so others can see real-world effectiveness.
