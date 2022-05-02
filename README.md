# Vanilla Plus JS

This is a framework for building web frontends which are as faithful to vanilla
html/css/js as possible without forcing the developer to sacrifice significant
performance enhancements or to repeat themselves in an error-prone way. The hope
would be that as more features are implemented into the browser, this framework
could slowly be removed until it is no longer necessary.

This framework is compatible with the following content security policy:
`default-src 'self'; object-src 'none';`

This generates a static folder which can be served using any static file server,
but example configurations will only be given for Nginx.

## Folder Structure

A vanillaplusjs project is assumed to be structured as follows:

```
src/
    public/
        (all your html/js/css files can go here or in subfolders)
        img/
            (most images go here, see Images)
        assets/
            (particularly large non-image files go here)
        js/
            (all your js files go here or in subfolders)
        partials/
            (html templates go here)
out/
    (overwritten by vanillaplusjs)
    www/
        (this is the folder that is served that you can copy in your CI/CD)
artifacts/
    (overwritten by vanillaplusjs)
vanillaplusjs.json (configuration)
```

You should exclude `out/` from your repository via gitignore. It's recommended
to include `artifacts/` in your repository, as it may take a large amount of
memory to produce (e.g., cropping images). You will need to use git-lfs for this.
The recommended `.gitattributes` are

```txt
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
src/public/assets/* filter=lfs diff=lfs merge=lfs -text
```

## Running

The general concept for setup, once you have a virtual environment, is

```bash
vanillaplusjs init
```

Then to build and run, automatically watching for changes, it's

```bash
vanillaplusjs dev 8888 --watch
```

Or to just build it's

```bash
vanillaplusjs build
```

Or to just run it's

```bash
vanillaplusjs run 8888
```

## Features

### Cache-busting

Projects all need to update themselves occassionally. When they are updated,
the point is that clients receive the updated versions relatively quickly. However,
we also don't want to force each client to download the entire js tree on every
page load - that would dramatically increase server load and bandwidth and reduce
page load speed on the client.

This project will recursively calculate stable hashes of all imported or preloaded
javascript and css files and append them to all import URLs. So for example,

```html
<html>
<head>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>Test</body>
</html>
```

will be replaced with something like

```html
<html>
<head>
    <link rel="stylesheet" href="css/style.css?v=7e2541f06a8d1f1e2806a3634186917922a219a1b54b76cf04da636fbb7faf87&pv=1">
</head>
<body>Test</body>
</html>
```

This applies to link tags, script tags, and imports within javascript modules. You
should configure your reverse proxy to add cache control headers when there is an
exact match of path, the `v` query parameter, and `pv` query parameter on js/css
files. For example, in nginx

```conf
# ... omitting standard boilerplate ...
location ~* \.(js|css) {
    if ($args ~ "^v=[^&]+(&pv=[^&]+)?$") {
        add_header Cache-Control "public, max-age=31536000";
    }
}
```

### Image preprocessing

A very common task on the web is serving images. When serving images they should
be transcoded to common web formats and compressed as much as possible. This
reduces server load and bandwidth, while reducing page size. The effect can be
extremely dramatic.

Without any tooling this is very tedious and error prone. This project uses
Pillow to perform the image preprocessing, and stores the results in the
`artifacts/` folder. The image preprocessing will take advantage of multiple
cores, but by nature can still be slow. Hence we ensure that the artifacts
folder is byte-for-byte reproducible, thus it can be easily included in your
repository, and then just downloaded by your CI/CD pipeline rather than
regenerated from scratch.

The `artifacts/` folder will contain more images than are ultimately served via
the `out/www` folder. Our image processor is deterministic, but it does need to
sample different compression levels to find the best one for a given image.

Our image processing will also handling cropping an image using a `cover-fit`
algorithm. In the most basic case, to render a 375x370 image, it would look
like the following:


```html
<html>
<head>
    <title>Image Test</title>
</head>
<body>
    <!--[IMAGE /img/hero/mobile.jpg 375 370]-->
</body>
</html>
```

