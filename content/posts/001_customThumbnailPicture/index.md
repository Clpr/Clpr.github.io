---
title: "Blowfish: One cover picture for all posts"
date: 2025-07-16T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Shows how to specify cover/thumbnail picture for each post using assets without duplicate copies."

featureAsset: "img/feature_default.webp"
---


`Blowfish​` is a highly flexible framework within the `​Hugo​` ecosystem, allowing users to quickly build visually appealing websites in just minutes.
A typical Blowfish (and Hugo) website is structured around "posts" or "articles." Each post may include a cover image, commonly referred to as a "thumbnail" as demonstrated on this website.

![example_thumbnail_picture](img/feature_default.webp "An example cover/thumbnail picture")

The default ways to specify the cover picture for a post:

- Putting a picture file with substring "feature" in the same folder as the `index.md` of the post
- Use `featureimage: PICTURE_URL` to cite an online picture

While Blowfish (and Hugo) allows each post to specify its own cover image, this approach can lead to inefficiencies. Storing duplicate copies of the same image across multiple posts is unnecessary, especially when cover images are large.
A more efficient approach would be to reuse a single image (or a set of images) stored in `assets/` or another directory, rather than embedding duplicates in each post. However, this is not currently supported. Blowfish’s `featureimage` parameter only accepts remote URLs, not local assets.
This post introduces a new parameter, `featureAsset` (or a name of your choice), which allows referencing a local asset image (e.g., `featureAsset: "img/feature_default.png"`) directly in a post’s TOML front matter. This enables efficient reuse of cover images while maintaining flexibility.

This post is based on the [discussion thread](https://github.com/nunocoracao/blowfish/discussions/1672) by `@f-hollow` on GitHub.

**Idea**: We have to tell the compiler when and where to find the asset picture in the process of website building. This requries to modify the theme partial templates according to which hero style you are applying to your website.

**Fisrt**, copy `themes/blowfish/layouts/partials/article-link/` and `themes/blowfish/layouts/partials/hero/` to `layouts/partials/` folder. The files stored in `layouts/partials/` would overwrite the default Blowfish building files in the compilation process.

1. Explain: the building files in `article-link/` controls how the gallery files (named as `_index.md`) are parsed and compiled
2. Explain: the building files in `hero/` controls how the generic page/post/article files (named as `index.md`) are parsed and compiled

**Then**, let's check the building files in `layouts/partials/article-link/`. In the Blowfish version of writing this post (2.88.1), there should be 3 files:

1. `simple.html`: for `showCards=false` in the `[list]` section of the TOML file `config/_default/params.toml`. This building file works for the case where the posts are listed as top-to-bottom lists.
2. `card.html` and `card-related.html`: for `showCards=true`. These builidng files works for the case where the posts are organized as cards.

WLOG, let's check `simple.html`. Reading this building file, one can quickly locate the related shortcodes that check and set up the cover pictures. e.g.

```html {lineNos=inline}
{{- with $.Params.images -}}
{{- range first 6 . }}
<meta property="og:image" content="{{ . | absURL }}" />{{ end -}}
{{- else -}}
{{- $images := $.Resources.ByType "image" -}}
{{- $featured := $images.GetMatch "*feature*" -}}

{{- if not $featured }}{{ $featured = $images.GetMatch "{*cover*,*thumbnail*}" }}{{ end -}}
{{ if and .Params.featureimage (not $featured) }}
{{- $url:= .Params.featureimage -}}
{{ $featured = resources.GetRemote $url }}
{{ end }}
{{- if not $featured }}{{ with .Site.Params.defaultFeaturedImage }}{{ $featured = resources.Get . }}{{ end }}{{ end -}}
{{ if .Params.hideFeatureImage }}{{ $featured = false }}{{ end }}
{{- with $featured -}}
{{ if or $disableImageOptimization (strings.HasSuffix $featured ".svg")}}
    {{ with . }}
    <div class="{{ $articleImageClasses }}" style="background-image:url({{ .RelPermalink }});"></div>
    {{ end }}
    {{ else }}
    {{ with .Resize "600x"  }}
    <div class="{{ $articleImageClasses }}" style="background-image:url({{ .RelPermalink }});"></div>
    {{ end }}
    {{ end }}
{{- else -}}
{{- with $.Site.Params.images }}
<meta property="og:image" content="{{ index . 0 | absURL }}" />{{ end -}}
{{- end -}}
{{- end -}}
```

This shortcode block basiclly: first search if there exists a file with substring `feature`, `cover`, `thumbnail` in the same folder; if not, then check if `featureimage` parameter is set in the TOML front matter; if not, then use default feature picture (set in `config/_default/params.toml`); if no default picture, then hide the cover picture.

Then, we need to modify this block by inserting the following condition codes between line 6 and 8 (to prioritize our specification):

```html {lineNos=inline}
{{ if and .Params.featureAsset (not $featured) }}
    {{- $genericImage:= .Params.featureAsset -}}
    {{ $featured = resources.Get $genericImage }}
{{ end }}
```

This shortcode block basically does: check if there is a parameter `featureAsset` in the TOML front matter; if yes and the `featured` value has not been successfully set yet, then set it using the provided path (`resources.Get RELATIVE_PATH` refers to the `assets/` folder which should be the root folder of the relative path).

After understanding the idea, one can modify all the other building files in the same way.
Then, a Markdown post file (not the gallery file) can have a TOML front matter like:

```toml
---
title: "Blowfish: One cover picture for all posts"
date: 2025-07-16T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Shows how to specify cover/thumbnail picture for each post using assets without duplicate copies."

featureAsset: "img/feature_default.webp"
---
```
