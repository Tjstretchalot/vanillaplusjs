from pathlib import Path
from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.build.file_signature import get_file_signature
from vanillaplusjs.constants import PROCESSOR_VERSION
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build


# We define these here to avoid breaking the indent flow too much while
# using the """ syntax.
BASIC = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --icon-size-medium: 1rem;
}

/*! PREPROCESSOR: icon x primary all-colors all-sizes */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --icon-size-medium: 1rem;
}}

.icon-x-medium-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

TWO_COLORS_AND_SIZES = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --col-primary-dark: #222;
    --icon-size-medium: 1rem;
    --icon-size-small: 0.75rem;
}

/*! PREPROCESSOR: icon x primary all-colors all-sizes */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --col-primary-dark: #222;
    --icon-size-medium: 1rem;
    --icon-size-small: 0.75rem;
}}

.icon-x-medium-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-primary-dark {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-dark.svg?v=Cg4WFkYCK65L468jk53Apom6bJb38JjMz5CIcJddaw0%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-small-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-small);
    height: var(--icon-size-small);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-small-primary-dark {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-small);
    height: var(--icon-size-small);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-dark.svg?v=Cg4WFkYCK65L468jk53Apom6bJb38JjMz5CIcJddaw0%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/primary-dark.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

SELECT_COLOR_AND_SIZE = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --col-primary-dark: #222;
    --icon-size-medium: 1rem;
    --icon-size-small: 0.75rem;
}

/*! PREPROCESSOR: icon x primary ["primary-dark"] ["small"] */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --col-primary-dark: #222;
    --icon-size-medium: 1rem;
    --icon-size-small: 0.75rem;
}}

.icon-x-small-primary-dark {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-small);
    height: var(--icon-size-small);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-dark.svg?v=Cg4WFkYCK65L468jk53Apom6bJb38JjMz5CIcJddaw0%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary-dark.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

BUTTON = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --col-primary-dark: #222;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}

/*! PREPROCESSOR: icon x primary all-colors all-sizes */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --col-primary-dark: #222;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}}