Which will generate something like the following:

```html
<html>
<head>
    <title>Image Test</title>
</head>
<body>
    <picture><source srcset="/img/hero/mobile/375x370-100.webp 375w, /img/hero/mobile/562x555-85.webp 562w, /img/hero/mobile/750x740-85.webp 750w, /img/hero/mobile/937x925-75.webp 937w, /img/hero/mobile/1125x1110-75.webp 1125w, /img/hero/mobile/1312x1295-75.webp 1312w, /img/hero/mobile/1500x1480-75.webp 1500w, /img/hero/mobile/1687x1665-75.webp 1687w, /img/hero/mobile/1875x1850-75.webp 1875w" type="image/webp"><img width="375" height="370" loading="lazy" src="/img/hero/mobile/375x370-100.jpeg" srcset="/img/hero/mobile/375x370-100.jpeg 375w, /img/hero/mobile/562x555-85.jpeg 562w, /img/hero/mobile/750x740-85.jpeg 750w, /img/hero/mobile/937x925-85.jpeg 937w, /img/hero/mobile/1125x1110-85.jpeg 1125w, /img/hero/mobile/1312x1295-85.jpeg 1312w, /img/hero/mobile/1500x1480-85.jpeg 1500w, /img/hero/mobile/1687x1665-85.jpeg 1687w, /img/hero/mobile/1875x1850-85.jpeg 1875w"></picture>
</body>
```

Notice how it includes both webp and jpeg files and will have the browser select
the appropriate resolution based on the screen width.

You can also control the crop by specifying a minimum crop for any of the sides.
If the source image is 5000x5000, the following will ensure we only use the
bottom 3600 pixels before resizing in the final image:

```html
<html>
<head>
    <title>Image Test</title>
</head>
<body>
    <!--[IMAGE /img/hero/mobile.jpg 375 370 cover {"min_top_crop": 1400}]-->
</body>
</html>
```

This is typically used as a last resort when the image crop is important for the
legibility of the page, and so you need to use many different crops at different
breakpoints. Typically this comes up for full bleed images with text on them,
where the text has to go over a particular part of the image to have enough
contrast.

#### Static images in javascript

It is sometimes helpful to be able to control images in javascript, but still
take advantage of the preprocessing described above. For this purpose, we
treat the following file special: `src/public/js/modules/kit/images/_static_images.json`
and we will use it to produce `src/public/js/modules/kit/images/_static_images.js`

Example:

```json
[
    {
        "slug": "admin-portal-page-users",
        "filepath": "/img/admin/portal/users.jpg",
        "width": 219,
        "height": 219
    }
]
```

will generate something like

