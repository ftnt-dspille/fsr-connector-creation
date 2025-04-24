---
title: Notices
menuTitle: Notices
weight: 20
---

Reference [here](https://mcshelby.github.io/hugo-theme-relearn/shortcodes/notice/index.html)

#### Note

```go
{{%/* notice style="note" */%}}
A **notice** disclaimer
{{%/* /notice */%}}
```

{{% notice style="note" %}}
A **notice** disclaimer
{{% /notice %}}

#### Tip

```go
{{%/* notice style="tip" */%}}
A **tip** disclaimer
```

{{% notice style="tip" %}}
A **tip** disclaimer
{{% /notice %}}

#### Warning

```go
{{%/* notice style="warning" */%}}
A **warning** disclaimer
{{%/* /notice */%}}
```

{{% notice style="warning" %}}
A **warning** disclaimer
{{% /notice %}}

#### Warning with Non-Default Title and Icon

```go
{{%/* notice style="warning" title="Here are dragons" icon="dragon" */%}}
A **warning** disclaimer
{{%/* /notice */%}}
```

{{% notice style="warning" title="Here are dragons" icon="dragon" %}}
A **warning** disclaimer
{{% /notice %}}

#### Warning without a Title and Icon

```go
{{%/* notice style="warning" title=" " icon=" " */%}}
A **warning** disclaimer
{{%/* /notice */%}}
```

{{% notice style="warning" title=" " icon=" " %}}
A **warning** disclaimer
{{% /notice %}}

### By Brand Colors

#### Primary with Title only

```go
{{%/* notice style="primary" title="Primary" */%}}
A **primary** disclaimer
{{%/* /notice */%}}
```

{{% notice style="primary" title="Primary" %}}
A **primary** disclaimer
{{% /notice %}}

#### Secondary with Icon only

```go
{{%/* notice style="secondary" icon="stopwatch" */%}}
A **secondary** disclaimer
{{%/* /notice */%}}
```

{{% notice style="secondary" icon="stopwatch" %}}
A **secondary** disclaimer
{{% /notice %}}

#### Accent

```go
{{%/* notice style="accent" */%}}
An **accent** disclaimer
{{%/* /notice */%}}
```

{{% notice style="accent" %}}
An **accent** disclaimer
{{% /notice %}}

### By Color

#### Blue without a Title and Icon

```go
{{%/* notice style="blue" */%}}
A **blue** disclaimer
{{%/* /notice */%}}
```

{{% notice style="blue" %}}
A **blue** disclaimer
{{% /notice %}}

#### Green with Title only

```go
{{%/* notice style="green" title="Green" */%}}
A **green** disclaimer
{{%/* /notice */%}}
```

{{% notice style="green" title="Green" %}}
A **green** disclaimer
{{% /notice %}}

#### Grey with Icon only

```go
{{%/* notice style="grey" icon="bug" */%}}
A **grey** disclaimer
{{%/* /notice */%}}
```

{{% notice style="grey" icon="bug" %}}
A **grey** disclaimer
{{% /notice %}}

#### Orange with Title and Icon

```go
{{%/* notice style="orange" title="Orange" icon="bug" */%}}
A **orange** disclaimer
{{%/* /notice */%}}
```

{{% notice style="orange" title="Orange" icon="bug" %}}
A **orange** disclaimer
{{% /notice %}}

#### Red without a Title and Icon

```go
{{%/* notice style="red" */%}}
A **red** disclaimer
{{%/* /notice */%}}
```

{{% notice style="red" %}}
A **red** disclaimer
{{% /notice %}}

### By Special Color

#### Default with Positional Parameter

```go
{{%/* notice default "Pay Attention to this Note!" "skull-crossbones" */%}}
Some serious information.
{{%/* /notice */%}}
```

{{% notice default "Pay Attention to this Note!" "skull-crossbones" %}}
Some serious information.
{{% /notice %}}

#### Transparent with Title and Icon

```go
{{%/* notice style="transparent" title="Pay Attention to this Note!" icon="skull-crossbones" */%}}
Some serious information.
{{%/* /notice */%}}
```

{{% notice style="transparent" title="Pay Attention to this Note!" icon="skull-crossbones" %}}
Some serious information.
{{% /notice %}}

### With User-Defined Color, Font Awesome Brand Icon and Markdown Title

```go
{{%/* notice color="fuchsia" title="**Hugo**" icon="fab fa-hackerrank" */%}}
Victor? Is it you?
{{%/* /notice */%}}
```

{{% notice color="fuchsia" title="**Hugo**" icon="fab fa-hackerrank" %}}
Victor? Is it you?
{{% /notice %}}
