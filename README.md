# news-image-20261123
[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/mooohgaming/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/mooohgaming/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

`main.py` draws one newspaper page — "The World in One Page" — summing up
Monday 23 November 2026 in a single 1024x1024 PNG. Six stories, each with a
headline, two lines of text, a drawn illustration and a source line:

1. **COP31 ends with no deal** — nearly 200 nations leave Antalya without a
   climate pact after talks collapse over fossil fuels. (CNN)
2. **Democrats win 258 House seats** — AP calls a historic majority, the
   largest for either party since 1992. (Associated Press)
3. **Ukraine sinks Russian warship off Libya** — seven naval drones sink the
   corvette Merkury in Benghazi; a cargo ship and a helicopter are also hit.
   (Reuters)
4. **24 dead in Indonesia factory fire** — a blaze at a candy factory in
   Banten leaves about 30 people unaccounted for. (Xinhua)
5. **Liverpool thrash Man Utd 4-0** — Pochettino's first match as United
   boss ends in a rout at Anfield; Yoro sent off after 8 minutes. (Reuters)
6. **Iran says it downed a US drone** — Tehran says it shot down a US MQ-9
   Reaper over the Strait of Hormuz. (Inshorts)

The program uses only the Python standard library: it draws the page with its
own canvas code and a built-in 5x7 bitmap font, and encodes the PNG by hand
(zlib + struct). No network, no clock, no randomness — two runs produce
byte-identical output.

## Run it

```sh
python3 main.py
```

That writes `/output/entry.png`. To write elsewhere, set
`MAKEFUN_OUTPUT_DIR`:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