```js
/* boilerplate above removed */

const REPRESENTATIONS_BY_SLUG = {
    "admin-portal-page-users": {
        jpeg: [
            new ImageRepresentation("/img/admin/portal/users/219x219-100.jpeg", 219, 219),
            new ImageRepresentation("/img/admin/portal/users/328x328-100.jpeg", 328, 328),
            new ImageRepresentation("/img/admin/portal/users/438x438-100.jpeg", 438, 438),
            new ImageRepresentation("/img/admin/portal/users/547x547-85.jpeg", 547, 547),
            new ImageRepresentation("/img/admin/portal/users/657x657-85.jpeg", 657, 657),
            new ImageRepresentation("/img/admin/portal/users/766x766-85.jpeg", 766, 766),
            new ImageRepresentation("/img/admin/portal/users/876x876-85.jpeg", 876, 876),
            new ImageRepresentation("/img/admin/portal/users/985x985-85.jpeg", 985, 985),
            new ImageRepresentation("/img/admin/portal/users/1095x1095-85.jpeg", 1095, 1095),
            new ImageRepresentation("/img/admin/portal/users/1204x1204-85.jpeg", 1204, 1204),
            new ImageRepresentation("/img/admin/portal/users/1314x1314-85.jpeg", 1314, 1314),
            new ImageRepresentation("/img/admin/portal/users/1423x1423-85.jpeg", 1423, 1423),
            new ImageRepresentation("/img/admin/portal/users/1533x1533-85.jpeg", 1533, 1533),
        ],
        webp: [
            new ImageRepresentation("/img/admin/portal/users/219x219-lossless.webp", 219, 219),
            new ImageRepresentation("/img/admin/portal/users/328x328-lossless.webp", 328, 328),
            new ImageRepresentation("/img/admin/portal/users/438x438-100.webp", 438, 438),
            new ImageRepresentation("/img/admin/portal/users/547x547-100.webp", 547, 547),
            new ImageRepresentation("/img/admin/portal/users/657x657-85.webp", 657, 657),
            new ImageRepresentation("/img/admin/portal/users/766x766-85.webp", 766, 766),
            new ImageRepresentation("/img/admin/portal/users/876x876-85.webp", 876, 876),
            new ImageRepresentation("/img/admin/portal/users/985x985-85.webp", 985, 985),
            new ImageRepresentation("/img/admin/portal/users/1095x1095-85.webp", 1095, 1095),
            new ImageRepresentation("/img/admin/portal/users/1204x1204-85.webp", 1204, 1204),
            new ImageRepresentation("/img/admin/portal/users/1314x1314-85.webp", 1314, 1314),
            new ImageRepresentation("/img/admin/portal/users/1423x1423-85.webp", 1423, 1423),
            new ImageRepresentation("/img/admin/portal/users/1533x1533-75.webp", 1533, 1533),
        ],
    },
};

/* boilerplate below removed */
```

which can be used as in the following example

```html
<!DOCTYPE html>
<html>

<head>
    <title>Images</title>
    <style>
        .example-image {
            width: 100%;
            max-width: 590px;
            height: 425px;
            overflow: hidden;
        }

        .object-fit-cover {
            object-fit: cover;
        }
    </style>
</head>

<body>
    <h2>Managed image</h2>
    <div class="example-image" id="managedImage1"></div>

    <script type="module">
        import { getStaticImageView } from '/js/modules/kit/images/index.js';

        const lazy = true;
        const debug = true;
        const view = getStaticImageView('admin-portal-page-users', ['example-image'], 'alt text', lazy, debug);
        view.element = document.getElementById('managedImage1');
        view.recreate();
    </script>
</body>

</html>
```

### Outlining js/css

Vanillaplusjs is expected to be run under the strictest content security policy,
and to facilitate this will automatically outline scripts and stylesheets into
their own separate files which are imported appropriately.

It's recommended that only test scripts or _very_ small script tags utilize
this, but it does avoid CSP issues causing code to work when running locally
that fails when deployed.

### Templates

Some parts of the HTML are quite repetitive. This library makes no effort
to completely remove the boilerplate and does prefer clarity over brevity,
however, some amount of DRY is necessary to keep the code readable.
Extremely basic HTML templating is supported with constant variables.

The template file should go in the `partials` subdirectory of `public`
and works as follows:

index.html

```html
<!DOCTYPE html>
<html>
<head>
    <!--[IMPORT /partials/head/standard.html "Try it Now"]-->
</head>
<body>
</body>
</html>
```

src/public/partials/head/standard.html

```html
<title>
    <!--[ARG 0 "Default Title"]-->
</title>
<meta charset="utf-8">
```

### External dependencies

Although `vanillaplusjs` is not intended for applications with a large number
of external dependencies (and does not support NPM), it is still sometimes
appropriate to include some. This will handle downloading the dependencies and
caching them locally, and the dependencies will be served directly.

We only support the single-file exports of file.

An example of a meaningful dependency is bootstrap. Bootstrap's CSS files are
not CSP-friendly as they contain inline SVGs. The following setting will detect
those SVGs and seamlessly outline them to be served separately.

```json
{
    "dependencies": {
        "js": {
            "bootstrap": {
                "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
                "integrity": "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
            }
        },
        "css": {
            "bootstrap": {
                "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
                "integrity": "sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3",
                "clean_data_src": true
            }
        }
    }
}
```

