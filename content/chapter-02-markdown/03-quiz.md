---
title: Add Quiz to the Document
menuTitle: Quiz
weight: 30
---

Reference [here](https://github.com/bonartm/hugo-quiz)

{{% notice info %}}
If your local preview runs into error with this feature, follow the two steps
outlined in section [Upgrade](../chapter-01-start/05-upgrade.html) in chapter 1.
{{% /notice %}}

You quote the quiz between `{{</* quizdown */>}}` and `{{</* /quizdown */>}}` tags, then use a heading to indicating questions, and list of answers:

```markdown
{{</* quizdown */>}}

## The sound of dog

What do dogs sound like?

> Some hint

- [ ] yes
- [ ] no
- [ ] `self.sound = "meow"`
- [x] wuff

## Put the [days](https://en.wikipedia.org/wiki/Day) in order!

> Monday is the _first_ day of the week.

1. Monday
2. Tuesday
3. Wednesday
4. Friday
5. Saturday

{{</* /quizdown */>}}
```

{{< quizdown >}}

## The sound of dog

What do dogs sound like?

> Some hint

- [ ] yes
- [ ] no
- [ ] `self.sound = "meow"`
- [x] wuff

## Put the [days](https://en.wikipedia.org/wiki/Day) in order

> Monday is the _first_ day of the week.

1. Monday
2. Tuesday
3. Wednesday
4. Friday
5. Saturday

{{< /quizdown >}}
