# Research reports: explain what the numbers mean for a decision

## Reader's question

What is happening, and what should happen next? Data collection and description
alone do not answer a decision-maker's question. Readers should understand the
implications from the opening rather than reinterpret every graph themselves.

## Required elements

For a new report, use this order: purpose (who needs to decide what), opening
summary with the main message and arguments, findings, proposed next actions,
data limitations, and reproducible method. Methods and limitations may be short
but must not disappear. When revising, source-preservation rules take precedence:
do not invent a recommendation, method, or certainty to fill the structure.

## Structure

Use a conclusion-first hierarchy. Readers who need only the decision can stop
after the opening; readers checking evidence can continue. Make the opening
and proposals scannable with lists or tables. Body sections usually contain a
conclusion sentence, evidence such as a table, and short explanatory prose.

- State the purpose in the first sentence, not a separate section:
  「7月の部会で解約対策を決めるため、4〜6月の解約を調べた」.
- Follow with one main-message sentence. When a decision is requested, say how
  to decide, such as 「〜を確かめてから、〜を決めるのがよい」, not just what was
  observed. Follow with two to four distinct numbered arguments, each giving
  its conclusion and key figures.
- Do not begin with definitions or methods. Define a population beside the
  first table using it; place methods near the end.
- Match body sections to the opening arguments. Use conclusion headings and
  put each section's conclusion before its numbers or table, preserving
  conditions and certainty.
- Tables work well for segments, hypotheses, and options. This report-specific
  rule overrides a general preference for prose where comparison is easier
  in a table.
- Separate fact (what happened), interpretation (what it supports), and action
  or verification (what next). Do not blur company data with analogies from
  another organization.
- Divide proposals into checks possible before the decision and options to
  select at the decision. For each option, give supporting figures, what needs
  checking, and selection conditions when the material supports them.
  Draw options from stakeholder proposals, outcomes of verification, or waiting.
  Do not invent measures, costs, periods, or expected effects. If an authorized
  author preference exists, mark it as a view and recommend at most one option.
  Routine monitoring without a decision question need not invent options.
- Put limitations and methods after proposals, but place a caveat beside the
  particular number it qualifies, not only at the end.
- Move aggregation queries and detailed exclusions to the end or an appendix.

For a follow-up investigation, explain the relationship to the previous report
just after the opening: what changed, why investigate again, which conclusions
remain, and which change. Correct earlier errors near the beginning, before
readers decide based on the conclusion.

## Quality criteria

- The opening tells the reader what to do with the findings, not just numbers.
- Attribute facts and distinguish interpretation: 「〜だった(出典: アクセス解析、
  7月集計)」 is different from 「〜と考えられる」.
- Flag outlier-driven totals, unstable small denominators, and seasonal
  comparability next to the affected numbers. Do not hide the caveat at the end.
- Explain numerical meaning when directly derivable. 「継続率は4%だった」 may be
  clarified as 「96%は継続しなかった」 when those populations are identical.
  Do not change source numbers or introduce unsupported calculations.
- Define population, exclusions such as bots, and aggregation dates beside the
  first applicable table. Check definitions before comparing successive reports.
- Allocate space by substantive change. Unchanged segments may need only
  「特に変化なし」 rather than a repeated full paragraph.

## Common failures

A report ending with 「訪問数は前月比で減少した」 leaves the reader to work out
its relevance. The opposite failure is recommending priorities beyond what the
evidence supports, contradicting the report's own caveats. Do not describe all
channels with the identical 「Aチャネルは〜だった。Bチャネルは〜だった。」
pattern. Do not compare periods whose populations or collection methods differ
without acknowledging the difference.

The most relevant principles are conclusion-first structure, supported next
actions, separation of facts and opinions, explicit uncertainty and corrections,
and uneven emphasis.

## Fictional opening and proposal

This fictional example uses the EC site そらマルシェ. Its figures are example
material only, not defaults for another report.

```markdown
# そらマルシェ 流入経路調査(2026年6月分)

7月の販促会議で SNS 導線への予算配分を決めるため、6月の流入経路を調べた。

訂正: 前号(5月分)で「検索流入は横ばい」と書いたが、集計対象に社内アクセスが
混入しておりデータの誤りだった。除外後は前月比5%減で、今号の
「2カ月連続の減少」は訂正後の数値にもとづく。

SNS 導線への予算配分は、上位1商品を除いた7月の購入率を見てから決めるのがよい。

1. 検索流入が2カ月続けて減った(71,200件、前月比 -8%)。
   総訪問数の減少(-3%)の主因である
2. SNS経由の購入率は4.6%で、サイト平均(2.0%)の2.3倍に見える
3. ただし購入の41%が上位1商品(季節限定の虫よけスプレー)で、
   除くと2.1%と平均並みになる

## 次にすべきこと

会議の前にできる検証:

- 上位1商品を除いた SNS 経由の購入率を、7月前半の分で出す

会議で選ぶ選択肢:

| 選択肢 | 支える数字 | 選ぶ条件 |
| --- | --- | --- |
| SNS 導線の予算を増やす | 購入率 4.6%(平均の2.3倍) | 1商品を除いても平均を上回るとき |
| 今の配分のまま検索流入の減少を調べる | 検索流入が2カ月連続で減少 | 除くと平均並みのとき |
```

This is an excerpt: a complete report also needs its actual findings sections,
limitations, and method. Do not treat example omissions as permission to omit
those elements from a requested complete report.

## Description versus decision support

Suppose supplied June figures are: total visits 128,400, down 3%; search visits
71,200, down 8% for the second consecutive month; SNS purchase rate 4.6% against
a 2.0% site average; 41% of SNS purchases from one product, with a 2.1% rate
when that product is excluded. The team wants to inspect that exclusion before
choosing whether to emphasize SNS.

Merely listing 128,400, 71,200, and 4.6% does not explain the decision. A faithful
account can explain that search's decline is about 6,200 visits while the total
decline is about 4,000, derived from the supplied month-over-month percentages.
Label derived values as approximate. Other channels therefore increased in
aggregate. Explain the single-product concentration before repeating the team
view as an intention, not a decision:

> チームとしては、SNS導線に力を入れるかどうかを、
> この1商品を除いた数字を見てから決めたい考えである。

Derived explanation is not permission to add unsupported causes, new measures,
or figures unrelated to the supplied data.