The files can be imported as follows:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Bootstrap</title>
    <!--[IMPORT css bootstrap]-->
</head>
<body>
    <div class="container my-5">
        <h1>Bootstrap</h1>
        <p>This is a bootstrap page</p>
    </div>

    <!--[IMPORT js bootstrap]-->
</body>
</html>
```

### Canonical URLs

For SEO purposes it's often necessary to set a canonical URL for a page.
These URLs can't be reliably specified via relative URLs. This is a bit
of a pain if you want to be able to change the domain name of the site,
e.g., to facilitate test environments.

Hence the preprocessor makes these easier to work with. For the most
common case where the canonical url should just be the url where the
file would be accessed using a standard static file server, just omit
the href:

```html
<link rel="canonical">
```

an the tag will be replaced with the full url include the file extension for you:

```html
<link href="https://example.com/account.html" rel="canonical">
```

Alternatively, you can specify the relative path:


```html
<link href="/" rel="canonical">
```

becomes

```html
<link href="https://example.com/" rel="canonical">
```

### CSS Nesting

CSS without nesting can quickly be painful if you want to support the main
browsers. We support a very simplistic nesting system. We assume you have a
`/css/main.css` file which will act as the default source of imports. In that
file you can do:

```css
.unstyle {
    appearance: none;
    border: none;
    box-shadow: none;
    /* etc */
}

.button {
    /*! PREPROCESSOR: import .unstyle */
    /* etc */
}
```

For colors and other variables it's recommended you use CSS custom properties.

### Icons

Icons with a strict CSP can also be somewhat painful to use. We have a specific
CSS preprocessor action for dealing with icons, supposing that you follow a
specific naming convention.

Suppose you have an SVG icon for a navbar toggler, which we will call
`navbar-toggler.svg`, and this is a pretty simplistic svg: it has exactly one
color in it. Now also suppose that you also have defined CSS variables following
the given pattern on the `:root` selector in the `src/public/css/main.css` file:

```css
:root {
    --col-primary: #333;
    --col-primary-dark: #000;
    --col-primary-light: #666;
    --icon-size-large: 1.5rem;
    --icon-size-medium: 1rem;
    --icon-size-small: 0.75rem;
}
```

Lets assume the svg is specified in `primary`, ie., the only color in the file
is `#333` (`--col-primary`).

If the icon is stored at `src/public/img/icons/navbar-toggler.svg`, then in CSS
you may use the following preprocessor command:

```css
/*! PREPROCESSOR: icon navbar-toggler primary all-colors all-sizes */
```

and it will generate the following classes:

- `.icon-navbar-toggler-large-primary`
- `.icon-navbar-toggler-medium-primary`
- `.icon-navbar-toggler-small-primary`
- `.icon-navbar-toggler-large-primary-dark`
- `.icon-navbar-toggler-medium-primary-dark`
- `.icon-navbar-toggler-small-primary-dark`
- `.icon-navbar-toggler-large-primary-light`
- `.icon-navbar-toggler-medium-primary-light`
- `.icon-navbar-toggler-small-primary-light`
- `.icon-btn-navbar-toggler-large`
- `.icon-btn-navbar-toggler-medium`
- `.icon-btn-navbar-toggler-small`

Which can be used as follows:

To just show the icon in html:

```html
<span>Hello, heres the toggler: <span class="icon-navbar-toggler-large-primary"></span></span>
```

Or you can create a button which will have hover and disabled colors:

```html
<button class="icon-btn-navbar-toggler-large" title="Toggle Navigation">
    <span class="icon-btn--icon"></span>
</button>
```

You can instead specify the exact colors or sizes you want to generate, which is
particularly useful if you have a lot of colors, and you can suppress the button
class

```css
/*! PREPROCESSOR: icon navbar-toggler primary ["primary-dark"] all-sizes no-btn */
```

would only generate the `primary-dark` icon color, and would do so for all the
sizes specified.

In case you need it, such as to reference the icon in other css, the
large primary-dark file would be at
`/img/icons/navbar-toggler/large/primary-dark.svg`
