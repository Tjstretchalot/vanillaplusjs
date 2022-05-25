# Vanilla Plus JS

[https://vanillaplusjs.com/](https://vanillaplusjs.com/)

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
vanillaplusjs dev --port 8888 --watch
```

Or to just build it's

```bash
vanillaplusjs build
```

Or to just run (not suitable at all for production) it's

```bash
vanillaplusjs run --port 8888
```

Note that `dev` will build using `vanillaplusjs build --dev` which
may behave very slightly differently than `vanillaplusjs build`;
in particular, see the Constants section.

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

The image processor is deterministic, but it does need to sample different
compression levels to find the best one for a given image. The trade-off
for compression vs accuracy is configurable in `vanillaplusjs.json`.

Our image processing will also handling cropping an image using a `cover-fit`
algorithm. In the most basic case, to render a 375x370 image, it would look
like the following:


```html
<html>
<head>
    <title>Image Test</title>
</head>
<body>
    <!--[IMAGE: /img/hero/mobile.jpg 375 370]-->
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
    <!--[IMAGE: /img/hero/mobile.jpg 375 370 cover {"pre_top_crop": 1400}]-->
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
take advantage of the preprocessing described above. For this purpose we will
handle the files with the extension `.images.json` as intending to produce a
file called `.images.js`. The JSON file should be in the following format:

```json
{
    "img1": {
        "path": "/img/admin/img1.jpg",
        "width": 100,
        "height": 100,
        "crop_style": "cover",
        "crop_arguments": {},
        "lazy": true
    }
}
```

This will produce a placeholder file adjacent to it with the extension
`.images.js`:

```js
/**
 * The output for this file is generated via the json file by the same name -
 * this file is just for type hints.
 */

/**
 * Maps from the image name to the image metadata. For each image,
 * contains the settings used to produce that image from the source
 * image as well as the outputs produced.
 *
 * @type {Object.<string, {target: {settings: {width: number, height: number, crop: 'cover', crop_settings: {pre_top_crop: number, pre_left_crop: number, pre_bottom_crop: number, pre_right_crop: number, crop_left_percentage: number, crop_top_percentage: number}}, outputs: Object.<string, Array.<{width: number, height: number, url: string, choice: string}>>}}>}
 */
export default {};
```

And will produce a corresponding output file which is functionally
identical to the following:

```js
export default {
    "img1": {
        "target": {
            "outputs": {
                "jpeg": [
                    {
                        "choice": "100",
                        "height": 20,
                        "url": "/img/test/1/20x20.jpeg",
                        "width": 20
                    },
                    {
                        "choice": "100",
                        "height": 30,
                        "url": "/img/test/1/30x30.jpeg",
                        "width": 30
                    }
                ],
                "webp": [
                    {
                        "choice": "lossless",
                        "height": 20,
                        "url": "/img/test/1/20x20.webp",
                        "width": 20
                    },
                    {
                        "choice": "lossless",
                        "height": 30,
                        "url": "/img/test/1/30x30.webp",
                        "width": 30
                    }
                ]
            },
            "settings": {
                "crop": "cover",
                "crop_settings": {
                    "crop_left_percentage": 0.5,
                    "crop_top_percentage": 0.5,
                    "pre_bottom_crop": 0,
                    "pre_left_crop": 0,
                    "pre_right_crop": 0,
                    "pre_top_crop": 0
                },
                "height": 20,
                "width": 20
            }
        }
    }
};
```

### Outlining js/css

Vanillaplusjs is expected to be run under the strictest content security policy,
and to facilitate this will automatically outline scripts and stylesheets into
their own separate files which are imported appropriately.

It's recommended that only test scripts or _very_ small script tags utilize
this, but it does avoid CSP issues causing code to work when running locally
that fails when deployed.

### Templates

Some parts of the HTML are quite repetitive. This library does not intend
to completely remove the boilerplate and does prefer clarity over brevity,
however, some amount of DRY is necessary to keep the code readable.
Extremely basic HTML templating is supported with constant variables.

The template file should go in the `partials` subdirectory of `src` folder
and works as follows:

src/public/index.html

```html
<!DOCTYPE html>
<html>
<head>
    <!--[TEMPLATE: ["/head/standard.html", {"title": "Try it Now"}]]-->
</head>
<body>
</body>
</html>
```

src/partials/head/standard.html

```html
<title><!--[STACK: ["retrieve", "title"]]--></title>
<meta charset="utf-8">
```

You can also use the stack to define local variables:

```html
<!--[STACK: ["define", "price", "$24.99"]]-->
<p>Get it today! Just <!--[STACK: ["retrieve", "price"]]--></p>
```

### Outlining Images

If images are specified in CSS files via data URIs, they will be outlined
in order to support the desired content security policy. This is particularly
useful when combined with external files, since e.g., bootstrap will inline
SVGs.

This a performance trade-off and can cause some flashing, but this project
prefers the security assurances of the CSP to the performance gains of inlined
scripts and images. Note that the browser could resolve this flashing in the
future by loading svgs referenced in stylesheets in the background after the
page has loaded.

### External files

If you have files that are required but should not be distributed via source
control then you can instruct vanillaplusjs to download them from a CDN prior to
building. For example, if you want to include bootstrap 5.2.0-beta1 in your project, you
would update the `external_files` section of `vanillaplusjs.json` as follows:

```json
{
    "external_files": {
        "src/public/css/lib/bootstrap.min.css": {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css",
            "integrity": "sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor"
        },
        "src/public/js/lib/bootstrap.min.js": {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js",
            "integrity": "sha384-pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2"
        }
    }
}
```

Note that to update dependencies you must do a cold build (`vanillaplusjs build`) as they will not
be updated during a hot build (`vanillaplusjs dev --watch`)

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

This functions identically for the meta property `og:url`

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

### Constants

Editable in the `vanillaplusjs.json` file, you can specify a file that acts as the
constants file. For example,

```json
{
    "js_constants": {
        "relpath": "src/public/js/constants.js",
        "shared": {},
        "dev": {"API_URL": "http://127.0.0.1:8080"},
        "prod": {"API_URL": ""},
    }
}
```

Then, if you create the file at the corresponding path, in this case,
`src/public/js/constants.js`, the contents of that file will be ignored and the
outputted file will depend on the build environment. In production mode,
`vanillaplusjs build`, the file at `out/www/js/constants.js` will be

```js
export const API_URL = "";
```

In development mode, `vanillaplusjs build --dev`, it will instead be

```js
export const API_URL = "http://127.0.0.1:8080";
```

This can be used, for example, to create an API wrapper:

```js
import { API_URL } from '/js/constants.js';


export function apiFetch(url, options) {
    if (url.startsWith('/')) {
        url = API_URL + url;
    }

    return fetch(url, options);
}
```

Which will allow you to run the backend server on a different port
locally, but in production mode, it will use the same port as the frontend.

## Contributing

This package uses `pre-commit` to install git commit hooks. Before
contributing, configure your virtual environment with the development
dependencies and initialize the pre-commit hooks:

```bash
python -m venv venv
"venv/bin/activate"
python -m pip install -U pip
pip install -r requirements.txt
pre-commit install
```

For windows

```bash
python -m venv venv
"venv/Scripts/Activate.bat"
python -m pip install -U pip
pip install -r requirements.txt
```

Then, in Git Bash for Windows,

```bash
"venv/Scripts/pre-commit.exe" install
```
