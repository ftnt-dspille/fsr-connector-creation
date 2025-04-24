---
title: "Play video"
linkTitle: "Video"
weight: 70
---

## Youtube

To display a YouTube video with this URL:

```html
https://www.youtube.com/watch?v=0RKpf3rK57I
```

Include this in your Markdown:

```html
{{</* youtube 0RKpf3rK57I */>}}
```

## Vimeo

To display a Vimeo video with this URL:

```html
https://vimeo.com/channels/staffpicks/55073825
```

Include this in your Markdown:

```html
{{</* vimeo 5073825 */>}}
```

## Local video file

To display a local video file `How_to_make_video.webm`:

Include this in your Markdown:

```Markdown
{{</* video src="How_to_make_video.webm" */>}}

```

{{< video src="How_to_make_video.webm" >}}

You can add an optional `width` too. (default `width="100%"`)