.icon-x-medium-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-primary-dark {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-dark.svg?v=Cg4WFkYCK65L468jk53Apom6bJb38JjMz5CIcJddaw0%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-disabled {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium {{
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    outline: none;
    padding: 0;
    margin: 0;
    text-align: center;
    display: inline-block;
    cursor: pointer;
}}

.icon-btn-x-medium:disabled {{
    cursor: not-allowed;
}}

.icon-btn-x-medium .icon-btn--icon {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium:hover .icon-btn--icon {{
    background-image: url("/img/icons/x/primary-dark.svg?v=Cg4WFkYCK65L468jk53Apom6bJb38JjMz5CIcJddaw0%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium:disabled .icon-btn--icon {{
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/primary-dark.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/disabled.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

SUPPRESS_BUTTON = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --col-primary-dark: #222;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}

/*! PREPROCESSOR: icon x primary all-colors all-sizes no-btn */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --col-primary-dark: #222;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}}

.icon-x-medium-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-primary-dark {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-dark.svg?v=Cg4WFkYCK65L468jk53Apom6bJb38JjMz5CIcJddaw0%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-disabled {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/primary-dark.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/disabled.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

OVERRIDE_BUTTON_STYLE = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --col-primary-light: #444;
    --col-secondary: #300;
    --col-secondary-light: #400;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}

/*! PREPROCESSOR: icon x primary all-colors all-sizes {"default":["primary", "primary-light", "disabled"], "secondary":["secondary", "secondary-light", "disabled"]} */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --col-primary-light: #444;
    --col-secondary: #300;
    --col-secondary-light: #400;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}}

.icon-x-medium-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-primary-light {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-light.svg?v=UUzI0Z-KWKQXrHUPFSuQGKsGNRHEXRZW66aLQ7P9UZM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-secondary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/secondary.svg?v=iWfUoQRoMb3rnbgM71pmzdj-g0yc0peQ6hRKz9HhcTo%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-secondary-light {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/secondary-light.svg?v=ljIop1nCxvZj_DNkAgr7DLyOIcA9u9gUNQzbLntyai8%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-disabled {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium {{
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    outline: none;
    padding: 0;
    margin: 0;
    text-align: center;
    display: inline-block;
    cursor: pointer;
}}

.icon-btn-x-medium:disabled {{
    cursor: not-allowed;
}}

.icon-btn-x-medium .icon-btn--icon {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium:hover .icon-btn--icon {{
    background-image: url("/img/icons/x/primary-light.svg?v=UUzI0Z-KWKQXrHUPFSuQGKsGNRHEXRZW66aLQ7P9UZM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium:disabled .icon-btn--icon {{
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium-secondary {{
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    outline: none;
    padding: 0;
    margin: 0;
    text-align: center;
    display: inline-block;
    cursor: pointer;
}}

.icon-btn-x-medium-secondary:disabled {{
    cursor: not-allowed;
}}

.icon-btn-x-medium-secondary .icon-btn--icon {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/secondary.svg?v=iWfUoQRoMb3rnbgM71pmzdj-g0yc0peQ6hRKz9HhcTo%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium-secondary:hover .icon-btn--icon {{
    background-image: url("/img/icons/x/secondary-light.svg?v=ljIop1nCxvZj_DNkAgr7DLyOIcA9u9gUNQzbLntyai8%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium-secondary:disabled .icon-btn--icon {{
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/primary-light.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#444444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#444444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/secondary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#330000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#330000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/secondary-light.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#440000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#440000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/disabled.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

OVERRIDE_BUTTON_STYLE_MULTILINE_COMMENT = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --col-primary-light: #444;
    --col-secondary: #300;
    --col-secondary-light: #400;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}

/*!
PREPROCESSOR: icon x primary all-colors all-sizes
{
    // a comment within a comment!
    "default": ["primary", "primary-light", "disabled"],
    "secondary": ["secondary", "secondary-light", "disabled"]
}
*/
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
    "conv": {
        "out/www/css/main.css": """
:root {{
    --col-primary: #333;
    --col-primary-light: #444;
    --col-secondary: #300;
    --col-secondary-light: #400;
    --col-disabled: #C0C0C0;
    --icon-size-medium: 1rem;
}}

.icon-x-medium-primary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-primary-light {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary-light.svg?v=UUzI0Z-KWKQXrHUPFSuQGKsGNRHEXRZW66aLQ7P9UZM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-secondary {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/secondary.svg?v=iWfUoQRoMb3rnbgM71pmzdj-g0yc0peQ6hRKz9HhcTo%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-secondary-light {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/secondary-light.svg?v=ljIop1nCxvZj_DNkAgr7DLyOIcA9u9gUNQzbLntyai8%3D&pv={PROCESSOR_VERSION}");
}}

.icon-x-medium-disabled {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium {{
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    outline: none;
    padding: 0;
    margin: 0;
    text-align: center;
    display: inline-block;
    cursor: pointer;
}}

.icon-btn-x-medium:disabled {{
    cursor: not-allowed;
}}

.icon-btn-x-medium .icon-btn--icon {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/primary.svg?v=1mLZgdi1Qr7sv3OetXHemdOaaYFnLY_tJ4am5r0h_AM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium:hover .icon-btn--icon {{
    background-image: url("/img/icons/x/primary-light.svg?v=UUzI0Z-KWKQXrHUPFSuQGKsGNRHEXRZW66aLQ7P9UZM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium:disabled .icon-btn--icon {{
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium-secondary {{
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    outline: none;
    padding: 0;
    margin: 0;
    text-align: center;
    display: inline-block;
    cursor: pointer;
}}

.icon-btn-x-medium-secondary:disabled {{
    cursor: not-allowed;
}}

.icon-btn-x-medium-secondary .icon-btn--icon {{
    background: no-repeat center center;
    display: inline-block;
    vertical-align: middle;
    content: "";
    width: var(--icon-size-medium);
    height: var(--icon-size-medium);
    background-size: 100% 100%;
    background-image: url("/img/icons/x/secondary.svg?v=iWfUoQRoMb3rnbgM71pmzdj-g0yc0peQ6hRKz9HhcTo%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium-secondary:hover .icon-btn--icon {{
    background-image: url("/img/icons/x/secondary-light.svg?v=ljIop1nCxvZj_DNkAgr7DLyOIcA9u9gUNQzbLntyai8%3D&pv={PROCESSOR_VERSION}");
}}

.icon-btn-x-medium-secondary:disabled .icon-btn--icon {{
    background-image: url("/img/icons/x/disabled.svg?v=Y--GuRSWuXkdzeQo4_WuA1pZIzUz5hsnX2bS2OrFzBM%3D&pv={PROCESSOR_VERSION}");
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/img/icons/x/primary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/primary-light.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#444444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#444444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/secondary.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#330000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#330000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/secondary-light.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#440000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#440000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        "out/www/img/icons/x/disabled.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#C0C0C0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    },
}

CHANGE_MAIN_CSS_REBUILDS = {
    "orig": {
        "src/public/css/main.css": """
:root {
    --col-primary: #333;
    --icon-size-medium: 1rem;
}
""",
        "src/public/css/icons.css": """
/*! PREPROCESSOR: icon x primary all-colors all-sizes */
""",
        "src/public/img/icons/x.svg": """
<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 2.38721L9.5 9.88721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 9.88721L9.5 2.38721" stroke="#333333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    }
}


class Test(unittest.TestCase):
    def _basic_test(self, orig: Dict[str, str], conv: Dict[str, str]):
        self.maxDiff = None
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            for path, val in orig.items():
                os.makedirs(os.path.dirname(os.path.join("tmp", path)), exist_ok=True)
                with open(os.path.join("tmp", path), "w") as f:
                    f.write(val)

            vanillaplusjs.runners.build.main(["--folder", "tmp"])

            for path, val in conv.items():
                with open(os.path.join("tmp", path), "r") as f:
                    self.assertEqual(f.read(), val, path)
        finally:
            shutil.rmtree("tmp")

    def test_basic(self):
        self._basic_test(BASIC["orig"], BASIC["conv"])

    def test_two_colors_and_sizes(self):
        self._basic_test(TWO_COLORS_AND_SIZES["orig"], TWO_COLORS_AND_SIZES["conv"])

    def test_select_color_and_size(self):
        self._basic_test(SELECT_COLOR_AND_SIZE["orig"], SELECT_COLOR_AND_SIZE["conv"])

    def test_button(self):
        self._basic_test(BUTTON["orig"], BUTTON["conv"])

    def test_suppress_button(self):
        self._basic_test(SUPPRESS_BUTTON["orig"], SUPPRESS_BUTTON["conv"])

    def test_override_button_style(self):
        self._basic_test(OVERRIDE_BUTTON_STYLE["orig"], OVERRIDE_BUTTON_STYLE["conv"])

    def test_override_button_style_multiline_comment(self):
        self._basic_test(
            OVERRIDE_BUTTON_STYLE_MULTILINE_COMMENT["orig"],
            OVERRIDE_BUTTON_STYLE_MULTILINE_COMMENT["conv"],
        )

    def test_change_main_css_rebuilds(self):
        orig = CHANGE_MAIN_CSS_REBUILDS["orig"]
        self.maxDiff = None
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            for path, val in orig.items():
                os.makedirs(os.path.dirname(os.path.join("tmp", path)), exist_ok=True)
                with open(os.path.join("tmp", path), "w") as f:
                    f.write(val)

            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            old_signature = get_file_signature(
                os.path.join("tmp", "out", "www", "css", "icons.css")
            )
            Path(os.path.join("tmp", "src", "public", "css", "main.css")).touch()
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            new_signature = get_file_signature(
                os.path.join("tmp", "out", "www", "css", "icons.css")
            )
            self.assertNotEqual(old_signature, new_signature)
        finally:
            shutil.rmtree("tmp")
