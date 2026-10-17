# Optional asset scope

This OpenAR package omits assets/ to stay within the 2 MiB Hub limit. The core plotting templates, Python/R guidance, numerical checks, panel-alignment checks, PDF text audit and collision audit remain included and do not require those assets.

For an optional gallery preview, inspect the [pinned Nature Skills source](https://github.com/Yuan1z0825/nature-skills/tree/28150f30f8b4017991fca8c7b2839f02c6586d2f/skills/nature-figure/assets). If the user needs those examples locally, use a separate workspace checkout at that exact revision and resolve asset paths relative to its skills/nature-figure directory. Keep the installed package unchanged.

The figures4papers code and images are external references. Their upstream notice states that no explicit license was found; the Nature Skills root license does not grant reuse rights for them. Consult the [original rights notice](https://github.com/Yuan1z0825/nature-skills/blob/28150f30f8b4017991fca8c7b2839f02c6586d2f/skills/nature-figure/assets/figures4papers/THIRD_PARTY_NOTICES.md) before reuse. When reuse rights are unavailable, implement an original plot from the user's data using the included scripts and references.
