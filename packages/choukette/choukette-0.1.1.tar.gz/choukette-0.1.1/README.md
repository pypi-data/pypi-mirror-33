# Choukette

[![build status](https://gitlab.com/choukette/choukette/badges/master/build.svg)](https://gitlab.com/choukette/choukette/commits/master)
[![coverage](https://gitlab.com/choukette/choukette/badges/master/coverage.svg?job=coverage)](https://choukette.gitlab.io/choukette/coverage)
[![PyPI version](https://badge.fury.io/py/choukette.svg)](https://badge.fury.io/py/choukette)

A simple way to create badges.

Need more info, look at the homepage documentation. [choukette.gitlab.io](http://choukette.gitlab.io/)

## Install

```
pip install choukette
```

## Quickstart

```
choukette <text> <value> <color>
```

## Examples

```
choukette coverage 90% 4c1
```

<svg xmlns="http://www.w3.org/2000/svg" width="116" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>

  <mask id="a">
    <rect width="116" height="20" rx="3" fill="#fff"/>
  </mask>

  <g mask="url(#a)">
    <path fill="#555"
          d="M0 0 h62 v20 H0 z"/>
    <path fill="#4c1"
          d="M62 0 h54 v20 H62 z"/>
    <path fill="url(#b)"
          d="M0 0 h116 v20 H0 z"/>
  </g>

  <g fill="#fff" text-anchor="middle">
    <g font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
      <text x="31" y="15" fill="#010101" fill-opacity=".3">
        coverage
      </text>
      <text x="31" y="14">
        coverage
      </text>
      <text x="89" y="15" fill="#010101" fill-opacity=".3">
        90%
      </text>
      <text x="89" y="14">
        90%
      </text>
    </g>
  </g>
</svg>

```
choukette build failing e05d44
```

<svg xmlns="http://www.w3.org/2000/svg" width="116" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>

  <mask id="a">
    <rect width="116" height="20" rx="3" fill="#fff"/>
  </mask>

  <g mask="url(#a)">
    <path fill="#555"
          d="M0 0 h62 v20 H0 z"/>
    <path fill="#e05d44"
          d="M62 0 h54 v20 H62 z"/>
    <path fill="url(#b)"
          d="M0 0 h116 v20 H0 z"/>
  </g>

  <g fill="#fff" text-anchor="middle">
    <g font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
      <text x="31" y="15" fill="#010101" fill-opacity=".3">
        build
      </text>
      <text x="31" y="14">
        build
      </text>
      <text x="89" y="15" fill="#010101" fill-opacity=".3">
        failing
      </text>
      <text x="89" y="14">
        failing
      </text>
    </g>
  </g>
</svg>

```
choukette version 1.0.2 007ec6
```

<svg xmlns="http://www.w3.org/2000/svg" width="116" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>

  <mask id="a">
    <rect width="116" height="20" rx="3" fill="#fff"/>
  </mask>

  <g mask="url(#a)">
    <path fill="#555"
          d="M0 0 h62 v20 H0 z"/>
    <path fill="#007ec6"
          d="M62 0 h54 v20 H62 z"/>
    <path fill="url(#b)"
          d="M0 0 h116 v20 H0 z"/>
  </g>

  <g fill="#fff" text-anchor="middle">
    <g font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
      <text x="31" y="15" fill="#010101" fill-opacity=".3">
        version
      </text>
      <text x="31" y="14">
        version
      </text>
      <text x="89" y="15" fill="#010101" fill-opacity=".3">
        1.0.2
      </text>
      <text x="89" y="14">
        1.0.2
      </text>
    </g>
  </g>
</svg>