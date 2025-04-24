---
title: Color Text
weight: 50
---

{{% notice info %}}
If your local preview runs into error with this feature, follow the two steps
outlined in section [Upgrade](../chapter-01-start/05-upgrade.html) in chapter 1.
{{% /notice %}}

To add color to some text, use colortext short code:

```go
The apple is {{%/* colortext red */%}}RED{{%/* /colortext */%}}
```

The apple is {{% colortext red %}}RED{{% /colortext %}}

```go
The brand color of Fortinet is {{%/* colortext "#da291c" */%}}Fortinet RED{{%/* /colortext */%}}
```

The brand color of Fortinet is {{% colortext "#da291c" %}}Fortinet RED{{% /colortext %}}
