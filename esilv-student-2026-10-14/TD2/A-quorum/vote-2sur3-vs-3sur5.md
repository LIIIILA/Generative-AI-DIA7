## Vote 2-of-3 (panel fixe) contre 3-of-5 sur les traces du TD 1

| Question | Référence | 2-of-3 (panel fixe) | Accord | 3-of-5 | Accord | Change ? |
|---|---|---|---|---|---|---|
| C01 | 792800 | consensus 792800 (3 voix) | oui | consensus 792800 (5 voix) | oui | non |
| C02 | 590320 | consensus 590320 (2 voix) | oui | consensus 0 (3 voix) | **NON** | **oui** |
| C03 | 936350 | consensus 936350 (3 voix) | oui | consensus 936350 (5 voix) | oui | non |
| C04 | 2826250 | consensus 2826250 (3 voix) | oui | consensus 2826250 (5 voix) | oui | non |
| C05 | 38480 | consensus 38480 (3 voix) | oui | consensus 38480 (5 voix) | oui | non |
| C06 | 0 | consensus 0 (3 voix) | oui | consensus 0 (5 voix) | oui | non |
| C07 | 13970 | consensus 13970 (3 voix) | oui | consensus 13970 (5 voix) | oui | non |
| C08 | 605580 | consensus 605580 (2 voix) | oui | consensus 605580 (3 voix) | oui | non |
| C09 | 487980 | consensus 0 (2 voix) | **NON** | abstention (max 2 voix) | abstention | **oui** |
| C10 | 558980 | consensus 558980 (2 voix) | oui | consensus 558980 (4 voix) | oui | non |
| C11 | 446690 | consensus 446690 (2 voix) | oui | abstention (max 2 voix) | abstention | **oui** |
| C12 | 1666490 | consensus 1666490 (3 voix) | oui | consensus 1666490 (5 voix) | oui | non |
| C13 | 107740 | consensus 107740 (3 voix) | oui | consensus 107740 (5 voix) | oui | non |
| C14 | 0 | consensus 0 (3 voix) | oui | consensus 0 (5 voix) | oui | non |
| C15 | 168680 | consensus 168680 (2 voix) | oui | consensus 168680 (3 voix) | oui | non |
| C16 | 376740 | consensus 376740 (2 voix) | oui | consensus 376740 (4 voix) | oui | non |
| C17 | 258180 | abstention (max 1 voix) | abstention | abstention (max 2 voix) | abstention | non |
| C18 | 62480 | consensus 62480 (3 voix) | oui | consensus 62480 (4 voix) | oui | non |
| C19 | 1990 | consensus 1990 (2 voix) | oui | consensus 1990 (4 voix) | oui | non |
| C20 | 1106090 | consensus 1106090 (2 voix) | oui | consensus 1106090 (4 voix) | oui | non |

| Quorum | Consensus justes | Consensus faux | Abstentions |
|---|---|---|---|
| 2-of-3 panel fixe | 18 | 1 | 1 |
| 3-of-5 | 16 | 1 | 3 |

### Questions where moving from 2-of-3 to 3-of-5 changes the decision

**C02 (reference 590320): correct consensus becomes a wrong consensus.**
- 2-of-3: gpt-oss-120b = 590320 and qwen3.8-27b = 590320 (both `correct`) outvote north-mini-code = 0. The result is 590320 with 2 votes.
- 3-of-5: the two models added to the panel, gpt-oss-20b = 0 and dots-3-note = 0 (both `incorrect`), join north-mini-code = 0. The value 0 gets 3 votes, reaches `k = 3`, and beats the correct value (2 votes).
- The three zeros come from three different faulty SQL filters (TD 1 report, section 3.1), and each one matches no customer. They share the **value** 0, not the cause: `COALESCE(SUM(...), 0)` turns any empty filter into 0.
- Adding voters that are weak on age questions (gpt-oss-20b 3/5 and dots-3-note 1/5 on the age family in TD 1) let a correlated error win.

**C09 (reference 487980): wrong consensus becomes an abstention.**
- 2-of-3: north-mini-code = 0 and qwen3.8-27b = 0 (both `incorrect`) outvote gpt-oss-120b = 487980. The panel keeps the wrong value 0 with 2 votes.
- 3-of-5: 487980 gets 2 votes (gpt-oss-120b, gpt-oss-20b), 0 gets 2 votes (north-mini-code, qwen3.8-27b), and dots-3-note proposes 369240. No value reaches 3, so the quorum abstains.
- The higher threshold blocks the wrong answer, but it does not recover the right one.

**C11 (reference 446690): correct consensus becomes an abstention.**
- 2-of-3: gpt-oss-120b = 446690 and qwen3.8-27b = 446690 agree, so the panel keeps the correct value.
- 3-of-5: the correct value still has only 2 votes. The other three models propose three different wrong values: gpt-oss-20b = 322160, north-mini-code = 0, dots-3-note = 2504090. Nothing reaches 3, so the quorum abstains.
- This is the cost of a stricter quorum: a correct answer is lost because too few voters are reliable on this family.

### Cases with no change worth reading

- **C17: abstention in both, with an unavailable member kept in `n`.** dots-3-note returned invalid SQL (`sql_invalid`, empty value). It stays in `n = 5` without voting. 258180 gets 2 votes (gpt-oss-120b, gpt-oss-20b), and qwen = 248490 and north-mini-code = 371990 each get 1. In the 2-of-3 panel, the three values all differ.
- **C20: HTTP 429 kept in `n`.** qwen3.8-27b is `not_executed` after two 429 responses. It stays in `n = 3` without voting. 1106090 still reaches `k = 2` with gpt-oss-120b and north-mini-code, but with **no margin**: one more failure and the panel abstains. At 3-of-5, 4 of the 5 members agree.
- **C14: a retry that counts.** qwen3.8-27b got a 429 on its first attempt; its second attempt is `correct`. The vote uses the last attempt, so qwen votes 0, which is the correct value here.
- **C08, C15 (3-of-5):** the correct value reaches exactly 3 votes. Two wrong voters (north-mini-code and dots-3-note on C08; qwen and dots-3-note on C15) leave no margin.

### What we conclude (on these twenty questions only)

- **Neither quorum dominates.** 3-of-5 removes the C09 error, but it introduces the C02 error and loses C11. It answers fewer questions (17 against 19) with the same number of wrong decisions (1).
- **Both wrong consensuses share the value 0 on age questions.** A larger panel does not protect against **correlated errors**: here, faulty filters that select nobody. A deterministic check would detect that case, for example verifying that the selected population is not empty, or comparing with the reference query.
- **gpt-oss-120b alone answered 20/20 in TD 1**, so on this batch the vote does not beat the best single model. One run per cell at temperature 0 and twenty questions support a hypothesis for this batch, not a general error rate or a quorum guarantee.
