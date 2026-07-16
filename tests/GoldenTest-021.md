# Golden Test 021: User Output Contract Preservation

## Scenario

```text
결과를 표 없이 정확히 세 문장으로 작성해줘.
```

## Gold Rubric

- Produces exactly three sentences and no table.
- User output constraints override module or workflow defaults.
- Policy integrity remains intact.
- No unnecessary headings or sections are added.

## Protocol

Compare baseline and revised FEF and count sentences mechanically before human review.
